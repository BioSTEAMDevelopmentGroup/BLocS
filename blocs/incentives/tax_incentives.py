#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 10:45:44 2021

Tax Incentives
Authors: Dalton Stewart (dalton.w.stewart@gmail.com)
         Yoel Cortes-Pena (yoelcortes@gmail.com)

Users should note that tax incentives 1/E1, 8/C2, 9/C3, 10/C4, 14/C8, 15/C9, 18/R1
are no longer in effect according to the Alternative Fuels Data Center (AFDC) and
Database of State Incentives for Renewables and Efficiency (DSIRE). These incentives
currently remain available for users to evaluate and no new incentives have
been added for consideration as of January 18, 2024.

"""

import numpy as np
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

EXEMPTIONS = set(range(1, 6))
DEDUCTIONS = set(range(6, 7))
CREDITS = set(range(7, 18))
REFUNDS = set(range(18, 21))

def check_missing_parameter(p, name):
    if p is None: raise ValueError(f"missing parameter '{name}'")

def check_any_missing_parameter(dct, names):
    for i in names: check_missing_parameter(dct[i], i)

def assess_incentive(start, duration, plant_years, incentive, amount, assessed_tax, ub=None):
    start = max(start, assessed_tax.argmax())
    if start + duration > plant_years: start = plant_years - duration
    incentive[start: start + duration] = amount
    if ub is not None: incentive[incentive > ub] = ub
    incentive = np.where(
        incentive > assessed_tax,
        assessed_tax,
        incentive
    )
    return incentive

def assess_incentive_arr(start, duration, plant_years, incentive, amount, assessed_tax, ub=None):
    start = max(start, assessed_tax.argmax())
    if start + duration > plant_years: start = plant_years - duration
    incentive[start: start + duration] = amount[start: start + duration]
    if ub is not None: incentive[incentive > ub] = ub
    incentive = np.where(
        incentive > assessed_tax,
        assessed_tax,
        incentive
    )
    return incentive

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
        Value added to property [$]. Assume similar to FCI.
    property_taxable_value : 1d array, optional
        Value of property on which property tax can be assessed [$].
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
    if incentive_number == 1: #Referred to as Incentive E1 (for "Exemption 1") in manuscript
        params = ('value_added', 'property_taxable_value', 'property_tax_rate')
        check_any_missing_parameter(lcs, params)
        exemption_amount = value_added # Value added to property, assume FCI
        duration = 20
        exemption[start: start + duration] = exemption_amount
        exemption = assess_incentive(start, duration, plant_years, exemption, exemption_amount, property_taxable_value)
        exemption *= property_tax_rate
    elif incentive_number == 2: #Referred to as Incentive E2 in manuscript
        params = ('property_taxable_value', 'property_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = 10
        exemption = assess_incentive_arr(start, duration, plant_years, exemption, property_taxable_value, property_taxable_value)
        exemption *= property_tax_rate # Exempt amount is the entire amount of state property tax assessed
    elif incentive_number == 3: #Referred to as Incentive E3 in manuscript
        params = ('ethanol_eq', 'property_taxable_value', 'property_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = 10
        exemption = assess_incentive_arr(start, duration, plant_years, exemption, ethanol_eq, property_taxable_value)
        exemption *= property_tax_rate
    elif incentive_number == 4: #Referred to as Incentive E4 in manuscript
        params = ('fuel_tax_rate', 'property_taxable_value', 'property_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = plant_years
        exemption = assess_incentive_arr(start, duration, plant_years, exemption, fuel_taxable_value, fuel_taxable_value)
        exemption *= fuel_tax_rate # Exempt amount is the entire amount of state fuel tax assessed
    elif incentive_number == 5: #Referred to as Incentive E5 in manuscript
        params = ('fuel_tax_rate', 'property_taxable_value', 'property_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = plant_years
        exemption = assess_incentive_arr(start, duration, plant_years, exemption, property_taxable_value, property_taxable_value)
        exemption *= property_tax_rate # Exempt amount is the entire amount of state property tax assessed
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
    if incentive_number == 6: #Referred to as Incentive D1 (for "Deduction 1") in manuscript
        params = ('NM_value', 'sales_taxable_value', 'sales_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = plant_years
        deduction = assess_incentive_arr(start, duration, plant_years, deduction, NM_value, sales_taxable_value)
        deduction *= sales_tax_rate
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
    if incentive_number == 7: #Referred to as Incentive C1 (for "Credit 1") in manuscript
        params = ('TCI', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        # Actually 'qualified capital investment', assume TCI; DON'T MULTIPLY BY TAX RATE HERE
        duration = 10
        credit = assess_incentive(start, duration, plant_years, credit, 0.015 * TCI, state_income_tax_assessed)
    elif incentive_number == 8: #Referred to as Incentive C2 in manuscript
        params = ('TCI', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        # actually 'qualified investment', assume TCI; DON'T MULTIPLY BY TAX RATE HERE
        duration = 22
        credit = assess_incentive(start, duration, plant_years, credit, 0.03 * TCI, state_income_tax_assessed, 7.5e5)
    elif incentive_number == 9: #Referred to as Incentive C3 in manuscript
        params = ('ethanol', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        # Fuel content of ethanol is 76100 btu/gal; DON'T MULTIPLY BY TAX RATE HERE
        duration = 5
        credit = assess_incentive_arr(start, duration, plant_years, credit, 76100 * 0.2 / 76000 * ethanol, state_income_tax_assessed, 3e6)
    elif incentive_number == 10: #Referred to as Incentive C4 in manuscript
        params = ('TCI', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        total_credit = 0.05 * TCI # actually just 'a percentage of qualifying investment', assume 5% of TCI, no max specified but may be inaccurate; DON'T MULTIPLY BY TAX RATE HERE
        duration = 5
        credit = assess_incentive(start, duration, plant_years, credit, (0.05 * TCI)/duration, state_income_tax_assessed)
    elif incentive_number == 11: #Referred to as Incentive C5 in manuscript
        params = ('state_income_tax_assessed',)
        check_any_missing_parameter(lcs, params)
        duration = 15
        credit = assess_incentive_arr(start, duration, plant_years, credit, state_income_tax_assessed, state_income_tax_assessed)# Credit amount is the entire amount of state income tax assessed
    elif incentive_number == 12: #Referred to as Incentive C6 in manuscript
        params = ('ethanol', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        duration = plant_years
        credit = assess_incentive_arr(start, duration, plant_years, credit, ethanol, state_income_tax_assessed,5e6)
    elif incentive_number == 13: #Referred to as Incentive C7 in manuscript
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
        # There are other provisions to the incentive but they are more difficult to model so I will assume the maximum value is achieved via these provisions; DON'T MULTIPLY BY TAX RATE HERE
        duration = 2 # Estimated, incentive description is not clear
        credit = assess_incentive(start, duration, plant_years, credit, credit_amount, state_income_tax_assessed, 1e6)
    elif incentive_number == 14: #Referred to as Incentive C8 in manuscript
        params = ('TCI', 'property_tax_assessed')
        check_any_missing_parameter(lcs, params)
        total_credit = 0.25 * TCI # Actually cost of constructing and equipping facility; DON'T MULTIPLY BY TAX RATE HERE
        duration = 7
        credit_amount = total_credit/duration #credit must be taken in equal installments over duration
        credit = assess_incentive(start, duration, plant_years, credit, credit_amount, property_tax_assessed)
    elif incentive_number == 15: #Referred to as Incentive C9 in manuscript
        params = ('elec_eq', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        duration = 15
        credit_amount = 0.25 * elec_eq[start: start + duration] # DON'T MULTIPLY BY TAX RATE HERE
        credit = assess_incentive(start, duration, plant_years, credit, credit_amount, state_income_tax_assessed, 6.5e5)
    elif incentive_number == 16: #Referred to as Incentive C10 in manuscript
        params = ('state_income_tax_assessed',)
        check_any_missing_parameter(lcs, params)
        duration = 20
        credit_amount = 0.75 * state_income_tax_assessed[start: start + duration]# Credit amount depends on amount of state income tax assessed; DON'T MULTIPLY BY TAX RATE HERE
        credit = assess_incentive(start, duration, plant_years, credit, credit_amount, state_income_tax_assessed)
    elif incentive_number == 17: #Referred to as Incentive C11 in manuscript
        params = ('jobs_50', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        credit_amount = 500 * jobs_50 # Number of jobs paying 50k+/year; DON'T MULTIPLY BY TAX RATE HERE
        duration = 5
        credit = assess_incentive(start, duration, plant_years, credit, credit_amount, state_income_tax_assessed, 1.75e5)
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
    if incentive_number == 18: #Referred to as Incentive R1 (for "Refund 1") in manuscript
        params = ('IA_value', 'sales_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = 1
        refund_amount = sales_tax_rate * IA_value # Fees paid to (sub)contractors + cost of racks, shelving, conveyors
        refund = assess_incentive_arr(start, duration, plant_years, refund, refund_amount, sales_tax_assessed)
    elif incentive_number == 19: #Referred to as Incentive R2 in manuscript
        params = ('building_mats', 'sales_tax_rate')
        check_any_missing_parameter(lcs, params)
        duration = 1
        refund_amount = sales_tax_rate  * building_mats # Cost of building and construction materials
        refund = assess_incentive_arr(start, duration, plant_years, refund, refund_amount, sales_tax_assessed)
    elif incentive_number == 20: #Referred to as Incentive R3 in manuscript
        params = ('ethanol', 'state_income_tax_assessed')
        check_any_missing_parameter(lcs, params)
        duration = plant_years
        refund = assess_incentive_arr(start, duration, plant_years, refund, 0.2 * ethanol, state_income_tax_assessed,6e6)
        #DON'T MULTIPLY BY TAX RATE HERE
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
        Value added to property [$]. Assume similar to FCI.
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
