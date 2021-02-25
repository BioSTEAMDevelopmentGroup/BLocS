#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 10:45:44 2021

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
    'determine_exemption_amount',
    'determine_deduction_amount',
    'determine_credit_amount',
    'determine_refund_amount',
    'determine_tax_incentives',
)

EXEMPTIONS = set(range(1, 7))
DEDUCTIONS = set(range(7, 8))
CREDITS = set(range(8, 21))
REFUNDS = set(range(21, 24))

# P_tax_value = np.zeros((20,)) #TODO
# P_tax_value[:] = 2e6
# fuel_tax_value = np.zeros((20,))#TODO
# fuel_tax_value[:] = 330000

# S_tax_value = np.zeros((20,))#TODO
# S_tax_value[1:2] = 1e6

# U_tax_assessed = np.zeros((20,))#TODO
# U_tax_assessed[:] = 500000
# SI_tax_assessed = np.zeros((20,))#TODO
# SI_tax_assessed[:] = 3e6
# SP_tax_assessed = np.zeros((20,))#TODO
# SP_tax_assessed[:] = 1e6
# eth_arr = np.zeros((20,))#TODO
# eth_arr[:] = 100e6

def check_missing_parameter(p, name):
    if p is None: raise ValueError(f"missing parameter '{name}'")

def check_any_missing_parameter(dct, names):
    for i in names: check_missing_parameter(dct[i], i)
        
