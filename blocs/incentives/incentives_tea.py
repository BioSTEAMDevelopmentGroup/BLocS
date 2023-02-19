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
cs._include_blowdown_recycle = False
cs.load()

#Import state scenario data
folder = os.path.dirname(__file__)
st_data_file = os.path.join(folder, 'state_scenarios_for_import.xlsx')
state_data = pd.read_excel(st_data_file, index_col=[0])
#%%
__all__ = (
    'create_corn_tea',
    'create_sugarcane_tea',
    'create_cornstover_tea',
    'create_incentivized_tea',
    'ConventionalIncentivesTEA',
    'CellulosicIncentivesTEA',
    'CellulosicBLocSTEA',
    'ConventionalBLocSTEA',
)

def create_corn_tea():
    tea = cn.create_tea(cn.corn_sys, cls=ConventionalIncentivesTEA)
    # TODO: Update according to biorefinery specific TEA
    tea.incentive_numbers = () # Empty for now
    tea.fuel_tax = 0.
    tea.sales_tax = 0.
    tea.federal_income_tax = 0.21
    tea.state_income_tax = 0.065
    tea.property_tax = 0.013
    tea.utility_tax = 0.
    tea.ethanol_product = cn.ethanol
    tea.ethanol_group = bst.UnitGroup('Ethanol group', cn.corn_sys.units) # Assume all unit operations qualify
    tea.feedstock = cn.corn
    tea.DDGS = cn.DDGS
    tea.DDGS.price = 0.13709
    tea.V405 = cn.V405
    tea.crude_oil = cn.crude_oil
    tea.crude_oil.price = 0.64
    tea.sulfuric_acid = cn.sulfuric_acid
    tea.sulfuric_acid.price = 0.1070
    tea.lime = cn.lime
    tea.lime.price = 0.2958
    tea.alpha_amylase = cn.alpha_amylase
    tea.alpha_amylase.price = 2.56
    tea.gluco_amylase = cn.gluco_amylase
    tea.gluco_amylase.price = 2.56
    tea.ammonia = cn.ammonia
    tea.ammonia.price = 0.4727
    tea.denaturant = cn.denaturant
    tea.denaturant.price = 0.496
    tea.steam = cn.steam
    tea.steam.price = 0.01466
    tea.yeast = cn.yeast
    tea.yeast.price = 2.12
    return tea

def create_sugarcane_tea():
    tea = sc.create_tea(sc.sugarcane_sys, cls=ConventionalIncentivesTEA)
    # TODO: Update according to biorefinery specific TEA
    tea.incentive_numbers = () # Empty for now
    tea.fuel_tax = 0.
    tea.sales_tax = 0.
    tea.federal_income_tax = 0.21
    tea.state_income_tax = 0.065
    tea.property_tax = 0.013
    tea.utility_tax = 0.
    tea.ethanol_product = sc.ethanol
    tea.ethanol_group = bst.UnitGroup('Ethanol group', sc.sugarcane_sys.units) # Assume all unit operations qualify
    tea.BT = sc.BT
    tea.feedstock = sc.sugarcane
    tea.vinasse = sc.vinasse
    tea.R301 = sc.R301
    tea.property_tax = 0.001
    tea.lime = sc.lime
    tea.lime.price = 0.2958
    tea.denaturant = sc.denaturant
    tea.denaturant.price = 0.496
    tea.cooling_tower_chemicals = sc.cooling_tower_chemicals
    tea.cooling_tower_chemicals.price = 4.4385
    tea.makeup_water = sc.makeup_water
    tea.makeup_water.price = 0.0005
    return tea

def create_cornstover_tea():    
    tea = cs.create_tea(cs.cornstover_sys, cls=CellulosicIncentivesTEA)
    tea.incentive_numbers = () # Empty for now
    tea.fuel_tax = 0.
    tea.sales_tax = 0.
    tea.federal_income_tax = 0.21
    tea.state_income_tax = 0.065
    tea.property_tax = 0.013
    tea.utility_tax = 0.
    tea.ethanol_product = cs.ethanol
    tea.ethanol_group = bst.UnitGroup('Ethanol group', cs.cornstover_sys.units) # Assume all unit operations qualify
    tea.BT = cs.BT
    tea.feedstock = cs.cornstover
    tea.cellulase = cs.cellulase
    tea.cellulase.price = 0.258
    tea.R201 = cs.R201
    tea.R303 = cs.R303
    tea.property_tax = 0.001
    tea.sulfuric_acid = cs.sulfuric_acid
    tea.sulfuric_acid.price = 0.1070
    tea.FGD_lime = cs.FGD_lime
    tea.FGD_lime.price = 0.2958
    tea.denaturant = cs.denaturant
    tea.denaturant.price = 0.496
    tea.cooling_tower_chemicals = cs.cooling_tower_chemicals
    tea.cooling_tower_chemicals.price = 4.4385
    tea.makeup_water = cs.makeup_water
    tea.makeup_water.price = 0.0005
    tea.CSL = cs.CSL
    tea.CSL.price = 0.0843
    tea.DAP = cs.DAP
    tea.DAP.price = 0.4092
    tea.ammonia = cs.ammonia
    tea.ammonia.price = 0.4727
    tea.boiler_chemicals = cs.boiler_chemicals
    tea.boiler_chemicals.price = 7.4062
    tea.caustic = cs.caustic
    tea.caustic.price = 0.5931
    return tea

