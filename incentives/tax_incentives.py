#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
<<<<<<< HEAD
Created on Mon Jan 25 10:45:44 2021
=======
Tax Incentives
Authors: Dalton Stewart (dalton.w.stewart@gmail.com)
         Yoel Cortes-Pena (yoelcortes@gmail.com)

"""

import numpy as np
import pandas as pd
from inspect import signature

__all__ = (
    'EXEMPTIONS',
    'DEDUCTIONS',
    'CREDITS',
    'REFUNDS',
    'variable_incentives',
    'fixed_incentives',
    'determine_exemption_amount',
    'determine_deduction_amount',
    'determine_credit_amount',
    'determine_refund_amount',
    'determine_tax_incentives',
)

EXEMPTIONS = set(range(1, 7))
DEDUCTIONS = set(range(7, 8))
CREDITS = set(range(8, 20))
REFUNDS = set(range(21, 24))

def variable_incentives(durations, 
                        incentives, 
                        plant_years,
                        variable_incentive_frac_at_startup=1.,
                        start=0):
    """
    Return a 2d array of incentives based on variable operation.
    
    Parameters
    ----------
    durations : 1d array[int]
        Number of years an incentives last.
    incentives : 1d array[float]
        Dollar amount of incentive.
    plant_years : int
        Number of years plant will operate.
    variable_incentive_frac_at_startup : float
        Fraction of incentive at the startup year.
    start : int, optional
        Year incentive starts. Defaults to 0.
    
    """
    N_incentives = len(incentives)
    cashflow = np.zeros([plant_years, N_incentives])
    for i in range(N_incentives):
        cashflow[start: durations[i], i] = incentives[i] 
    cashflow[start, :] *= variable_incentive_frac_at_startup
    return cashflow

def fixed_incentives(durations,
                     incentives, 
                     plant_years,
                     start=0):
    """
    Return a 2d array of incentives based on fixed operation.
    
    Parameters
    ----------
    durations : 1d array[int]
        Number of years an incentives last.
    incentives : 1d array[float]
        Dollar amount of incentive.
    plant_years : int
        Number of years plant will operate.
    start : int, optional
        Year incentive starts. Defaults to 0.
    
    """
    N_incentives = len(incentives)
    cashflow = np.zeros([plant_years, N_incentives])
    for i in range(N_incentives):
        cashflow[start: durations[i], i] = incentives[i] 
    return cashflow

P_tax_value = np.zeros((20,)) #TODO
P_tax_value[:] = 2e6
fuel_tax_value = np.zeros((20,))#TODO
fuel_tax_value[:] = 330000

S_tax_value = np.zeros((20,))#TODO
S_tax_value[1:2] = 1e6

U_tax_assessed = np.zeros((20,))#TODO
U_tax_assessed[:] = 500000
SI_tax_assessed = np.zeros((20,))#TODO
SI_tax_assessed[:] = 3e6
SP_tax_assessed = np.zeros((20,))#TODO
SP_tax_assessed[:] = 1e6
eth_arr = np.zeros((20,))#TODO
eth_arr[:] = 100e6

def determine_exemption_amount(incentive_number,
                               plant_years,
                               property_taxable_value=0.,
                               value_added=0.,
                               biodiesel_eq=0.,
                               ethanol_eq=0.,
                               fuel_taxable_value=0.,
                               variable_incentive_frac_at_startup=1.,
                               start=0,
                               df=False):
    """
    Return 1d array of tax exemptions per year.
    
    Parameters
    ----------
    incentive_number : int
        Incentive type.
    plant_years : int
        Number of years plant will operate.
    value_added : float, optional
        Value added to property [$]. Presumably similar to TCI. 
        TODO: look for more specifics.
    property_taxable_value : array, optional 
        Value of property on which property tax can be assessed [$/yr].
    biodiesel_eq : float, optional
        Value of equipment used for producing biodiesel [$].
    ethanol_eq : float, optional
        Value of equipment used for producing ethanol [$].
    fuel_taxable_value : array, optional
        Amount of fuel on which fuel tax can be assessed [gal/year].
    variable_incentive_frac_at_startup : float
        Fraction of incentive at the startup year.
    start : int, optional
        Year incentive starts. Defaults to 0.
    df : bool, optional
        Whether to return a DataFrame or an array.
    
    """
    
    EXEMPTION=np.zeros((plant_years,))
    
    if incentive_number == 1:
        exemption_amount = value_added #value added to property, assume TCI
        duration = 20
        EXEMPTION[start:start+duration] = EXEMPTION[start:start+duration] + exemption_amount
        EXEMPTION = np.where(EXEMPTION>property_taxable_value,property_taxable_value,EXEMPTION)
    
    elif incentive_number == 2:
        duration = 10
        EXEMPTION[start:start+duration] = EXEMPTION[start:start+duration] + property_taxable_value[start:start+duration] #entire amount of state property taxable value
        #no > statement here bc the exempt amount is the entire amount of state property tax assessed
        
    elif incentive_number == 3:
        exemption_amount = biodiesel_eq
        duration = plant_years
        EXEMPTION[start:start+duration] = EXEMPTION[start:start+duration] + exemption_amount
        EXEMPTION = np.where(EXEMPTION>property_taxable_value,property_taxable_value,EXEMPTION)
        
    elif incentive_number == 4:
        exemption_amount = ethanol_eq
        duration = 10
        EXEMPTION[start:start+duration] = EXEMPTION[start:start+duration] + exemption_amount
        EXEMPTION = np.where(EXEMPTION>property_taxable_value,property_taxable_value,EXEMPTION)
        
    elif incentive_number == 5:
        duration = plant_years
        EXEMPTION[start:start+duration] = EXEMPTION[start:start+duration] + fuel_taxable_value[start:start+duration] #entire amount of state fuel taxable value
        #no > statement here bc the exempt amount is the entire amount of state fuel tax assessed
        
    elif incentive_number == 6:
        duration = plant_years
        EXEMPTION[start:start+duration] = EXEMPTION[start:start+duration] + property_taxable_value[start:start+duration] #entire amount of state property taxable value
        #no > statement here bc the exempt amount is the entire amount of state property tax assessed
        
    else: 
        EXEMPTION[:] = 0
        
    if df: EXEMPTION = pd.DataFrame(EXEMPTION, columns=['Tax exemption'])
    return EXEMPTION
    
def determine_deduction_amount(incentive_number,
                               plant_years,
                               NM_value=0.,
                               sales_taxable_value=0.,
                               start=0,
                               df=False):
    """
    Return 1d array of tax deductions per year.
    
    Parameters
    ----------
    incentive_number : int
        Incentive type.
    plant_years : int
        Number of years plant will operate.
    NM_value : float, optional
        Value of biomass boiler, gasifier, furnace, turbine-generator, 
        storage facility, feedstock processing or drying equipment, feedstock 
        trailer or interconnection transformer, and the value of biomass 
        materials [$/yr]
    sales_taxable_value : array
        Value of purchases on which sales tax can be assessed [$/yr]
    start : int, optional
        Year incentive starts. Defaults to 0.
    df : bool, optional
        Whether to return a DataFrame or an array.
        
    """
    
    DEDUCTION=np.zeros((plant_years,))
    
    if incentive_number == 7:
        deduction_amount = NM_value 
        duration = plant_years
        DEDUCTION[start:start+duration] = DEDUCTION[start:start+duration] + deduction_amount
        # DEDUCTION[start:start+duration] = DEDUCTION[start:start+duration] + NM_value[start:start+duration]
        DEDUCTION = np.where(DEDUCTION>sales_taxable_value,sales_taxable_value,DEDUCTION)
        
    #DO NOT DELETE
    #TODO ask Yoel, I'm not sure how this incentive would interact with the existing depreciation calculations
    # elif incentive_number == 26:
    # deduction_amount = 0.5*adj_basis #adjusted basis of property, formula varies; DON'T MULTIPLY BY TAX RATE
    # duration = 1
    # if deduction_amount <= property_taxable_value:
    #         deduction_amount = deduction_amount
    #     else:
    #         deduction_amount = property_taxable_value
    # cashflow = fixed_incentives([duration],[deduction_amount],
    #                                  plant_years, start)
    #DO NOT DELETE
        
    else: 
        DEDUCTION[:] = 0
        
    if df: DEDUCTION = pd.DataFrame(DEDUCTION, columns=['Tax deduction'])
    return DEDUCTION
        
def determine_credit_amount(incentive_number,
                            plant_years,
                            wages=0.,
                            TCI=0.,
                            ethanol=0.,
                            fed_income_tax_assessed=0.,
                            elec_eq=0.,
                            jobs_50=0.,
                            utility_tax_assessed=0.,
                            state_income_tax_assessed=0.,
                            property_tax_assessed=0.,
                            variable_incentive_frac_at_startup=1.,
                            start=0,
                            df=False):
    """
    Return 1d array of tax credits as cash flows per year.
    
    Parameters
    ----------
    incentive_number : int
        Incentive type.
    plant_years : int
        Number of years plant will operate.
    wages : float, optional
        Employee wages [$/yr].
    TCI : float, optional
        Total capital investment [$].
    ethanol : array
        Volume of ethanol produced [gal/yr].
    fed_income_tax_assessed : float, optional 
        Federal income tax per year [$/yr].
    elec_eq : float, optional 
        Value of equipment used for producing electricity [$]/
    jobs_50 : float, optional 
        Number of jobs paying more than 50,000 USD/yr.
    utility_tax_assessed
        Utility tax per year [$/yr]
    state_income_tax_assessed 
        State income tax per year [$/yr]
    property_tax_assessed
        Property tax per year [$/yr]
    variable_incentive_frac_at_startup : float
        Fraction of incentive at the startup year.
    start : int, optional
        Year incentive starts. Defaults to 0.
    df : bool, optional
        Whether to return a DataFrame or an array.
        
    """
    
    CREDIT = np.zeros((plant_years,))
    
    if incentive_number == 8:
        credit_amount = 0.03*wages #DON'T MULTIPLY BY TAX RATE
        duration = 10
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + credit_amount
        # CREDIT[start:start+duration] = CREDIT[start:start+duration] + 0.03*wages[start:start+duration]
        CREDIT = np.where(CREDIT>utility_tax_assessed,utility_tax_assessed,CREDIT)
        
    elif incentive_number == 9:
        credit_amount = 0.015*TCI #actually 'qualified capital investment', assume TCI; DON'T MULTIPLY BY TAX RATE
        duration = 10
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + credit_amount
        CREDIT = np.where(CREDIT>state_income_tax_assessed,state_income_tax_assessed,CREDIT)
        
    elif incentive_number == 10:
        credit_amount = 0.03*TCI #actually 'qualified investment', assume TCI; DON'T MULTIPLY BY TAX RATE
        duration = 22
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + credit_amount
        CREDIT[CREDIT>750000] = 750000
        CREDIT = np.where(CREDIT>state_income_tax_assessed,state_income_tax_assessed,CREDIT)
        
    elif incentive_number == 11:
        # credit = 76100*(0.2/76000)*ethanol # Fuel content of ethanol is 76100 btu/gal; DON'T MULTIPLY BY TAX RATE
        duration = 5
        # CREDIT[start:start+duration] = CREDIT[start:start+duration] + credit_amount
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + (76100*(0.2/76000))*ethanol[start:start+duration]
        CREDIT[CREDIT>3000000] = 3000000
        CREDIT = np.where(CREDIT>state_income_tax_assessed,state_income_tax_assessed,CREDIT)
        
    elif incentive_number == 12:
        total_credit = 0.05*TCI #actually just 'a percentage of qualifying investment', assume 5% of TCI, no max specified but may be inaccurate; DON'T MULTIPLY BY TAX RATE
        duration = 5
        credit_amount = total_credit/duration
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + credit_amount
        CREDIT = np.where(CREDIT>state_income_tax_assessed,state_income_tax_assessed,CREDIT)
        
    elif incentive_number == 13:
        duration = 15
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + state_income_tax_assessed[start:start+duration] #entire amount of state income tax assessed
        #no > statement here bc the credit amount is the entire amount of state income tax assessed
         
    elif incentive_number == 14:
        # credit = 1 * ethanol # 1 $/gal ethanol * gal ethanol; DON'T MULTIPLY BY TAX RATE
        # if credit <= 5000000:
        #     credit_amount = credit
        # else:
        #     credit_amount = 5000000
        duration = plant_years
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + 1*ethanol[start:start+duration] #1 $/gal ethanol * gal ethanol; DON'T MULTIPLY BY TAX RATE
        CREDIT[CREDIT>5000000] = 5000000
        CREDIT = np.where(CREDIT>state_income_tax_assessed,state_income_tax_assessed,CREDIT)
        
    elif incentive_number == 15:
        if TCI < 100000:
            credit_amount = 0
        if 100000<=TCI<=300000:
            credit_amount = 0.07*TCI
        elif 300000<TCI<=1000000:
            credit_amount = 0.14*TCI
        elif TCI>1000000:
            credit_amount = 0.18*TCI
        #there are other provisions to the incentive but they are more difficult to model so I will assume the maximum value is achieved via these provisions; DON'T MULTIPLY BY TAX RATE
        duration = 2 #estimated, incentive description is not clear
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + credit_amount
        CREDIT[CREDIT>1000000] = 1000000
        CREDIT = np.where(CREDIT>state_income_tax_assessed,state_income_tax_assessed,CREDIT)
        
    elif incentive_number == 16:
        total_credit = 0.25*TCI #actually cost of constructing and equipping facility; DON'T MULTIPLY BY TAX RATE
        duration = 7
        credit_amount = total_credit/duration #credit must be taken in equal installments over duration
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + credit_amount
        CREDIT = np.where(CREDIT>property_tax_assessed,property_tax_assessed,CREDIT)
            
    elif incentive_number == 17:
        credit_amount = 0.25*elec_eq #DON'T MULTIPLY BY TAX RATE
        # if credit <= 650000:
        #     credit_amount = credit
        # else:
        #     credit_amount = 650000
        duration = 15
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + credit_amount
        CREDIT[CREDIT>650000] = 650000
        CREDIT = np.where(CREDIT>state_income_tax_assessed,state_income_tax_assessed,CREDIT)
        
    elif incentive_number == 18:
        # credit_amount  = 0.75*state_income_tax_assessed #DON'T MULTIPLY BY TAX RATE
        duration = 20
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + 0.75*state_income_tax_assessed[start:start+duration]
        #no > statement here bc the credit amount depends on amount of state income tax assessed
        
    elif incentive_number == 19:
        credit_amount = 500*jobs_50 #number of jobs paying 50k+/year; DON'T MULTIPLY BY TAX RATE
        duration = 5
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + credit_amount
        CREDIT[CREDIT>175000] = 175000
        CREDIT = np.where(CREDIT>state_income_tax_assessed,state_income_tax_assessed,CREDIT)
        
    elif incentive_number == 20:
        # if ethanol <= 15000000:
        #     credit_amount = 1.01*ethanol #DON'T MULTIPLY BY TAX RATE
        # else:
        #     credit_amount = 1.01*15000000
        duration = plant_years
        CREDIT[start:start+duration] = CREDIT[start:start+duration] + 1.01*ethanol[start:start+duration]
        CREDIT[CREDIT>(1.01*15000000)] = (1.01*15000000)
        CREDIT = np.where(CREDIT>fed_income_tax_assessed,fed_income_tax_assessed,CREDIT)
        
    else: 
        CREDIT[:] = 0
        
    if df: CREDIT = pd.DataFrame(CREDIT, columns=['Tax credit'])
    return CREDIT   

def determine_refund_amount(incentive_number,
                            plant_years,
                            IA_value=0.,
                            building_mats=0.,
                            ethanol=0.,
                            sales_tax_rate=0.,
                            sales_tax_assessed=0.,
                            state_income_tax_assessed=0.,
                            variable_incentive_frac_at_startup=1.,
                            start=0,
                            df=False):
    """
    Return 1d array of tax refunds as cash flows per year.
    
    Parameters
    ----------
    incentive_number : int
        Incentive number.
    plant_years : int
        Number of years plant will operate.
    IA_value : float, optional
        Fees paid to (sub)contractors + cost of racks, shelving, conveyors [$].
    building_mats : float, optional
        Cost of building and construction materials [$].
    ethanol
        Volume of ethanol produced per year [gal/yr]
    sales_tax_rate
        State sales tax rate [decimal], i.e. for 6% enter 0.06
    sales_tax_assessed
        Sales tax per year [$/yr]
    state_income_tax_assessed
        State income tax per year [$/yr]
    start : int, optional
        Year incentive starts. Defaults to 0.
    df : bool, optional
        Whether to return a DataFrame or an array.
        
    """
  
    REFUND = np.zeros((plant_years,))
    
    if incentive_number == 21:
        refund_amount = IA_value * sales_tax_rate #fees paid to (sub)contractors + cost of racks, shelving, conveyors
        duration = 1
        REFUND[start:start+duration] = REFUND[start:start+duration] + refund_amount
        REFUND = np.where(REFUND>sales_tax_assessed,sales_tax_assessed,REFUND)
        
    elif incentive_number == 22:
        refund_amount = building_mats * sales_tax_rate #cost of building and construction materials
        duration = 1
        REFUND[start:start+duration] = REFUND[start:start+duration] + refund_amount
        REFUND = np.where(REFUND>sales_tax_assessed,sales_tax_assessed,REFUND)
        
    elif incentive_number == 23:
        # refund = 0.2*ethanol #DON'T MULTIPLY BY TAX RATE
        duration = plant_years
        REFUND[start:start+duration] = REFUND[start:start+duration] + 0.2*ethanol[start:start+duration]
        REFUND[REFUND>6e6] = 6e6
        REFUND = np.where(REFUND>state_income_tax_assessed,state_income_tax_assessed,REFUND)
           
    else: 
        REFUND[:] = 0
        
    if df: REFUND = pd.DataFrame(REFUND, columns=['Tax refund'])
    return REFUND
        
def determine_tax_incentives(incentive_numbers,
                             **kwargs):
    """
    Return a tuple of 1d arrays for tax excemptions, deductions, credits, and 
    refunds.

    Parameters
    ----------
    incentive_numbers : frozenset[int]
        Incentive types.
    **kwargs : 
        Key word arguments to calculate incentives.

    Raises
    ------
    ValueError
        On invalid incentive number.

    Returns
    -------
    exemptions : 1d array
    deductions : 1d array
    credits : 1d array
    refunds : 1d array

    """
    incentive_numbers = frozenset(incentive_numbers)
    exemptions = []
    deductions = []
    credits = []
    refunds = []
    for i in incentive_numbers:
        if i in EXEMPTIONS: exemptions.append(i)
        elif i in DEDUCTIONS: deductions.append(i)
        elif i in CREDITS: credits.append(i)
        elif i in REFUNDS: refunds.append(i)
        else: raise ValueError(f"invalid incentive number '{i}'")
    get_kwargs = lambda params: {i: kwargs[i] for i in params if i in kwargs} 
    exemption_kwargs = get_kwargs(EXCEMPTION_PARAMETERS)
    deduction_kwargs = get_kwargs(DEDUCTION_PARAMETERS)
    credit_kwargs = get_kwargs(CREDIT_PARAMETERS)
    refund_kwargs = get_kwargs(REFUND_PARAMETERS)
    get_incentives = lambda f, nums, kwargs: sum([f(i, **kwargs) for i in nums]) if nums else f(-1, **kwargs)
    exemptions = get_incentives(determine_exemption_amount, 
                                 exemptions, 
                                 exemption_kwargs)
    deductions = get_incentives(determine_deduction_amount, 
                                deductions, 
                                deduction_kwargs)
    credits = get_incentives(determine_credit_amount, 
                             credits, 
                             credit_kwargs)
    refunds = get_incentives(determine_refund_amount, 
                             refunds, refund_kwargs)
    return exemptions, deductions, credits, refunds

get_incentive_parameters = lambda f: tuple(signature(f).parameters)[1:]
EXCEMPTION_PARAMETERS = get_incentive_parameters(determine_exemption_amount)
DEDUCTION_PARAMETERS = get_incentive_parameters(determine_deduction_amount)
CREDIT_PARAMETERS = get_incentive_parameters(determine_credit_amount)
REFUND_PARAMETERS = get_incentive_parameters(determine_refund_amount)