def determine_exemption_amount(incentive_number,
                               plant_years,
                               property_taxable_value=None,
                               property_tax_rate=None,
                               value_added=None,
                               biodiesel_eq=None,
                               ethanol_eq=None,
                               fuel_taxable_value=None,
                               fuel_tax_rate=None,
                               start=0):
    """
    Return 1d array of tax exemptions per year.
    
    Parameters
    ----------
    incentive_number : int
        Incentive type.
    plant_years : int
        Number of years plant will operate.
    value_added : float, optional
        Value added to property [$]. Presumably similar to FCI. 
        TODO: look for more specifics.
    property_taxable_value : 1d array, optional 
        Value of property on which property tax can be assessed [$/yr].
    property_tax_rate : float, optional
        Property tax rate [-].
    biodiesel_eq : 1d array, optional
        Value of equipment used for producing biodiesel [$].
    ethanol_eq : 1d array, optional
        Value of equipment used for producing ethanol [$].
    fuel_taxable_value : 1d array, optional
        Amount of fuel on which fuel tax can be assessed [$/year].
    fuel_tax_rate : float, optional
        Fuel tax rate [-].
    start : int, optional
        Year incentive starts. Defaults to 0.
    
    """
    lcs = locals()
    exemption = np.zeros((plant_years,))
    if incentive_number == 1:
        params = ('value_added', 'property_taxable_value', 'property_tax_rate')
        check_any_missing_parameter(lcs, params)
        exemption_amount = value_added # Value added to property, assume FCI
        duration = 20
        exemption[start: start + duration] = exemption_amount
        exemption = np.where(exemption > property_taxable_value, 
                              property_taxable_value, 
                              exemption)
        exemption *= property_tax_rate
    elif incentive_number == 2:
        params = ('property_taxable_value', 'property_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = 10
        exemption[start: start + duration] = property_taxable_value[start: start + duration] #entire amount of state property taxable value
        # Exempt amount is the entire amount of state property tax assessed
        exemption *= property_tax_rate
    elif incentive_number == 3:
        params = ('biodiesel_eq', 'property_taxable_value', 'property_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = plant_years
        exemption[start: start + duration] = biodiesel_eq[start: start + duration]
        exemption = np.where(exemption > property_taxable_value,
                              property_taxable_value, 
                              exemption)
        exemption *= property_tax_rate        
    elif incentive_number == 4:
        params = ('ethanol_eq', 'property_taxable_value', 'property_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = 10
        exemption[start: start + duration] = ethanol_eq[start: start + duration]
        exemption = np.where(exemption > property_taxable_value, 
                              property_taxable_value, 
                              exemption)
        exemption *= property_tax_rate        
    elif incentive_number == 5:
        params = ('fuel_tax_rate', 'property_taxable_value', 'property_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = plant_years
        exemption[start: start + duration] = fuel_taxable_value[start: start + duration] #entire amount of state fuel taxable value
        # Exempt amount is the entire amount of state fuel tax assessed
        exemption *= fuel_tax_rate        
    elif incentive_number == 6:
        params = ('fuel_tax_rate', 'property_taxable_value', 'property_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = plant_years
        exemption[start: start + duration] = property_taxable_value[start: start + duration] #entire amount of state property taxable value
        # Exempt amount is the entire amount of state property tax assessed
        exemption *= property_tax_rate        
    return exemption
    
def determine_deduction_amount(incentive_number,
                               plant_years,
                               NM_value=None,
                               sales_taxable_value=None,
                               sales_tax_rate=None,
                               start=0):
    """
    Return 1d array of tax deductions per year.
    
    Parameters
    ----------
    incentive_number : int
        Incentive type.
    plant_years : int
        Number of years plant will operate.
    NM_value : 1d array, optional
        Value of biomass boiler, gasifier, furnace, turbine-generator, 
        storage facility, feedstock processing or drying equipment, feedstock 
        trailer or interconnection transformer, and the value of biomass 
        materials [$/yr]
    sales_taxable_value : 1d array
        Value of purchases on which sales tax can be assessed [$/yr]
    sales_tax_rate : float, optional
        Sales tax rate [-].
    start : int, optional
        Year incentive starts. Defaults to 0.
    """
    lcs = locals()
    deduction = np.zeros((plant_years,))
    if incentive_number == 7:
        params = ('NM_value', 'sales_taxable_value', 'sales_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = plant_years
        deduction[start: start + duration] = NM_value[start: start + duration]
        deduction = np.where(deduction > sales_taxable_value,
                             sales_taxable_value,
                             deduction)
        deduction *= sales_tax_rate
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
    return deduction
        
def determine_credit_amount(incentive_number,
                            plant_years,
                            wages=None,
                            TCI=None,
                            ethanol=None,
                            fed_income_tax_assessed=None,
                            elec_eq=None,
                            jobs_50=None,
                            utility_tax_assessed=None,
                            state_income_tax_assessed=None,
                            property_tax_assessed=None,
                            start=0):
    """
    Return 1d array of tax credits as cash flows per year.
    
    Parameters
    ----------
    incentive_number : int
        Incentive type.
    plant_years : int
        Number of years plant will operate.
    wages : 1d array, optional
        Employee wages [$/yr].
    TCI : float, optional
        Total capital investment [$].
    ethanol : 1d array
        Volume of ethanol produced [gal/yr].
    fed_income_tax_assessed : 1d array, optional 
        Federal income tax per year [$/yr].
    elec_eq : 1d array, optional 
        Value of equipment used for producing electricity [$].
    jobs_50 : int, optional 
        Number of jobs paying more than 50,000 USD/yr.
    utility_tax_assessed : 1d array, optional
        Utility tax per year [$/yr]
    state_income_tax_assessed : 1d array, optional
        State income tax per year [$/yr]
    property_tax_assessed : 1d array, optional
        Property tax per year [$/yr]
    start : int, optional
        Year incentive starts. Defaults to 0.
        
    """
    lcs = locals()
    credit = np.zeros((plant_years,))
    if incentive_number == 8:
        params = ('wages', 'utility_tax_assessed')
        check_any_missing_parameter(lcs, params)
        duration = 10
        credit[start: start + duration] = 0.03 * wages[start: start + duration]
        credit = np.where(credit > utility_tax_assessed, 
                          utility_tax_assessed, 
                          credit)
    elif incentive_number == 9:
        params = ('TCI', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        # Actually 'qualified capital investment', assume TCI; DON'T MULTIPLY BY TAX RATE
        duration = 10
        credit[start: start + duration] = 0.015 * TCI
        credit = np.where(credit > state_income_tax_assessed,
                          state_income_tax_assessed,
                          credit)
    elif incentive_number == 10:
        params = ('TCI', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        # actually 'qualified investment', assume TCI; DON'T MULTIPLY BY TAX RATE
        duration = 22
        credit[start: start + duration] = 0.03 * TCI
        credit[credit > 7.5e5] = 7.5e5
        credit = np.where(credit > state_income_tax_assessed,
                          state_income_tax_assessed,
                          credit)
    elif incentive_number == 11:
        params = ('ethanol', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        # Fuel content of ethanol is 76100 btu/gal; DON'T MULTIPLY BY TAX RATE
        # credit = 76100*(0.2/76000)*ethanol 
        duration = 5
        credit[start: start + duration] = 76100 * 0.2 / 76000 * ethanol[start: start + duration]
        credit[credit > 3e6] = 3e6
        credit = np.where(credit > state_income_tax_assessed, 
                          state_income_tax_assessed, 
                          credit)
    elif incentive_number == 12:
        params = ('TCI', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        total_credit = 0.05 * TCI # actually just 'a percentage of qualifying investment', assume 5% of TCI, no max specified but may be inaccurate; DON'T MULTIPLY BY TAX RATE
        duration = 5
        credit_amount = total_credit / duration
        credit[start: start + duration] = credit_amount
        credit = np.where(credit > state_income_tax_assessed,
                          state_income_tax_assessed,
                          credit)
    elif incentive_number == 13:
        params = ('state_income_tax_assessed',)
        check_any_missing_parameter(lcs, params)
        duration = 15
        credit[start: start + duration] = state_income_tax_assessed[start: start + duration] #entire amount of state income tax assessed
        # Credit amount is the entire amount of state income tax assessed
    elif incentive_number == 14:
        params = ('ethanol', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        duration = plant_years
        credit[start: start + duration] = ethanol[start: start + duration] #1 $/gal ethanol * gal ethanol; DON'T MULTIPLY BY TAX RATE
        credit[credit > 5e6] = 5e6
        credit = np.where(credit > state_income_tax_assessed,
                          state_income_tax_assessed,
                          credit)
    elif incentive_number == 15:
        params = ('TCI', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        if TCI < 1e5:
            credit_amount = 0
        if TCI <= 3e5:
            credit_amount = 0.07 * TCI
        elif TCI <= 1e6:
            credit_amount = 0.14 * TCI
        else:
            credit_amount = 0.18 * TCI
        # There are other provisions to the incentive but they are more difficult to model so I will assume the maximum value is achieved via these provisions; DON'T MULTIPLY BY TAX RATE
        duration = 2 # Estimated, incentive description is not clear
        credit[start: start + duration] = credit_amount
        credit[credit > 1e6] = 1e6
        credit = np.where(credit > state_income_tax_assessed,
                          state_income_tax_assessed,
                          credit)
    elif incentive_number == 16:
        params = ('TCI', 'property_tax_assessed')
        check_any_missing_parameter(lcs, params)
        total_credit = 0.25 * TCI # Actually cost of constructing and equipping facility; DON'T MULTIPLY BY TAX RATE
        duration = 7
        credit_amount = total_credit/duration #credit must be taken in equal installments over duration
        credit[start: start + duration] = credit_amount
        credit = np.where(credit > property_tax_assessed,
                          property_tax_assessed,
                          credit)
    elif incentive_number == 17:
        params = ('elec_eq', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        # if credit <= 650000:
        #     credit_amount = credit
        # else:
        #     credit_amount = 650000
        duration = 15
        credit[start: start + duration] = 0.25 * elec_eq[start: start + duration] # DON'T MULTIPLY BY TAX RATE
        credit[credit > 6.5e5] = 6.5e5
        credit = np.where(credit > state_income_tax_assessed,
                          state_income_tax_assessed,
                          credit)
    elif incentive_number == 18:
        params = ('state_income_tax_assessed',)
        check_any_missing_parameter(lcs, params)
        duration = 20
        # DON'T MULTIPLY BY TAX RATE
        credit[start: start + duration] = 0.75 * state_income_tax_assessed[start: start + duration]
        # Credit amount depends on amount of state income tax assessed
    elif incentive_number == 19:
        params = ('jobs_50', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        credit_amount = 500 * jobs_50 # Number of jobs paying 50k+/year; DON'T MULTIPLY BY TAX RATE
        duration = 5
        credit[start: start + duration] = credit_amount
        credit[credit > 1.75e5] = 1.75e5
        credit = np.where(credit > state_income_tax_assessed,
                          state_income_tax_assessed,
                          credit)
    elif incentive_number == 20:
        params = ('ethanol', 'fed_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        duration = plant_years
        credit[start: start + duration] = 1.01 * ethanol[start: start + duration]
        max_credit = 1.01 * 1.5e7
        credit[credit > max_credit] = max_credit
        credit = np.where(credit > fed_income_tax_assessed,
                          fed_income_tax_assessed,
                          credit)
    return credit   

def determine_refund_amount(incentive_number,
                            plant_years,
                            IA_value=None,
                            building_mats=None,
                            ethanol=None,
                            sales_tax_rate=None,
                            sales_tax_assessed=None,
                            state_income_tax_assessed=None,
                            start=0):
    """
    Return 1d array of tax refunds as cash flows per year.
    
    Parameters
    ----------
    incentive_number : int
        Incentive number.
    plant_years : int
        Number of years plant will operate.
    IA_value : 1d array, optional
        Fees paid to (sub)contractors + cost of racks, shelving, conveyors [$].
    building_mats : 1d array, optional
        Cost of building and construction materials [$].
    ethanol : 1d array, optional
        Volume of ethanol produced per year [gal/yr]
    sales_tax_rate : float, optional
        State sales tax rate [decimal], i.e. for 6% enter 0.06
    sales_tax_assessed : 1d array, optional
        Sales tax per year [$/yr]
    state_income_tax_assessed : 1d array, optional
        State income tax per year [$/yr]
    start : int, optional
        Year incentive starts. Defaults to 0.
        
    """
    lcs = locals()
    refund = np.zeros((plant_years,))
    if incentive_number == 21:
        params = ('IA_value', 'sales_tax_rate')
        check_any_missing_parameter(lcs, params)
        # Fees paid to (sub)contractors + cost of racks, shelving, conveyors
        duration = 1
        refund[start: start + duration] = sales_tax_rate * IA_value[start: start + duration]
        refund = np.where(refund > sales_tax_assessed,
                          sales_tax_assessed,
                          refund)
    elif incentive_number == 22:
        params = ('building_mats', 'sales_tax_rate')
        check_any_missing_parameter(lcs, params)
        # Cost of building and construction materials
        duration = 1
        refund[start: start + duration] = sales_tax_rate  * building_mats[start: start + duration]
        refund = np.where(refund > sales_tax_assessed,
                          sales_tax_assessed,
                          refund)
    elif incentive_number == 23:
        params = ('ethanol', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        # refund = 0.2*ethanol #DON'T MULTIPLY BY TAX RATE
        duration = plant_years
        refund[start: start + duration] = 0.2 * ethanol[start: start + duration]
        refund[refund > 6e6] = 6e6
        refund = np.where(refund > state_income_tax_assessed,
                          state_income_tax_assessed,
                          refund)
    return refund
        
def determine_tax_incentives(incentive_numbers,
                             **kwargs):
    """
    Return a tuple of 1d arrays for tax exemptions, deductions, credits, and 
    refunds.

    Parameters
    ----------
    incentive_numbers : frozenset[int]
        Incentive types.

    Other parameters
    ----------------
    start : int, optional
        Year incentive starts. Defaults to 0.
    plant_years : int
        Number of years plant will operate.
    value_added : float, optional
        Value added to property [$]. Presumably similar to FCI. 
        TODO: look for more specifics.
    property_taxable_value : 1d array, optional 
        Value of property on which property tax can be assessed [$/yr].
    property_tax_rate : float, optional
        Property tax rate [-].
    biodiesel_eq : 1d array, optional
        Value of equipment used for producing biodiesel [$].
    ethanol_eq : 1d array, optional
        Value of equipment used for producing ethanol [$].
    fuel_taxable_value : 1d array, optional
        Amount of fuel on which fuel tax can be assessed [$/year].
    fuel_tax_rate : float, optional
        Fuel tax rate [-].
    NM_value : 1d array, optional
        Value of biomass boiler, gasifier, furnace, turbine-generator, 
        storage facility, feedstock processing or drying equipment, feedstock 
        trailer or interconnection transformer, and the value of biomass 
        materials [$/yr].
    sales_taxable_value : 1d array
        Value of purchases on which sales tax can be assessed [$/yr]
    sales_tax_rate : float, optional
        Sales tax rate [-].
    sales_tax_assessed : 1d array, optional
        Sales tax per year [$/yr]
    wages : 1d array, optional
        Employee wages [$/yr].
    TCI : float, optional
        Total capital investment [$].
    ethanol : 1d array
        Volume of ethanol produced [gal/yr].
    fed_income_tax_assessed : 1d array, optional 
        Federal income tax per year [$/yr].
    elec_eq : 1d array, optional 
        Value of equipment used for producing electricity [$].
    jobs_50 : int, optional 
        Number of jobs paying more than 50,000 USD/yr.
    utility_tax_assessed : 1d array, optional
        Utility tax per year [$/yr]
    state_income_tax_assessed : 1d array, optional
        State income tax per year [$/yr]
    property_tax_assessed : 1d array, optional
        Property tax per year [$/yr]
    IA_value : 1d array, optional
        Fees paid to (sub)contractors + cost of racks, shelving, conveyors [$].
    building_mats : 1d array, optional
        Cost of building and construction materials [$].
        
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
    exemption_kwargs = get_kwargs(EXEMPTION_PARAMETERS)
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
EXEMPTION_PARAMETERS = get_incentive_parameters(determine_exemption_amount)
DEDUCTION_PARAMETERS = get_incentive_parameters(determine_deduction_amount)
CREDIT_PARAMETERS = get_incentive_parameters(determine_credit_amount)
REFUND_PARAMETERS = get_incentive_parameters(determine_refund_amount)