# cellulosic: BT, feedstock, ethanol_product,

def create_incentivized_tea(
        system, isconventional, cogeneration_unit, feedstock,
        ethanol_product, state=None, **kwargs,
    ):
    TEA = ConventionalIncentivesTEA if isconventional else CellulosicIncentivesTEA
    tea = TEA(system, income_tax=None, **kwargs)
    tea.BT = cogeneration_unit
    tea.feedstock = feedstock
    tea.ethanol_product = ethanol_product
    tea.utility_tax = 0.
    if ethanol_product:
        tea.ethanol_group = bst.UnitGroup('Ethanol group', system.units)
    else:
        tea.ethanol_group = bst.UnitGroup('Ethanol group', ())
    folder = os.path.dirname(__file__)
    st_data_file = os.path.join(folder, 'state_scenarios_for_import.xlsx')
    st_data = pd.read_excel(st_data_file, index_col=[0])
    if state:
        tea.state_income_tax = st_data.loc[state]['Income Tax Rate (decimal)']
        tea.property_tax = st_data.loc[state]['Property Tax Rate (decimal)']
        tea.fuel_tax = st_data.loc[state]['State Motor Fuel Tax (decimal)']
        tea.sales_tax = st_data.loc[state]['State Sales Tax Rate (decimal)']
        bst.PowerUtility.price = st_data.loc[state]['Electricity Price (USD/kWh)']
        tea.F_investment = st_data.loc[state]['Location Capital Cost Factor (dimensionless)']
        if feedstock.ID == 'corn':
            name = 'CN'
        elif feedstock.ID == 'sugarcane':
            name = 'SC'
        elif feedstock.ID == 'cornstover':
            name = 'CS'
        tea.feedstock.price = st_data.loc[state][f'{name} Price (USD/kg)']
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
        self.jobs_50 = 50
        self.deduct_federal_income_tax_to_state_taxable_earnings = False
        self.deduct_half_federal_income_tax_to_state_taxable_earnings = False
        self.state_tax_by_gross_receipts = False
        self.labor_cost *= (26.03/19.55) # BLS labor indices for years 2020/2007

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

    def _fill_tax_and_incentives(self, incentives, taxable_cashflow, nontaxable_cashflow, tax, depreciation):
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
        taxable_property_arr = (construction_flow(taxable_property) - depreciation).cumsum()
        elec_eq_arr = construction_flow(elec_eq).cumsum()
        biodiesel_eq_arr = construction_flow(biodiesel_eq).cumsum()
        ethanol_eq_arr = construction_flow(ethanol_eq).cumsum()
        converyor_cost_arr = construction_flow(converyor_costs).cumsum()
        property_tax_arr = taxable_property_arr * self.property_tax
        fuel_tax_arr = self.fuel_tax * fuel_value_arr
        sales_tax = self.sales_tax
        purchase_cost_arr = construction_flow(self.purchase_cost)
        sales_arr = purchase_cost_arr + feedstock_value_arr
        sales_tax_arr = None if sales_tax is None else sales_arr * sales_tax
        util_cost_arr = yearly_flows(abs(self.utility_cost), startup_FOCfrac) # absolute value of utility cost bc it will likely always be negative
        util_tax_arr = self.utility_tax * util_cost_arr
        federal_assessed_income_tax = taxable_cashflow * self.federal_income_tax
        if self.deduct_federal_income_tax_to_state_taxable_earnings:
            state_assessed_income_tax = (taxable_cashflow - federal_assessed_income_tax) * self.state_income_tax
        else:
            state_assessed_income_tax = taxable_cashflow * self.state_income_tax
        if self.deduct_half_federal_income_tax_to_state_taxable_earnings:
            state_assessed_income_tax = (taxable_cashflow - (0.5*federal_assessed_income_tax)) * self.state_income_tax
        else:
            state_assessed_income_tax = taxable_cashflow * self.state_income_tax
        if self.state_tax_by_gross_receipts:
            revenue_arr = yearly_flows(self.sales, startup_VOCfrac)
            state_assessed_income_tax = revenue_arr * self.state_income_tax
        else:
            state_assessed_income_tax = taxable_cashflow * self.state_income_tax
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
            fed_income_tax_assessed=federal_assessed_income_tax,
            elec_eq=elec_eq_arr,
            jobs_50=self.jobs_50, # Assumption made by the original lipid-cane biorefinery publication
            utility_tax_assessed=util_tax_arr,
            state_income_tax_assessed=state_assessed_income_tax,
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
        tax[:] = property_tax_arr + fuel_tax_arr + sales_tax_arr # util_tax_arr; utility tax not currently considered
        tax[index] += federal_assessed_income_tax[index]
        if self.state_tax_by_gross_receipts:
            tax[:] += state_assessed_income_tax
        else:
            tax[index] += state_assessed_income_tax[index]
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
        self.TDC_over_FCI = 0.625
        self.jobs_50 = 50
        self.deduct_federal_income_tax_to_state_taxable_earnings = False
        self.deduct_half_federal_income_tax_to_state_taxable_earnings = False
        self.state_tax_by_gross_receipts = False
        self.labor_cost *= (26.03/21.40) # BLS labor indices for years 2020/2013

    depreciation_incentive_24 = CellulosicIncentivesTEA.depreciation_incentive_24
    _fill_tax_and_incentives = CellulosicIncentivesTEA._fill_tax_and_incentives

    def _fill_depreciation_array(self, depreciation, start, years, FCI):
        TDC = self.TDC_over_FCI * FCI
        return super()._fill_depreciation_array( depreciation, start, years, TDC)

    def _DPI(self, installed_equipment_cost):
        return self.F_investment * installed_equipment_cost

    def _FOC(self, FCI):
        return (FCI*(self.property_insurance + self.maintenance + self.administration)
                + self.labor_cost*(1+self.fringe_benefits+self.supplies))

