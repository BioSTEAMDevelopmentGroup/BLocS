"""
Created on Sun Oct  4 12:18:15 2020

@author: yrc2. Modified by Dalton Stewart.
"""
import os
import pandas as pd
import numpy as np
from biorefineries import corn as cn
from biorefineries import sugarcane as sc
from biorefineries import cornstover as cs
import blocs as blc
import biosteam as bst
    
__all__ = (
    'create_corn_tea',
    'create_sugarcane_tea',
    'create_cornstover_tea',
    'ConventionalIncentivesTEA',
    'CellulosicIncentivesTEA',
)

def create_corn_tea():
    tea = cn.create_tea(cn.corn_sys, cls=ConventionalIncentivesTEA)
    tea.incentive_numbers = () # Empty for now
    tea.fuel_tax = 0.
    tea.sales_tax = 0.
    tea.federal_income_tax = 0.35
    tea.state_income_tax = 0.065
    tea.property_tax = 0.013
    tea.utility_tax = 0.
    tea.ethanol_product = cn.ethanol
    tea.ethanol_group = bst.UnitGroup('Ethanol group', cn.corn_sys.units) # Assume all unit operations qualify
    tea.feedstock = cn.corn
    return tea

def create_sugarcane_tea():
    tea = sc.create_tea(sc.sugarcane_sys, cls=ConventionalIncentivesTEA)
    tea.incentive_numbers = () # Empty for now
    tea.fuel_tax = 0.
    tea.sales_tax = 0.
    tea.federal_income_tax = 0.35
    tea.state_income_tax = 0.065
    tea.property_tax = 0.013
    tea.utility_tax = 0.
    tea.ethanol_product = sc.ethanol
    tea.ethanol_group = bst.UnitGroup('Ethanol group', sc.sugarcane_sys.units) # Assume all unit operations qualify
    tea.BT = sc.BT
    tea.feedstock = sc.sugarcane
    tea.property_tax = 0.001
    return tea

def create_cornstover_tea():
    tea = cs.create_tea(cs.cornstover_sys, cls=CellulosicIncentivesTEA)
    tea.incentive_numbers = () # Empty for now
    tea.fuel_tax = 0.
    tea.sales_tax = 0.
    tea.federal_income_tax = 0.35
    tea.state_income_tax = 0.065
    tea.property_tax = 0.013
    tea.utility_tax = 0.
    tea.ethanol_product = cs.ethanol
    tea.ethanol_group = bst.UnitGroup('Ethanol group', cs.cornstover_sys.units) # Assume all unit operations qualify
    tea.BT = cs.BT
    tea.feedstock = cs.cornstover
    tea.property_tax = 0.001
    return tea
    

