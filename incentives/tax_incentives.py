#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 10:45:44 2021

@author: daltonstewart
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
)

EXEMPTIONS = set(range(1, 6))
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

def determine_exemption_amount(incentive_number,
                               plant_years,
                               value_added=0.,
                               property_tax_assessed=0.,
                               biodiesel_eq=0.,
                               ethanol_eq=0.,
                               fuel_tax_assessed=0.,
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
    property_tax_assessed : float, optional
        Property tax per year [$/yr].
    biodiesel_eq : float, optional
        Value of equipment used for producing biodiesel [$].
    ethanol_eq : float, optional
        Value of equipment used for producing ethanol [$].
    fuel_tax_assessed : float, optional
        Fuel tax per year [$/yr].
    variable_incentive_frac_at_startup : float
        Fraction of incentive at the startup year.
    start : int, optional
        Year incentive starts. Defaults to 0.
    df : bool, optional
        Whether to return a DataFrame or an array.
    
    """
    
    if incentive_number == 1:
        exemption_amount = value_added #value added to property, assume TCI
        duration = 20
        cashflow = fixed_incentives([duration],[exemption_amount],
                                     plant_years, start)
    
    elif incentive_number == 2:
        exemption_amount = property_tax_assessed #entire amount of state property tax assessed
        duration = 10
        cashflow = fixed_incentives([duration],[exemption_amount],
                                     plant_years, start)
        
    elif incentive_number == 3:
        exemption_amount = biodiesel_eq
        duration = plant_years
        cashflow = fixed_incentives([duration],[exemption_amount],
                                     plant_years, start)
        
    elif incentive_number == 4:
        exemption_amount = ethanol_eq
        duration = 10
        cashflow = fixed_incentives([duration],[exemption_amount],
                                     plant_years, start)
        
    elif incentive_number == 5:
        exemption_amount = fuel_tax_assessed #entire amount of state fuel tax assessed
        duration = plant_years
        cashflow = variable_incentives([duration],[exemption_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
        
    elif incentive_number == 6:
        exemption_amount = property_tax_assessed #entire amount of state property tax assessed
        duration = plant_years
        cashflow = fixed_incentives([duration],[exemption_amount],
                                     plant_years, start)
        
    #
    # elif incentive_number == 24:
    #     exemption_amount = air_eq #value of property used for air quality improvement project
    #     duration = 1
    #     cashflow = fixed_incentives([duration],[exemption_amount],
    #                                  plant_years, start)
        
    # elif incentive_number == 25:
    #     exemption_amount = blending_eq #value of equipment used for storing and blending petroleum fuel with biofuel (equipment used for denaturing ethanol not eligible)
    #     duration = 10
    #     cashflow = fixed_incentives([duration],[exemption_amount],
    #                                  plant_years, start)
    #
    else: 
        cashflow = fixed_incentives([plant_years], [0.], plant_years, start)
        
    if df: cashflow = pd.DataFrame(cashflow, columns=['Tax exemption'])
    return cashflow
    
def determine_deduction_amount(incentive_number,
                               plant_years,
                               NM_value=0.,
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
    start : int, optional
        Year incentive starts. Defaults to 0.
    df : bool, optional
        Whether to return a DataFrame or an array.
        
    """
    
    if incentive_number == 7:
        deduction_amount = NM_value #TODO come up with formula
        duration = plant_years
        cashflow = fixed_incentives([duration],[deduction_amount],
                                     plant_years, start)
        
    #
    #TODO ask Yoel, I'm not sure how this incentive would interact with the existing depreciation calculations
    # elif incentive_number == 26:
    # deduction_amount = 0.5*adj_basis #adjusted basis of property, formula varies
    # duration = 1
    # cashflow = fixed_incentives([duration],[deduction_amount],
    #                                  plant_years, start)
    #
        
    else: 
        cashflow = fixed_incentives([plant_years], [0.], plant_years, start)
        
    if df: cashflow = pd.DataFrame(cashflow, columns=['Tax deduction'])
    return cashflow
        
def determine_credit_amount(incentive_number,
                            plant_years,
                            wages=0.,
                            TCI=0.,
                            ethanol=0.,
                            income_tax_assessed=0.,
                            elec_eq=0.,
                            jobs_50=0.,
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
    ethanol :
        Volume of ethanol produced [gal/yr].
    income_tax_assessed : float, optional 
        Income tax per year [$/yr].
    elec_eq : float, optional 
        Value of equipment used for producing electricity [$]/
    jobs_50 : float, optional 
        Number of jobs paying more than 50,000 USD/yr.
    variable_incentive_frac_at_startup : float
        Fraction of incentive at the startup year.
    start : int, optional
        Year incentive starts. Defaults to 0.
    df : bool, optional
        Whether to return a DataFrame or an array.
        
    """
    
    if incentive_number == 8:
        credit_amount = 0.03*wages
        duration = 10
        cashflow = variable_incentives([duration],[credit_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
        
    elif incentive_number == 9:
        credit_amount = 0.015*TCI #actually 'qualified capital investment', assume TCI
        duration = 10
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive_number == 10:
        credit = 0.03*TCI #actually 'qualified investment', assume TCI
        if credit <= 750000:
            credit_amount = credit
        else:
            credit_amount = 750000
        duration = 22
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive_number == 11:
        credit = 76100*(0.2/76000)*ethanol # Fuel content of ethanol is 76100 btu/gal
        if credit <= 3000000:
            credit_amount = credit
        else:
            credit_amount = 3000000
        duration = 5
        cashflow = variable_incentives([duration],[credit_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
        
    elif incentive_number == 12:
        total_credit = 0.05*TCI #actually just 'a percentage of qualifying investment', assume 5% of TCI, no max specified but may be inaccurate
        duration = 5
        credit_amount = total_credit/duration
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive_number == 13:
        credit_amount = income_tax_assessed #entire amount of state income tax assessed
        duration = 15
        cashflow = variable_incentives([duration],[credit_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
         
    elif incentive_number == 14:
        credit = 1 * ethanol # 1 $/gal ethanol * gal ethanol
        if credit <= 5000000:
            credit_amount = credit
        else:
            credit_amount = 5000000
        duration = plant_years
        cashflow = variable_incentives([duration],[credit_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
        
    elif incentive_number == 15:
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
        
    elif incentive_number == 16:
        total_credit = 0.25*TCI #actually cost of constructing and equipping facility
        duration = 7
        credit_amount = total_credit/duration #credit must be taken in equal installments over duration
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
            
    elif incentive_number == 17:
        credit = 0.25*elec_eq
        if credit <= 650000:
            credit_amount = credit
        else:
            credit_amount = 650000
        duration = 15
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive_number == 18:
        credit_amount  = 0.75*income_tax_assessed
        duration = 20
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive_number == 19:
        credit = 500*jobs_50 #number of jobs paying 50k+/year
        if credit <= 175000:
            credit_amount = credit
        else:
            credit_amount = 175000
        duration = 5
        cashflow = fixed_incentives([duration],[credit_amount],
                                     plant_years, start)
        
    elif incentive_number == 20:
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

def determine_refund_amount(incentive_number,
                            plant_years,
                            IA_value=0.,
                            building_mats=0.,
                            ethanol=0.,
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
    start : int, optional
        Year incentive starts. Defaults to 0.
    df : bool, optional
        Whether to return a DataFrame or an array.
        
    """
    if incentive_number == 21:
        refund_amount = IA_value #fees paid to (sub)contractors + cost of racks, shelving, conveyors
        duration = 1
        cashflow = fixed_incentives([duration],[refund_amount],
                                     plant_years, start)
        
    elif incentive_number == 22:
        refund_amount = building_mats #cost of building and construction materials
        duration = 1
        cashflow = fixed_incentives([duration],[refund_amount],
                                     plant_years, start)
        
    elif incentive_number == 23:
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