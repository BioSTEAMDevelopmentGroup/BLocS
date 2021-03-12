"""
Created on Sun Oct  4 12:18:15 2020

@author: yrc2. Modified by Dalton Stewart.
"""
import os
import pandas as pd
import numpy as np
from biorefineries import lipidcane as lc
from biorefineries import cornstover as cs
import incentives as inct
import biosteam as bst
    
__all__ = ('IncentivesTEA',)

class IncentivesTEA(lc.ConventionalEthanolTEA):
    
    def __init__(self, *args, incentive_numbers=(), 
                 state_income_tax=None,
                 federal_income_tax=None,
                 ethanol_product=None, 
                 biodiesel_product=None,
                 ethanol_group=None, 
                 biodiesel_group=None,
                 sales_tax=None,
                 fuel_tax=None,
                 BT=None,
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
        self.BT = BT 
    
    def _FOC(self, FCI):
        return (FCI*(self.property_insurance + self.maintenance + self.administration)
                + self.labor_cost*(1+self.fringe_benefits+self.supplies))
    
    def _fill_tax_and_incentives(self, incentives, taxable_cashflow, nontaxable_cashflow, tax):
        operating_hours = self._operating_hours
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
            ethanol_eq = 1e6 * self.lang_factor * ethanol_group.get_purchase_cost()
        else:
            ethanol = ethanol_eq = ethanol_sales = 0.
        if biodiesel_product: 
            fuel_value += biodiesel_product.cost * operating_hours
            biodiesel_eq = 1e6 * self.lang_factor * biodiesel_group.get_purchase_cost() 
        else:
            biodiesel_eq = 0.
        
        elec_eq = self.lang_factor * BT.purchase_cost if BT else 0.
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
        ethanol_arr = yearly_flows(ethanol, startup_VOCfrac)
        taxable_property_arr = construction_flow(taxable_property).cumsum()
        elec_eq_arr = construction_flow(elec_eq).cumsum()
        biodiesel_eq_arr = construction_flow(biodiesel_eq).cumsum()
        ethanol_eq_arr = construction_flow(ethanol_eq).cumsum()
        property_tax_arr = yearly_flows(FCI * self.property_tax, startup_FOCfrac)
        fuel_tax_arr = self.fuel_tax * fuel_value_arr
        sales_tax = self.sales_tax
        purchase_cost_arr = sales_arr = construction_flow(self.purchase_cost)
        sales_tax_arr = None if sales_tax is None else purchase_cost_arr * sales_tax
        
        exemptions, deductions, credits, refunds = inct.determine_tax_incentives(
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
            sales_taxable_value=sales_arr, # Only regards building materials
            sales_tax_rate=self.sales_tax,
            sales_tax_assessed=sales_tax_arr,
            wages=wages_arr,
            TCI=TCI,
            ethanol=ethanol_arr,
            fed_income_tax_assessed=taxable_cashflow * self.federal_income_tax,
            elec_eq=elec_eq_arr,
            jobs_50=50, # TODO: This is not explicit in BioSTEAM 
            utility_tax_assessed=0., # TODO: Ignore for now
            state_income_tax_assessed=taxable_cashflow * self.state_income_tax,
            property_tax_assessed=property_tax_arr,
            IA_value=elec_eq_arr, # TODO: this is not correct, pass a different ARRAY here
            building_mats=purchase_cost_arr,
            NM_value=elec_eq_arr, # TODO: Check this
        )
        self.exemptions = exemptions
        self.deductions = deductions
        self.credits = credits
        self.refunds = refunds
        # taxable_cashflow = taxable_cashflow - property_tax_arr
        taxable_cashflow[taxable_cashflow < 0.] = 0.
        index = taxable_cashflow > 0.
        tax[:] = property_tax_arr + fuel_tax_arr
        tax[index] += (self.federal_income_tax + self.state_income_tax) * taxable_cashflow[index] 
        maximum_incentives = credits + refunds + deductions + exemptions
        index = maximum_incentives > tax
        maximum_incentives[index] = tax[index]
        incentives[:] = maximum_incentives
   
# if __name__ == '__main__':
#     IRR_without_incentives = lc.lipidcane_tea.solve_IRR()
#     tea = lc.create_tea(lc.lipidcane_sys, IncentivesTEA)
#     tea.incentive_numbers = tuple(range(1, 21)) + tuple(range(22, 24))
#     tea.fuel_tax = 0.
#     tea.sales_tax = 0.
#     tea.sales_tax = 0.
#     tea.federal_income_tax = 0.35
#     tea.state_income_tax = 0. # TODO: Check this
#     tea.ethanol_product = lc.ethanol
#     tea.biodiesel_product = lc.biodiesel
#     tea.ethanol_group = lc.ethanol_production_units
#     tea.biodiesel_group = lc.biodiesel_production_units
#     tea.BT = lc.BT
#     IRR_with_incentives = tea.solve_IRR()
#     df = tea.get_cashflow_table()
#     print(f"{IRR_without_incentives=}")
#     print(f"{IRR_with_incentives=}")


# folder = os.path.dirname(__file__)
# xlfile = os.path.join(folder, 'State_Parameters.xlsx')
# nm_data = pd.read_excel(xlfile, index_col=[0])


# folder = os.path.dirname(__file__)

# available_states = ('AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
#                     'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 
#                     'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH',
#                     'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
#                     'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY')

# prices_by_state_with_federal = {}
# prices_by_state_without_federal = {}


# for state in available_states:
#             bst.PowerUtility.price = nm_data.loc['rate',state]
#             tea.state = state
#             tea.with_federal_incentives = True
#             prices_by_state_with_federal[state] = lc.ethanol.price = tea.solve_price(lc.ethanol)
#             prices_by_state_with_federal[state] *= 2.98668849 # USD/gal
#             tea.with_federal_incentives = False
#             prices_by_state_without_federal[state] = lc.ethanol.price = tea.solve_price(lc.ethanol)
#             prices_by_state_without_federal[state] *= 2.98668849 # USD/gal
            

# for kind in ("with federal", "without federal"):
#     with pd.ExcelWriter(os.path.join(folder, f'Incentives {kind}.xlsx')) as writer:
#         for state in available_states:
#             tea.state = state
#             tea.with_federal_incentives = include_federal = kind == "with federal"
#             prices_by_state_with_federal[state] = lc.ethanol.price = tea.solve_price(lc.ethanol)
#             prices_by_state_with_federal[state] *= 2.98668849 # USD/gal
#             df = tea.tax_incentives.calc_all_tax_incentives(df=True, include_federal=include_federal)
#             df.to_excel(writer, sheet_name=state + " incentives")
#             df = tea.get_cashflow_table()
#             df.to_excel(writer, sheet_name=state + " cash flows")