class CellulosicIncentivesTEA(cs.CellulosicEthanolTEA):
    
    def __init__(self, *args, incentive_numbers=(), 
                 property_tax=None,
                 state_income_tax=None,
                 federal_income_tax=None,
                 ethanol_product=None, 
                 biodiesel_product=None,
                 ethanol_group=None, 
                 biodiesel_group=None,
                 sales_tax=None,
                 fuel_tax=None,
                 utility_tax=None,
                 BT=None,
                 feedstock=None,
                 F_investment=1.,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.property_tax = property_tax
        self.state_income_tax = state_income_tax
        self.federal_income_tax = federal_income_tax
        self.incentive_numbers = incentive_numbers
        self.ethanol_product = ethanol_product
        self.biodiesel_product = biodiesel_product
        self.ethanol_group = ethanol_group
        self.biodiesel_group = biodiesel_group
        self.sales_tax = sales_tax
        self.fuel_tax = fuel_tax
        self.feedstock = feedstock
        self.utility_tax = utility_tax
        self.F_investment = F_investment
        self.BT = BT
    
    def depreciation_incentive_24(self, switch):
        if switch:
            self._depreciation_array = inc24 = self.depreciation_schedules[self.depreciation].copy()
            inc24[0] += 0.5
            inc24[1:] = inc24[1:] / (inc24[1:].sum() / (1 - inc24[0]))
            np.testing.assert_allclose(inc24.sum(), 1.) 
        else:
            self._depreciation_array = self.depreciation_schedules[self.depreciation]
        
    def _FCI(self, TDC):
        self._FCI_cached = FCI = self.F_investment * super()._FCI(TDC)
        return FCI
    
    def _fill_tax_and_incentives(self, incentives, taxable_cashflow, nontaxable_cashflow, tax):
        taxable_cashflow[taxable_cashflow < 0.] = 0.
        lang_factor = self.lang_factor
        if lang_factor:
            converyor_costs = lang_factor * sum([i.purchase_cost for i in self.units if isinstance(i, bst.ConveyingBelt)])
        else:
            converyor_costs = sum([i.installed_cost for i in self.units if isinstance(i, bst.ConveyingBelt)])
        operating_hours = self.operating_hours
        ethanol_product = self.ethanol_product
        biodiesel_product = self.biodiesel_product
        biodiesel_group = self.biodiesel_group
        ethanol_group = self.ethanol_group
        BT = self.BT
        fuel_value = 0.
        if ethanol_product:
            # Ethanol in gal/yr
            ethanol = 2.98668849 * ethanol_product.F_mass * operating_hours  
            fuel_value += ethanol_product.cost * operating_hours
            if lang_factor:
                ethanol_eq = 1e6 * lang_factor * ethanol_group.get_purchase_cost()
            else:
                ethanol_eq = 1e6 * ethanol_group.get_installed_cost()
        else:
            ethanol = ethanol_eq = ethanol_sales = 0.
        if biodiesel_product: 
            fuel_value += biodiesel_product.cost * operating_hours
            if lang_factor:
                biodiesel_eq = 1e6 * lang_factor * biodiesel_group.get_purchase_cost() 
            else:
                biodiesel_eq = 1e6 * biodiesel_group.get_installed_cost() 
        else:
            biodiesel_eq = 0.
        feedstock = self.feedstock
        feedstock_value = feedstock.cost * operating_hours
        if lang_factor:
            elec_eq = lang_factor * BT.purchase_cost if BT else 0.
        else:
            elec_eq = BT.installed_cost if BT else 0.
        TCI = self.TCI
        wages = self.labor_cost
        FCI = self.FCI
        startup_VOCfrac = self.startup_VOCfrac
        startup_FOCfrac = self.startup_FOCfrac
        construction_schedule = self._construction_schedule
        taxable_property = FCI
        start = self._start
        years = self._years
        w0 = self._startup_time
        w1 = 1. - w0
        plant_years = start + years
        empty_cashflows = np.zeros(plant_years)        
        
        def yearly_flows(x, startup_frac):
            y = empty_cashflows.copy()
            y[start] = w0 * startup_frac * x + w1 * x
            y[start + 1:] = x
            return y
        
        def construction_flow(x):
            y = empty_cashflows.copy()
            y[:start] = x * construction_schedule
            return y
        
        wages_arr = yearly_flows(wages, startup_FOCfrac)
        fuel_value_arr = yearly_flows(fuel_value, startup_VOCfrac)
        feedstock_value_arr = yearly_flows(feedstock_value, startup_VOCfrac)
        ethanol_arr = yearly_flows(ethanol, startup_VOCfrac)
        taxable_property_arr = construction_flow(taxable_property).cumsum()
        elec_eq_arr = construction_flow(elec_eq).cumsum()
        biodiesel_eq_arr = construction_flow(biodiesel_eq).cumsum()
        ethanol_eq_arr = construction_flow(ethanol_eq).cumsum()
        converyor_cost_arr = construction_flow(converyor_costs).cumsum()
        property_tax_arr = yearly_flows(FCI * self.property_tax, startup_FOCfrac)
        fuel_tax_arr = self.fuel_tax * fuel_value_arr
        sales_tax = self.sales_tax
        purchase_cost_arr = construction_flow(self.purchase_cost)
        sales_arr = purchase_cost_arr + feedstock_value_arr
        sales_tax_arr = None if sales_tax is None else sales_arr * sales_tax
        #here i took the absolute value of utility cost bc it will likely always be negative
        util_cost_arr = yearly_flows(abs(self.utility_cost), startup_FOCfrac)
        util_tax_arr = self.utility_tax * util_cost_arr
        
        exemptions, deductions, credits, refunds = blc.determine_tax_incentives(
            self.incentive_numbers,
            start=self._start,
            plant_years=self._years + self._start,
            value_added=FCI,
            property_taxable_value=taxable_property_arr,
            property_tax_rate=self.property_tax,
            biodiesel_eq=biodiesel_eq_arr, 
            ethanol_eq=ethanol_eq_arr,
            fuel_taxable_value=fuel_value_arr,
            fuel_tax_rate=self.fuel_tax,
            sales_taxable_value=sales_arr, # Regards equipment cost with building materials (foundation, pipping, etc.), installation fees, and biomass flow rate
            sales_tax_rate=self.sales_tax,
            sales_tax_assessed=sales_tax_arr,
            wages=wages_arr,
            TCI=TCI,
            ethanol=ethanol_arr,
            fed_income_tax_assessed=taxable_cashflow * self.federal_income_tax,
            elec_eq=elec_eq_arr,
            jobs_50=50, # Assumption made by the original lipid-cane biorefinery publication 
            utility_tax_assessed=util_tax_arr,
            state_income_tax_assessed=taxable_cashflow * self.state_income_tax,
            property_tax_assessed=property_tax_arr,
            IA_value=converyor_cost_arr, 
            building_mats=purchase_cost_arr,
            NM_value=elec_eq + feedstock_value_arr,
        )
        self.exemptions = exemptions
        self.deductions = deductions
        self.credits = credits
        self.refunds = refunds
        index = taxable_cashflow > 0.
        #i included utility tax here
        tax[:] = property_tax_arr + fuel_tax_arr + util_tax_arr
        tax[index] += (self.federal_income_tax + self.state_income_tax) * taxable_cashflow[index] 
        maximum_incentives = credits + refunds + deductions + exemptions
        index = maximum_incentives > tax
        maximum_incentives[index] = tax[index]
        incentives[:] = maximum_incentives

class ConventionalIncentivesTEA(sc.ConventionalEthanolTEA):
    
    def __init__(self, *args, incentive_numbers=(), 
                 state_income_tax=None,
                 federal_income_tax=None,
                 ethanol_product=None, 
                 biodiesel_product=None,
                 ethanol_group=None, 
                 biodiesel_group=None,
                 sales_tax=None,
                 fuel_tax=None,
                 utility_tax=None,
                 BT=None,
                 feedstock=None,
                 F_investment=1.,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.state_income_tax = state_income_tax
        self.federal_income_tax = federal_income_tax
        self.incentive_numbers = incentive_numbers
        self.ethanol_product = ethanol_product
        self.biodiesel_product = biodiesel_product
        self.ethanol_group = ethanol_group
        self.biodiesel_group = biodiesel_group
        self.sales_tax = sales_tax
        self.fuel_tax = fuel_tax
        self.feedstock = feedstock
        self.utility_tax = utility_tax
        self.F_investment = F_investment
        self.BT = BT
        self.lang_factor = 3
        
    depreciation_incentive_24 = CellulosicIncentivesTEA.depreciation_incentive_24
    _fill_tax_and_incentives = CellulosicIncentivesTEA._fill_tax_and_incentives
    
    def _FCI(self, TDC):
        self._FCI_cached = FCI = self.F_investment * super()._FCI(TDC)
        return FCI
    
    def _FOC(self, FCI):
        return (FCI*(self.property_insurance + self.maintenance + self.administration)
                + self.labor_cost*(1+self.fringe_benefits+self.supplies))
    