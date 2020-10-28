#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tax Incentives
Authors: Dalton Stewart, Yoel Cortes-Pena
"""

# %%
from incentives import *
from numpy.testing import assert_allclose
import numpy as np
import pandas as pd

def test_variable_incentives():
    lifetime = 20
    duration = 15
    data = np.zeros(lifetime)
    data[0] = 7500.0
    data[1:duration] = 10000.0
    values = variable_incentives([15], [10000], lifetime, .75)
    assert_allclose(data, values[:, 0])

def test_determine_state_credit_amount():
    data = [150197.368421, 200263.157895, 200263.157895, 200263.157895, 200263.157895, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]
    values = determine_state_credit_amount('HI', 20, .75, ethanol=1e6, df=False)
    assert_allclose(data, values[:, 0])
     
def test_determine_fed_credit_amount():
    data = [757500.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0, 1010000.0]
    values = determine_fed_credit_amount(20, .75, ethanol=1e6, df=False)
    assert_allclose(data, values[:, 0])

def test_determine_state_refund_amount():
    data = [4761.904762, 0.000000, 0.000000, 0.000000, 0.000000]
    values = determine_state_refund_amount('KY', 5, .75, construction_costs=100000, df=False)
    assert_allclose(data, values[:, 0])

def test_determine_state_deduction_amount():
    data = [512.5, 512.5, 512.5, 512.5, 512.5]
    values = determine_state_deduction_amount('NM', 5, NM_value=10000, df=False)
    assert_allclose(data, values[:, 0])

def test_determine_fed_deduction_amount():
    data = [50.0, 0.0, 0.0, 0.0]
    values = determine_fed_deduction_amount(4, adj_basis=100, df=False)
    assert_allclose(data, values[:, 0])

#%% Tax exemption calculations

def test_determine_state_exemption_amount():
    data = [3000.0,3000.0,3000.0,3000.0,3000.0,3000.0,3000.0,3000.0]
    values = determine_state_exemption_amount('KS',8,.75,fuel_mix_eq=1000,state_property_tax=2000, df=False)
    assert_allclose(data, values[:, 0])

def test_determine_net_metering_limit():
    assert_allclose(3000.0, determine_net_metering_limit(3000,0,10e7,4800))

def test_determine_net_metering_revenue():
    data = [2576000.0,2576000.0,2576000.0,2576000.0,2576000.0]
    values = determine_net_metering_revenue(5,10e7,4800,3000,.06,.02, df=False)
    assert_allclose(data, values[:, 0])
      
def test_calc_all_tax_incentives():
    data = {
        'Federal credit': [7575000.0, 10100000.0],
        'Federal deduction': [85000.0, 0.0],
        'Income tax credit': [100000.0, 100000.0],
        'Ethanol credit': [3750000.0, 5000000.0],
        'State refund': [7142.857142857142, 0.0],
        'State deduction': [0.0, 0.0],
        'State exemption': [0.0, 0.0],
        'Net metering': [0.0, 0.0]
    }
    values = pd.DataFrame(data,columns=['Federal credit','Federal deduction','Income tax credit','Ethanol credit','State refund','State deduction','State exemption','Net metering'])
    KY = TaxIncentives('KY',2,.75,ethanol=10e6,state_income_tax=100000,construction_costs=150000,adj_basis=170000)
    overall_cashflow = KY.calc_all_tax_incentives()
    assert_allclose(overall_cashflow, values)

def test_integration_with_biosteam():
    from biorefineries import lipidcane as lc
    
    class IncentivesTEA(lc.ConventionalEthanolTEA):
        
        def __init__(self, *args, state='KY', **kwargs):
            self.state = state
            super().__init__(*args, **kwargs)
        
        def _fill_incentives(self, incentives, taxable_cashflow, nontaxable_cashflow, tax):
            operating_hours = self._operating_hours
            ethanol = 0.
            for i in self.system.products:
                if 'Ethanol' in i.chemicals:
                    F_mol = i.F_mol 
                    if F_mol and i.imol['Ethanol'] / i.F_mol > 0.95:
                        ethanol = i.get_total_flow('gal/hr') * operating_hours
                        break
            biodiesel_eq = 0.
            for s in self.system.streams:
                if 'Lipid' in i.chemicals:
                    F_mol = i.F_mol 
                    if F_mol and i.imol['Lipid'] / i.F_mol > 0.95:
                        biodiesel_eq = sum([i.installed_cost for i in s.sink._downstream_units])
                        break
            ethanol_eq = 0.
            for sys in self.system.subsystems:
                if sys.ID == 'ethanol_production_sys':
                    ethanol_eq = sum([i.installed_cost for i in sys.units])
            elec_eq = sum([i.installed_cost for i in self.units if i.power_utility.production])
            TCI = self.TCI
            tax_incentives = TaxIncentives(
                 state=self.state,
                 plant_years=self._years + self._start, 
                 variable_incentive_frac_at_startup=self.startup_VOCfrac,
                 wages=self.labor_cost, 
                 TCI=TCI, 
                 ethanol=ethanol,
                 state_income_tax=0., 
                 jobs_50=50, # TODO: This is not explicit in BioSTEAM 
                 elec_eq=elec_eq,
                 construction_costs=TCI, # TODO: Verify this assumption 
                 subcontract_fees=0.,
                 racks_etc=0., 
                 NM_value=0., # TODO: What is this?
                 adj_basis=0., # TODO: Define property please
                 value_add=0., 
                 state_property_tax=0., 
                 airq_taxes=0.,
                 fuel_mix_eq=0., # TODO: This can be ignored 
                 biodiesel_eq=biodiesel_eq, 
                 ethanol_eq=ethanol_eq,
                 elec_use=sum([i.power_utility.consumption for i in self.units]),
                 elec_gen=sum([i.power_utility.production for i in self.units]),
                 op_hours=operating_hours,
                 start=self._start)
            tax_incentives.load_net_metering_parameters()
            credits_ = tax_incentives.calc_all_tax_incentives(df=False)    
            credits_[credits_ > tax] = tax
            incentives[:] = credits_
            
    tea = lc.create_tea(lc.lipidcane_sys, IncentivesTEA)
    price = tea.solve_price(lc.ethanol) * 2.98668849 # USD/gal
    assert_allclose(price, 1.3549310277674518) # With incentives, price is almost half
        

# def test_new_incentives():
#     data = [2500.0,2500.0,2500.0,0.0,0.0]
#     values = new_incentives(['incentive'],[3],[10000],[.25],5, df=False)
#     assert_allclose(data, values[:, 0])

# def test_calc_all_new_tax_incentives():
#     data = {'incentive':[50.0,50.0]}
#     expected = pd.DataFrame(data,columns=['incentive'])
#     new = NewTaxIncentives(['incentive'],[2],[100],[.5],2,1)
#     new.calc_all_incentives()
#     values = new.overall_cashflow
      
#     assert sorted(expected) == sorted(values)
    