class CellulosicBLocSTEA(cs.CellulosicEthanolTEA):
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
                 location=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._property_tax = property_tax
        self._state_income_tax = state_income_tax
        self.federal_income_tax = federal_income_tax
        self._incentive_numbers = incentive_numbers
        self.ethanol_product = ethanol_product
        self.biodiesel_product = biodiesel_product
        self.ethanol_group = ethanol_group
        self.biodiesel_group = biodiesel_group
        self._sales_tax = sales_tax
        self._fuel_tax = fuel_tax
        self.feedstock = feedstock
        self.utility_tax = utility_tax
        self._F_investment = F_investment
        self.BT = BT
        self.jobs_50 = 50
        self.location = location
        self.deduct_federal_income_tax_to_state_taxable_earnings = False
        self.deduct_half_federal_income_tax_to_state_taxable_earnings = False
        self.state_tax_by_gross_receipts = False
        self.labor_cost *= (26.03/19.55) # BLS labor cost indices for years 2020/2007

    @property
    def state_income_tax(self):
        if self._state_income_tax: return self._state_income_tax
        if self.location: return state_data.loc[self.location]['Income Tax Rate (decimal)']
        return 0
    @state_income_tax.setter
    def state_income_tax(self, tax):
        self._state_income_tax = tax
        
    @property
    def property_tax(self):
        if self._property_tax: return self._property_tax
        if self.location: return state_data.loc[self.location]['Property Tax Rate (decimal)']
    @property_tax.setter
    def property_tax(self, tax):
        self._property_tax = tax
        
    @property
    def state_fuel_producer_tax(self):
        if self._fuel_tax: return self._fuel_tax
        if self.location: return state_data.loc[self.location]['State Motor Fuel Tax (decimal)']
        return 0
    @state_fuel_producer_tax.setter
    def state_fuel_producer_tax(self, tax):
        self._fuel_tax = tax
        
    @property
    def sales_tax(self):
        if self._sales_tax: return self._sales_tax
        if self.location: return state_data.loc[self.location]['State Sales Tax Rate (decimal)']
        return 0
    @sales_tax.setter
    def sales_tax(self, tax):
        self._sales_tax = 0
        
    @property
    def LCCF(self): #LCCF stands for location capital cost factor
        if self._F_investment: return self._F_investment
        if self.location: return state_data.loc[self.location]['Location Capital Cost Factor (dimensionless)']
        return 1
    @LCCF.setter
    def LCCF(self, number):
        self._F_investment = number
        
    # TODO make sure electricity price property is set up correctly
    @property
    def electricity_price(self):
        if self.BT: return bst.PowerUtility.price
        if self.location: return state_data.loc[self.location]['Electricity Price (USD/kWh)']
        return 0.0681
    @electricity_price.setter
    def electricity_price(self, number):
        bst.PowerUtility.price = number
        
    def get_state_incentives(self):
        state = self.location
        if not state: return []
        avail_incentives = state_data.loc[state]['Incentives Available']
        avail_incentives = [] if pd.isna(avail_incentives) else avail_incentives # no incentives
        if avail_incentives is not None:
            try: # multiple incentives
                avail_incentives = [int(i) for i in avail_incentives if i.isnumeric()]
            except TypeError: # only one incentive
                avail_incentives = [int(avail_incentives)]
        return avail_incentives
        
    # TODO make sure incentive numbers works properly
    @property
    def incentive_numbers(self):
        if self._incentive_numbers: return self._incentive_numbers
        if self.location: return self.get_state_incentives()
        return []
    @incentive_numbers.setter
    def incentive_numbers(self, number):
        number = [] if not number else number
        self._incentive_numbers = list(number) # might need to adjust to accept multiple incentives

    def _FCI(self, TDC):
        self._FCI_cached = FCI = self.F_investment * super()._FCI(TDC)
        return FCI

    def _fill_tax_and_incentives(self, incentives, taxable_cashflow, nontaxable_cashflow, tax, depreciation):
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
            ethanol_eq = 1e6 * ethanol_group.get_installed_cost()
        else:
            ethanol = ethanol_eq = 0.
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
        taxable_property_arr = (construction_flow(taxable_property) - depreciation).cumsum()
        elec_eq_arr = construction_flow(elec_eq).cumsum()
        biodiesel_eq_arr = construction_flow(biodiesel_eq).cumsum()
        ethanol_eq_arr = construction_flow(ethanol_eq).cumsum()
        converyor_cost_arr = construction_flow(converyor_costs).cumsum()
        property_tax_arr = taxable_property_arr * self.property_tax
        fuel_tax_arr = self.fuel_tax * fuel_value_arr
        sales_tax = self.sales_tax
        purchase_cost_arr = construction_flow(self.purchase_cost)
        sales_arr = purchase_cost_arr + feedstock_value_arr
        sales_tax_arr = None if sales_tax is None else sales_arr * sales_tax
        util_cost_arr = yearly_flows(abs(self.utility_cost), startup_FOCfrac) # absolute value of utility cost bc it will likely always be negative
        util_tax_arr = self.utility_tax * util_cost_arr
        federal_assessed_income_tax = taxable_cashflow * self.federal_income_tax
        if self.deduct_federal_income_tax_to_state_taxable_earnings:
            state_assessed_income_tax = (taxable_cashflow - federal_assessed_income_tax) * self.state_income_tax
        else:
            state_assessed_income_tax = taxable_cashflow * self.state_income_tax
        if self.deduct_half_federal_income_tax_to_state_taxable_earnings:
            state_assessed_income_tax = (taxable_cashflow - (0.5*federal_assessed_income_tax)) * self.state_income_tax
        else:
            state_assessed_income_tax = taxable_cashflow * self.state_income_tax
        if self.state_tax_by_gross_receipts:
            revenue_arr = yearly_flows(self.sales, startup_VOCfrac)
            state_assessed_income_tax = revenue_arr * self.state_income_tax
        else:
            state_assessed_income_tax = taxable_cashflow * self.state_income_tax
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
            fed_income_tax_assessed=federal_assessed_income_tax,
            elec_eq=elec_eq_arr,
            jobs_50=self.jobs_50, # Assumption made by the original lipid-cane biorefinery publication
            utility_tax_assessed=util_tax_arr,
            state_income_tax_assessed=state_assessed_income_tax,
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
        tax[:] = property_tax_arr + fuel_tax_arr + sales_tax_arr # util_tax_arr; utility tax not currently considered
        tax[index] += federal_assessed_income_tax[index]
        if self.state_tax_by_gross_receipts:
            tax[:] += state_assessed_income_tax
        else:
            tax[index] += state_assessed_income_tax[index]
        maximum_incentives = credits + refunds + deductions + exemptions
        index = maximum_incentives > tax
        maximum_incentives[index] = tax[index]
        incentives[:] = maximum_incentives
        
