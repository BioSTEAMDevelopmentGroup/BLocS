#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 10:45:44 2021

@author: daltonstewart
"""

import numpy as np
import pandas as pd

def variable_incentives(durations, 
                        incentives, 
                        plant_years,
                        variable_incentive_frac_at_startup=1.,
                        start=0):
    """Return a 2d array of incentive cashflows based on variable operation."""
    N_incentives = len(incentives)
    cashflow = np.zeros([plant_years, N_incentives])
    for i in range(N_incentives):
        cashflow[start: durations[i], i] = incentives[i] 
    cashflow[0, 0:] *= variable_incentive_frac_at_startup
    return cashflow

def fixed_incentives(durations,
                     incentives, 
                     plant_years,
                     start=0):
    """Return a 2d array of incentive cashflows based on fixed operation."""
    N_incentives = len(incentives)
    cashflow = np.zeros([plant_years, N_incentives])
    for i in range(N_incentives):
        cashflow[start: durations[i], i] = incentives[i] 
    return cashflow

def determine_exemption_amount(incentive,
                               plant_years,
                               value_added=0.,
                               property_tax_assessed=0.,
                               biodiesel_eq=0.,
                               ethanol_eq=0.,
                               fuel_tax_assessed=0.,
                               variable_incentive_frac_at_startup=1.,
                               start=0,
                               df=True):
    
    if incentive == '01':
        exemption_amount = value_added #value added to property, assume TCI
        duration = 20
        cashflow = fixed_incentives([duration],[exemption_amount],
                                     plant_years, start)
    
    elif incentive == '02':
        exemption_amount = property_tax_assessed #entire amount of state property tax assessed
        duration = 10
        cashflow = fixed_incentives([duration],[exemption_amount],
                                     plant_years, start)
        
    elif incentive == '03':
        exemption_amount = biodiesel_eq
        duration = plant_years
        cashflow = fixed_incentives([duration],[exemption_amount],
                                     plant_years, start)
        
    elif incentive == '04':
        exemption_amount = ethanol_eq
        duration = 10
        cashflow = fixed_incentives([duration],[exemption_amount],
                                     plant_years, start)
        
    elif incentive == '05':
        exemption_amount = fuel_tax_assessed #entire amount of state fuel tax assessed
        duration = plant_years
        cashflow = variable_incentives([duration],[exemption_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
        
    elif incentive == '06':
        exemption_amount = property_tax_assessed #entire amount of state property tax assessed
        duration = plant_years
        cashflow = fixed_incentives([duration],[exemption_amount],
                                     plant_years, start)
        
    #
    # elif incentive == '24':
    #     exemption_amount = air_eq #value of property used for air quality improvement project
    #     duration = 1
    #     cashflow = fixed_incentives([duration],[exemption_amount],
    #                                  plant_years, start)
        
    # elif incentive == '25':
    #     exemption_amount = blending_eq #value of equipment used for storing and blending petroleum fuel with biofuel (equipment used for denaturing ethanol not eligible)
    #     duration = 10
    #     cashflow = fixed_incentives([duration],[exemption_amount],
    #                                  plant_years, start)
    #
    else: 
        cashflow = fixed_incentives([plant_years], [0.], plant_years, start)
        
    if df: cashflow = pd.DataFrame(cashflow, columns=['Tax exemption'])
    return cashflow
    
def determine_deduction_amount(incentive,
                               plant_years,
                               NM_value=0.,
                               start=0,
                               df=True):
    
    if incentive == '07':
        deduction_amount = NM_value #TODO come up with formula
        duration = plant_years
        cashflow = fixed_incentives([duration],[deduction_amount],
                                     plant_years, start)
        
    #
    #TODO ask Yoel, I'm not sure how this incentive would interact with the existing depreciation calculations
    # elif incentive == '26':
    # deduction_amount = 0.5*adj_basis #adjusted basis of property, formula varies
    # duration = 1
    # cashflow = fixed_incentives([duration],[deduction_amount],
    #                                  plant_years, start)
    #
        
    else: 
        cashflow = fixed_incentives([plant_years], [0.], plant_years, start)
        
    if df: cashflow = pd.DataFrame(cashflow, columns=['Tax deduction'])
    return cashflow
        
def determine_credit_amount(incentive,
                               plant_years,
                               wages=0.,
                               TCI=0.,
                               ethanol=0.,
                               income_tax_assessed=0.,
                               elec_eq=0.,
                               jobs_50=0.,
                               variable_incentive_frac_at_startup=1.,
                               start=0,
                               df=True):
    
    if incentive == '08':
        credit_amount = 0.03*wages
        duration = 10
        cashflow = variable_incentives([duration],[credit_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
        
    elif incentive == '09':
        credit_amount = 0.015*TCI #actually 'qualified capital investment', assume TCI
        duration = 10
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive == '10':
        credit = 0.03*TCI #actually 'qualified investment', assume TCI
        if credit <= 750000:
            credit_amount = credit
        else:
            credit_amount = 750000
        duration = 22
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive == '11':
        credit = 76100*(0.2/76000)*ethanol # Fuel content of ethanol is 76100 btu/gal
        if credit <= 3000000:
            credit_amount = credit
        else:
            credit_amount = 3000000
        duration = 5
        cashflow = variable_incentives([duration],[credit_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
        
    elif incentive == '12':
        total_credit = 0.05*TCI #actually just 'a percentage of qualifying investment', assume 5% of TCI, no max specified but may be inaccurate
        duration = 5
        credit_amount = total_credit/duration
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive == '13':
        credit_amount = income_tax_assessed #entire amount of state income tax assessed
        duration = 15
        cashflow = variable_incentives([duration],[credit_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
         
    elif incentive == '14':
        credit = 1 * ethanol # 1 $/gal ethanol * gal ethanol
        if credit <= 5000000:
            credit_amount = credit
        else:
            credit_amount = 5000000
        duration = plant_years
        cashflow = variable_incentives([duration],[credit_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
        
    elif incentive == '15':
        if TCI < 100000:
            credit = 0
        if 100000<=TCI<=300000:
            credit = 0.07*TCI
        elif 300000<TCI<=1000000:
            credit = 0.14*TCI
        elif TCI>1000000:
            credit = 0.18*TCI
        if credit <= 1000000:
            credit_amount = credit
        else:
            credit_amount = 1000000
        #there are other provisions to the incentive but they are more difficult to model so I will assume the maximum value is achieved via these provisions
        duration = 2 #estimated, incentive description is not clear
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive == '16':
        total_credit = 0.25*TCI #actually cost of constructing and equipping facility
        duration = 7
        credit_amount = total_credit/duration #credit must be taken in equal installments over duration
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
            
    elif incentive == '17':
        credit = 0.25*elec_eq
        if credit <= 650000:
            credit_amount = credit
        else:
            credit_amount = 650000
        duration = 15
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive == '18':
        credit_amount  = 0.75*income_tax_assessed
        duration = 20
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive == '19':
        credit = 500*jobs_50 #number of jobs paying 50k+/year
        if credit <= 175000:
            credit_amount = credit
        else:
            credit_amount = 175000
        duration = 5
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive == '20':
        if ethanol <= 15000000:
            credit_amount = 1.01*ethanol
        else:
            credit_amount = 1.01*15000000
            duration = plant_years
            cashflow = variable_incentives([duration],[credit_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
        
    else: 
        cashflow = fixed_incentives([plant_years], [0.], plant_years, start)
        
    if df: cashflow = pd.DataFrame(cashflow, columns=['Tax credit'])
    return cashflow    

def determine_refund_amount(incentive,
                               plant_years,
                               IA_value=0.,
                               building_mats=0.,
                               ethanol=0.,
                               variable_incentive_frac_at_startup=1.,
                               start=0,
                               df=True):
        
    if incentive == '21':
        refund_amount = IA_value #fees paid to (sub)contractors + cost of racks, shelving, conveyors
        duration = 1
        cashflow = fixed_incentives([duration],[refund_amount],
                                     plant_years, start)
        
    elif incentive == '22':
        refund_amount = building_mats #cost of building and construction materials
        duration = 1
        cashflow = fixed_incentives([duration],[refund_amount],
                                     plant_years, start)
        
    elif incentive == '23':
        refund = 0.2*ethanol
        if refund <= 6e6:
            refund_amount = refund
        else:
            refund_amount = 6e6
        duration = plant_years
        cashflow = variable_incentives([duration],[refund_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
           
    else: 
        cashflow = fixed_incentives([plant_years], [0.], plant_years, start)
        
    if df: cashflow = pd.DataFrame(cashflow, columns=['Tax refund'])
    return cashflow
        