class ConventionalBLocSTEA(sc.ConventionalEthanolTEA):

    def __init__(self, *args, incentive_numbers=[],
                 # property_tax=None,
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
                 location=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        # self._property_tax = property_tax
        self._state_income_tax = state_income_tax
        self.federal_income_tax = federal_income_tax
        self._incentive_numbers = incentive_numbers
        self.ethanol_product = ethanol_product
        self.biodiesel_product = biodiesel_product
        self.ethanol_group = ethanol_group
        self.biodiesel_group = biodiesel_group
        self._sales_tax = sales_tax
        self._fuel_tax = fuel_tax
        self.feedstock = feedstock
        self.utility_tax = utility_tax
        self._F_investment = F_investment
        self.BT = BT
        self.TDC_over_FCI = 0.625
        self.jobs_50 = 50
        self.location = location
        self.deduct_federal_income_tax_to_state_taxable_earnings = False # TODO add True statement for appropriate locations
        self.deduct_half_federal_income_tax_to_state_taxable_earnings = False
        self.state_tax_by_gross_receipts = False
        self.labor_cost *= (26.03/21.40) # BLS labor indices for years 2020/2013

    @property
    def state_income_tax(self):
        if self._state_income_tax: return self._state_income_tax
        if self.location: return state_data.loc[self.location]['Income Tax Rate (decimal)']
        return 0
    @state_income_tax.setter
    def state_income_tax(self, tax):
        self._state_income_tax = tax
        
    @property
    def property_tax(self):
        if self._property_tax: return self._property_tax
        if self.location: return state_data.loc[self.location]['Property Tax Rate (decimal)']
    @property_tax.setter
    def property_tax(self, tax):
        self._property_tax = tax
        
    @property
    def state_fuel_producer_tax(self):
        if self._fuel_tax: return self._fuel_tax
        if self.location: return state_data.loc[self.location]['State Motor Fuel Tax (decimal)']
        return 0
    @state_fuel_producer_tax.setter
    def state_fuel_producer_tax(self, tax):
        self._fuel_tax = tax
        
    @property
    def sales_tax(self):
        if self._sales_tax: return self._sales_tax
        if self.location: return state_data.loc[self.location]['State Sales Tax Rate (decimal)']
        return 0
    @sales_tax.setter
    def sales_tax(self, tax):
        self._sales_tax = 0
        
    @property
    def LCCF(self): #LCCF stands for location capital cost factor
        if self._F_investment: return self._F_investment
        if self.location: return state_data.loc[self.location]['Location Capital Cost Factor (dimensionless)']
        return 1
    @LCCF.setter
    def LCCF(self, number):
        self._F_investment = number
        
    # TODO make sure electricity price property is set up correctly
    @property
    def electricity_price(self):
        if self.BT: return bst.PowerUtility.price
        if self.location: return state_data.loc[self.location]['Electricity Price (USD/kWh)']
        return 0.0681
    @electricity_price.setter
    def electricity_price(self, number):
        bst.PowerUtility.price = number
        
    def get_state_incentives(self):
        state = self.location
        if not state: return []
        avail_incentives = state_data.loc[state]['Incentives Available']
        avail_incentives = [] if pd.isna(avail_incentives) else avail_incentives # no incentives
        if avail_incentives is not None:
            try: # multiple incentives
                avail_incentives = [int(i) for i in avail_incentives if i.isnumeric()]
            except TypeError: # only one incentive
                avail_incentives = [int(avail_incentives)]
        return avail_incentives
        
    # TODO make sure incentive numbers works properly
    @property
    def incentive_numbers(self):
        if self._incentive_numbers: return self._incentive_numbers
        if self.location: return self.get_state_incentives()
        return []
    @incentive_numbers.setter
    def incentive_numbers(self, number):
        number = [] if not number else number
        self._incentive_numbers = list(number) # might need to adjust to accept multiple incentives

    _fill_tax_and_incentives = CellulosicIncentivesTEA._fill_tax_and_incentives

    def _fill_depreciation_array(self, depreciation, start, years, FCI):
        TDC = self.TDC_over_FCI * FCI
        return super()._fill_depreciation_array( depreciation, start, years, TDC)

    def _DPI(self, installed_equipment_cost):
        return self.F_investment * installed_equipment_cost

    def _FOC(self, FCI):
        return (FCI*(self.property_insurance + self.maintenance + self.administration)
                + self.labor_cost*(1+self.fringe_benefits+self.supplies))
