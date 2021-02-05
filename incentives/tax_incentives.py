#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tax Incentives
Authors: Dalton Stewart (dalton.w.stewart@gmail.com)
         Yoel Cortes-Pena (yoelcortes@gmail.com)

"""

# %%
import numpy as np
import pandas as pd
import os

__all__ = ('TaxIncentives', 'find_tax_incentive',
           'variable_incentives', 'fixed_incentives', 'mixed_incentives',
           'determine_state_credit_amount', 'determine_fed_credit_amount',
           'determine_state_refund_amount', 
           'determine_state_deduction_amount', 'determine_fed_deduction_amount',
           'determine_state_exemption_amount',
           'find_net_metering_parameters',
           'determine_net_metering_limit',
           'determine_net_metering_revenue')

folder = os.path.dirname(__file__)
xlfile = os.path.join(folder, 'State_Incentives.xlsx')
data = pd.read_excel(xlfile, index_col=[0])

def find_tax_incentive(state):
    incentive = data[state]
    return incentive

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

def mixed_incentives(durations, 
                     incentives, 
                     plant_years,
                     variable_incentive_frac_at_startup=1.0,
                     start=0):
    """
    Return a 2d array of incentive cashflows based on both fixed and 
    variable operation. Assume first incentive is fixed, and the rest are
    variable.
    """
    # First column is fixed incentive and the rest are variable.
    N_incentives = len(incentives)
    cashflow = np.zeros([plant_years, N_incentives])
    for i in range(N_incentives):
        cashflow[start: durations[i], i] = incentives[i] 
    cashflow[0, 1:] *= variable_incentive_frac_at_startup
    return cashflow


# %% Tax credit calculations
# plant_years: total plant duration in years
# variable_incentive_frac_at_startup

def determine_state_credit_amount(state, 
                                  plant_years,
                                  variable_incentive_frac_at_startup=1., 
                                  wages=0., 
                                  TCI=0., 
                                  ethanol=0.,
                                  state_income_tax=0., 
                                  jobs_50=0., 
                                  elec_eq=0.,
                                  construction_costs=0.,
                                  start=0,
                                  df=True):
    if state == 'AL': # Alabama
        state_credit_amount = 0.03*wages + 0.015*TCI
        duration = data.at['duration', 'AL']
        names = ['State credit']
        cashflows = variable_incentives([duration], [state_credit_amount], plant_years, variable_incentive_frac_at_startup, start)
    elif state == 'HI': # Hawaii
        eth_credit = 76100*(0.2/76000)*ethanol # Fuel content of ethanol is 76100 btu/gal
        duration = data.at['duration', 'HI']
        if eth_credit <= 3000000:
            state_credit_amount = eth_credit
        else:
            state_credit_amount = 3000000
        names = ['State credit']
        cashflows = variable_incentives([duration], [state_credit_amount], plant_years, variable_incentive_frac_at_startup, start)
    elif state == 'KY': # Kentucky
        duration1 = 15
        credit1 = state_income_tax
        ethanol_credit = 1 * ethanol # 1 $/gal ethanol * gal ethanol
        duration2 = plant_years
        if ethanol_credit <= 5000000:
            credit2 = ethanol_credit
        else:
            credit2 = 5000000
        names = ['Income tax credit','Ethanol credit']
        cashflows = mixed_incentives([duration1, duration2], [credit1, credit2],
                                     plant_years, variable_incentive_frac_at_startup,
                                     start)
    elif state == 'SC': # South Carolina
        fuels_duration = 7
        fuels_credit = 0.25*TCI/fuels_duration #credit must be taken in equal installments over duration
        elec_credit_calc = 0.25*elec_eq
        elec_duration = 15
        if elec_credit_calc <= 650000:
            elec_credit = elec_credit_calc
        else:
            elec_credit = 650000
        names = ['Fuels credit','Electricity credit']
        cashflows = fixed_incentives([fuels_duration, elec_duration],
                                     [fuels_credit, elec_credit],
                                     plant_years, start)    
    elif state == 'VA': # Virginia
        job_credit = 500*jobs_50
        duration = data.at['duration', 'VA']
        
        if job_credit <= 175000:
            state_credit_amount = job_credit
        else:
            state_credit_amount = 175000
        names = ['State credit']
        cashflows = fixed_incentives([duration], [state_credit_amount],
                                     plant_years, start)
    elif state == 'LA': # Louisiana
        duration = 1 # TODO: CHECK THIS
        if TCI < 100000:
            inv_credit = 0
        if 100000<=TCI<=300000:
            inv_credit = 0.07*TCI
        elif 300000<TCI<=1000000:
            inv_credit = 0.14*TCI
        elif TCI>1000000:
            inv_credit = 0.18*TCI
         
        sales_tax = 0.05    
        const_credit = 0.07*sales_tax/(1+sales_tax)*construction_costs #assume construction costs include tax
        
        grad_credit = 0.0072*sales_tax/(1+sales_tax)*construction_costs #assume construction costs include tax
            
        total_credit_amount = inv_credit + const_credit + grad_credit
        
        if total_credit_amount <= 1000000:
            state_credit_amount = total_credit_amount
        else:
            state_credit_amount = 1000000
        names = ['State credit']
        cashflows = fixed_incentives([duration], [state_credit_amount], 
                                     plant_years, start)
    elif state == 'CO': # Colorado
        credit_amount = 0.03*TCI
        duration = data.at['duration', 'CO']
        if credit_amount <= 750000:
            state_credit_amount = credit_amount
        else:
            state_credit_amount = 750000
        names = ['State credit']
        cashflows = fixed_incentives([duration], [state_credit_amount],
                                     plant_years, start)
    elif state == 'UT': # Utah
        state_credit_amount = 0.75*state_income_tax
        duration = data.at['duration', 'UT']
        names = ['State credit']
        cashflows = fixed_incentives([duration], [state_credit_amount],
                                     plant_years, start)
    else: # All other states
        names = ['State credit']
        cashflows = fixed_incentives([plant_years], [0.], 
                                     plant_years, start)
    if df: cashflows = pd.DataFrame(cashflows, columns=names)
    return cashflows
        
def determine_fed_credit_amount(plant_years, 
                                variable_incentive_frac_at_startup, 
                                ethanol=0.,
                                start=0,
                                df=True):
    if ethanol <= 15000000:
        fed_credit_amount = 1.01*ethanol
    else:
        fed_credit_amount = 1.01*15000000
    duration = plant_years
    cashflows = variable_incentives([duration], [fed_credit_amount],
                                    duration, variable_incentive_frac_at_startup,
                                    start)
    if df: cashflows = pd.DataFrame(cashflows, columns=['Federal credit'])
    return cashflows 
    
# %% Tax refund calculations
    
def determine_state_refund_amount(state, 
                                  plant_years, 
                                  variable_incentive_frac_at_startup, 
                                  ethanol=0., 
                                  subcontract_fees=0.,
                                  racks_etc=0.,
                                  construction_costs=0.,
                                  start=0,
                                  df=True):
    if state == 'MT': # Montana
        ethanol_refund = 0.2*ethanol
        duration = 6        
        if ethanol_refund <= 6e6:
            state_refund_amount = ethanol_refund
        else:
            state_refund_amount = 6e6
        cashflows = variable_incentives([duration], [state_refund_amount],
                                        plant_years, variable_incentive_frac_at_startup,
                                        start)
    elif state == 'IA': # Iowa
        duration = 1
        sales_tax = 0.05
        subcont_ref = sales_tax/(1+sales_tax)*subcontract_fees # Assume subcontractor fees include sales tax
        rack_ref = sales_tax/(1+sales_tax)*racks_etc # Assume value of racks, etc include sales tax
        state_refund_amount = subcont_ref + rack_ref
        cashflows = fixed_incentives([duration], [state_refund_amount], 
                                     plant_years, start)
    elif state == 'KY': # Kentucky
        duration = 1
        sales_tax = 0.05
        state_refund_amount = sales_tax/(1+sales_tax)*construction_costs # Assume construction costs include tax
        cashflows = fixed_incentives([duration], [state_refund_amount],
                                     plant_years, start)
    else: # All other states
        cashflows = fixed_incentives([plant_years], [0.], plant_years, start)
    if df: cashflows = pd.DataFrame(cashflows, columns=['State refund'])
    return cashflows
        
# %% Tax deduction calculations
       
def determine_state_deduction_amount(state, 
                                     plant_years,
                                     NM_value=0.,
                                     start=0,
                                     df=True):
    if state == 'NM': # New Mexico
        tax_rate = 0.05125 # NM compensating tax rate is 5.125%
        duration = plant_years
        state_deduction_amount = NM_value*tax_rate
        cashflows = fixed_incentives([duration], [state_deduction_amount], 
                                     plant_years, start)
    else: # All other states
        cashflows = fixed_incentives([plant_years], [0.], plant_years, start)
    if df: cashflows = pd.DataFrame(cashflows, columns=['State deduction'])
    return cashflows

# TODO: Note from Yoel: Something is fishy here, how does deduction translate 
# to tax credits? I don't things exemptions and deductions are cashflows.
def determine_fed_deduction_amount(plant_years,                             
                                   adj_basis=0.,
                                   start=0,
                                   df=True):
    tax_rate = 0.35 #federal income tax rate is 35%
    fed_deduction_amount = 0.5*adj_basis*tax_rate
    duration = 1
    cashflows = fixed_incentives([duration], [fed_deduction_amount], 
                                 plant_years, start)
    if df: cashflows = pd.DataFrame(cashflows, columns=['Federal deduction'])
    return cashflows

#%% Tax exemption calculations

def determine_state_exemption_amount(state, 
                                     plant_years, 
                                     variable_incentive_frac_at_startup,
                                     value_add=0.,
                                     ethanol_eq = 0., 
                                     state_property_tax=0.,
                                     airq_taxes=0., 
                                     fuel_mix_eq=0., 
                                     biodiesel_eq=0.,
                                     ethanol=0.,
                                     start=0,
                                     df=True):
    if state == 'IA': # Iowa
        state_exemption_amount = value_add * 0.05 #TODO: check IA property tax rate, assuming 5%
        duration = 20
        cashflows = fixed_incentives([duration],[state_exemption_amount],
                                     plant_years, start)
    elif state == 'MT': # Montana
        tax_rate = 3.2/100 # MT effective property tax rate was 3.2% in 2019
        state_exemption_amount = ethanol_eq * tax_rate
        duration = 10
        cashflows = fixed_incentives([duration],[state_exemption_amount], 
                                     plant_years, start)
    elif state == 'OH': # Ohio    
        state_exemption_amount = airq_taxes * 0.05 #TODO: check OH property tax rate, assuming 5%
        duration = 1
        cashflows = fixed_incentives([duration],[state_exemption_amount], 
                                     plant_years, start)
    elif state == 'KS': # Kansas
        duration = 10
        equip_ex = fuel_mix_eq * 0.05 #TODO: check KS property tax rate, assuming 5%
        ptax_ex = state_property_tax
        state_exemption_amount = equip_ex + ptax_ex
        cashflows = fixed_incentives([duration],[state_exemption_amount], 
                                     plant_years, start)
    elif state == 'MI': # Michigan
        state_exemption_amount = biodiesel_eq * 0.05 #TODO: check MI property tax rate, assuming 5%
        duration = plant_years
        cashflows = fixed_incentives([duration],[state_exemption_amount], 
                                     plant_years, start)
    elif state == 'NE': # Nebraska
        tax_rate = 33.2/100 # NE fuel tax rate is 33.2 cents per gallon
        state_exemption_amount = ethanol * tax_rate
        duration = plant_years
        cashflows = variable_incentives([duration],[state_exemption_amount], 
                                        plant_years, variable_incentive_frac_at_startup, 
                                        start)
    elif state == 'OR': # Oregon
        state_exemption_amount = state_property_tax
        duration = plant_years
        cashflows = fixed_incentives([duration],[state_exemption_amount], 
                                     plant_years, start)
    else: # All other states
        cashflows = fixed_incentives([plant_years], [0.], plant_years, start)
    if df: cashflows = pd.DataFrame(cashflows, columns=['State exemption'])
    return cashflows
  
#%% Net Metering calculations
# Data
import pandas as pd
import os

folder = os.path.dirname(__file__)
xlfile = os.path.join(folder, 'State_Parameters.xlsx')
nm_data = pd.read_excel(xlfile, index_col=[0])


# Define functions

def find_net_metering_parameters(state):
    nm_state_data = nm_data[state]
    return nm_state_data

def determine_net_metering_limit(L, L_mult, U, OH):
    U_avg = U/OH # U_avg: average electricity use in operating year (kW)
    limit = L + L_mult * U_avg # System capacity limit. May be set number or depend on biorefinery use (U).
    return limit

# TODO: Note from Yoel: rate_w is ignored when G_avg <= limit. Might want to 
# add a few more comments as to why.
def determine_net_metering_revenue(plant_years, G, OH, limit, rate, rate_w, 
                                   variable_incentive_frac_at_startup=1., start=0, df=True):
    # OH: operating hours, number of hours plant operates per year (hr/yr)
    duration = plant_years
    G_avg = G / OH #average system capacity in operating year (kW)
    if G_avg <= limit:
        net_metering_rev = G * rate
        cashflows = variable_incentives([duration], [net_metering_rev],
                                        plant_years, start) 
    else:
        net_metering_rev = limit * OH * rate
        extra_rev = (G - (limit * OH)) * rate_w
        total_rev = net_metering_rev + extra_rev
        cashflows = variable_incentives([duration], [total_rev], plant_years, 
                                        variable_incentive_frac_at_startup, start)  
    if df: cashflows = pd.DataFrame(cashflows, columns=['Net metering'])
    return cashflows

#%% New/fake incentives calculations
# If you don't want to simulate existing incentives or want to supplement existing incentives.

# TODO: Note from Yoel: I would suggest to remove the 'parameters' and 'multipliers
# arguments in favor of a 'incentives' argument that is an array of incentives.

# def incentives_calc(parameters, multipliers):
#     incentive = parameters*multipliers
#     return incentive

# def incentives_values(names,                
#                    parameters,
#                    multipliers):
   
#     incentives = []
#     for i in range(len(names)):
#         incentives.append(incentives_calc(parameters[i], multipliers[i]))
#     return incentives

# def new_incentives(names,
#                    durations, 
#                    parameters,
#                    multipliers,
#                    plant_years, 
#                    variable_incentive_frac_at_startup=1.0):
#     incentives = incentives_values(names, parameters, multipliers)    
#     return mixed_incentives(names, durations, incentives, plant_years, variable_incentive_frac_at_startup)

#%% Define class
class TaxIncentives:
    """
    Creates a TaxIncentives object which represents cashflows from various tax incentives.
    The DataFrame output from this TaxIncentives object is meant to be included in a TEA 
    object to assess the effect of tax incentives on biorefinery economics. A TaxIncentives 
    object may be used to simulate existing (as of September 2020) incentives in the United 
    States collected from the Database of State Incentives for Renewables and Efficiency (DSIRE) 
    and the Alternative Fuels Data Center (AFDC). If you would like to simulate new or theoretical
    incentives, please use a NewTaxIncentives object instead. 
    
    Parameters necessary to simulate an incentive vary with each incentive, but the US state
    (two letter abbreviation), state; number of years the plant will be operational, plant_years;
    and the fraction of variable costs at startup, variable_incentive_frac_at_startup, must always
    be specified. If you do not know which parameters you need to specify, please use the 
    find_tax_incentives method to find tax incentives parameters and the find_net_metering_parameters 
    method to find net metering parameters for the state you wish to simulate. There are two federal 
    incentives available in all states that require the amount of ethanol produced by the biorefinery 
    [gal/year], ethanol, and adjusted basis of biorefinery property [USD], adj_basis, so it is 
    recommended that you always specify these parameters as well.
    
    If you wish to simulate participation in net metering program, you will always need to specify
    the amount of electricity generated by the biorefinery per year [kWh], elec_gen; the amount of 
    electricity consumed from the grid by the biorefinery per year [kWh], elec_use; and the number
    of hours per year the biorefinery is operational, op_hours. If you do not know which parameters 
    you need to specify, please use the 
    find_tax_incentives method to find tax incentives parameters and the find_net_metering_parameters 
    method to find net metering parameters for the state you wish to simulate.
    
    Parameters
    ----------
    state: string 
        US state you wish to simulate (two letter abbreviation), ex) 'IL'
    
    plant_years: int
        number of years the plant will be operational
    
    variable_incentive_frac_at_startup: float
        fraction of variable costs occuring in first year of operation
    
    wages: int, optional depending on incentive
        total wages paid to all plant workers [USD/year] 
    
    TCI: int, optional depending on incentive
        total capital investment [USD] 
    
    ethanol: int
        amount of ethanol produced by biorefinery [gal/year]
        
    state_income_tax: int, optional depending on incentive
        amount of state income tax assessed on biorefinery income [USD/year]
        
    jobs_50: int, optional depending on incentive
        number of biorefinery jobs paying at least 50,000 USD/year
        
    # TODO: Is this the installation cost of units (not including purchase cost)
    # or is it the installed equipment cost? I'm assuming you meant the 
    # installed equipment cost (which includes purchase costs)
    elec_eq: int, optional depending on incentive
        installation cost of equipment used by biorefinery to generate electricity [USD]
        
    construction_costs: int, optional depending on incentive
        total biorefinery construction costs [USD]
        
    subcontract_fees: int, optional depending on incentive
        total amount paid to contractors and subcontractors during construction [USD]
        
    racks_etc: int, optional depending on incentive
        value of all racks, shelving, and conveyors within biorefinery [USD]
        
    NM_value: int, optional depending on incentive
        value of a biomass boiler, gasifier, furnace, turbine-generator, storage
        facility, feedstock processing or drying equipment, feedstock trailer or 
        interconnection transformer, and the value of biomass materials [USD]
    
    adj_basis: int
        adjusted basis of biorefinery property [USD]
        
    value_add: int, optional depending on incentive
        value added to property by biorefinery [USD]
        
    state_property_tax: int, optional depending on incentive
        amount of state property tax assessed on biorefinery property [usd/year]
        
    airq_taxes: int, optional depending on incentive
        amount of sales and use tax paid on equipment for air quality projects [USD]
        
    fuel_mix_eq: int, optional depending on incentive
        value of equipment used to mix biofuels with fossil fuels [USD]
        
    biodiesel_eq: int, optional depending on incentive
        value of equipment used to produce biodiesel [USD]
        
    ethanol_eq: int, optional depending on incentive
        value of equipment used to produce ethanol [USD]
        
    elec_use: int, optional if not simulating net metering
        amount of electricity used by biorefinery from grid [kWh/year]
        
    elec_gen: int, optional if not simulating net metering
        amount of electricity produced by biorefinery [kWh/year]
        
    op_hours: int, optional if not simulating net metering
        number of hours biorefinery operates per year
        
    L: int, optional if not simulating net metering
        electricity generating system capacity limit [kW]
        Note: you should only input a numerical value for L or L_mult, not both. The other should be 0.
        
    L_mult: float, optional if not simulating net metering
        multiplied by biorefinery's electricity use to determine electricity system capacity limit
        Note: you should only input a numerical value for L or L_mult, not both. The other should be 0.
        
    rate: float, optional if not simulating net metering
        the retail rate at which electricity is bought and sold [USD/kWh]
        
    rate_w: float, optional if not simulating net metering
        the wholesale rate at which electricity is bought and sold [USD/kWh]
    
    start : int, optional
        First year after construction.
        
    Examples
    --------
    Simulate tax incentives available for a biorefinery located in Illinois. The biorefinery will
    operate for 20 years and the variable startup fraction is 0.75. The biorefinery operates
    for 2400 hours per year and produces 10e6 gal/year of ethanol and 10e7 kWh/year of electricity, and
    consumes 10e5 kWh/year of electricity from the grid. The adjusted basis of biorefinery property
    is 2e6 USD.
    
    >>> ILtax = TaxIncentives('IL',
    ...                       20,
    ...                       0.75,
    ...                       op_hours=2400,
    ...                       ethanol=10e6,
    ...                       adj_basis=2e6,
    ...                       elec_gen=10e7,
    ...                       elec_use=10e5,
    ...                       rate_w=.02)
    
    >>> ILtax.find_tax_incentives()
    State
    incentive                                                              --
    state credit parameters                                                --
    state refund parameters                                                --
    state deduction parameters                                             --
    state exemption parameters                                             --
    max                                                                    --
    duration                                                               --
    federal credit parameters                                              --
    max                                                                    --
    fedc_duration                                                          --
    federal deduction parameters    adj_basis (adjusted basis of property, $)
    max                                                                    --
    fedd_duration                                                           1
    Name: IL, dtype: object
    
    Note that there are no state-level tax incentives available in Illinois.
     
    >>> ILtax.load_net_metering_parameters()
    >>> df_incentives = ILtax.calc_all_tax_incentives()
    >>> df_incentives['Federal credit']
    0      7575000.0
    1     10100000.0
    2     10100000.0
    3     10100000.0
    4     10100000.0
    5     10100000.0
    6     10100000.0
    7     10100000.0
    8     10100000.0
    9     10100000.0
    10    10100000.0
    11    10100000.0
    12    10100000.0
    13    10100000.0
    14    10100000.0
    15    10100000.0
    16    10100000.0
    17    10100000.0
    18    10100000.0
    19    10100000.0
    Name: Federal credit, dtype: float64
    
    """
    
    def __init__(self, 
                 state,
                 plant_years, 
                 variable_incentive_frac_at_startup,
                 wages=0., 
                 TCI=0., 
                 ethanol=0.,
                 state_income_tax=0., 
                 jobs_50=0., 
                 elec_eq=0.,
                 construction_costs=0., 
                 subcontract_fees=0.,
                 racks_etc=0., 
                 NM_value=0., 
                 adj_basis=0.,
                 value_add=0., 
                 state_property_tax=0., 
                 airq_taxes=0.,
                 fuel_mix_eq=0., 
                 biodiesel_eq=0., 
                 ethanol_eq=0.,
                 elec_use=0.,
                 elec_gen=0.,
                 op_hours=1.,
                 L=0.,
                 L_mult=0.,
                 rate=0.,
                 rate_w=0.,
                 start=0):
        self.state = state
        self.plant_years = plant_years
        self.variable_incentive_frac_at_startup = variable_incentive_frac_at_startup
        self.wages = wages
        self.TCI = TCI
        self.ethanol = ethanol
        self.state_income_tax = state_income_tax
        self.jobs_50 = jobs_50
        self.elec_eq = elec_eq
        self.construction_costs = construction_costs
        self.subcontract_fees = subcontract_fees
        self.racks_etc = racks_etc
        self.NM_value = NM_value
        self.adj_basis = adj_basis
        self.value_add = value_add
        self.state_property_tax = state_property_tax
        self.airq_taxes = airq_taxes
        self.fuel_mix_eq = fuel_mix_eq
        self.biodiesel_eq = biodiesel_eq
        self.ethanol_eq = ethanol_eq
        self.elec_use = elec_use
        self.elec_gen = elec_gen
        self.op_hours = op_hours
        self.L = L
        self.L_mult = L_mult
        self.rate = rate
        self.rate_w = rate_w
        self.start = start

    def find_tax_incentives(self):
        return find_tax_incentive(self.state)

    def calc_fed_credit(self, df=True):
        return determine_fed_credit_amount(self.plant_years,
                                           self.variable_incentive_frac_at_startup, 
                                           self.ethanol,
                                           self.start,
                                           df)

    def calc_fed_deduction(self, df=True):
        return determine_fed_deduction_amount(self.plant_years,
                                              self.adj_basis,
                                              self.start,
                                              df)  

    def calc_state_credit(self, df=True):
        return determine_state_credit_amount(self.state, 
                                             self.plant_years,
                                             self.variable_incentive_frac_at_startup, 
                                             self.wages, 
                                             self.TCI, 
                                             self.ethanol,
                                             self.state_income_tax, 
                                             self.jobs_50, 
                                             self.elec_eq, 
                                             self.construction_costs,
                                             self.start,
                                             df)
        
    def calc_state_refund(self, df=True):
        return determine_state_refund_amount(self.state, 
                                             self.plant_years,
                                             self.variable_incentive_frac_at_startup, 
                                             self.ethanol, 
                                             self.subcontract_fees,
                                             self.racks_etc,
                                             self.construction_costs,
                                             self.start,
                                             df)

    def calc_state_deduction(self, df=True):
        return determine_state_deduction_amount(self.state,
                                                self.plant_years,
                                                self.NM_value,
                                                self.start,
                                                df)

    def calc_state_exemption(self, df=True):
        return determine_state_exemption_amount(self.state, 
                                                self.plant_years,
                                                self.variable_incentive_frac_at_startup,
                                                self.value_add, 
                                                self.state_property_tax,
                                                self.airq_taxes, 
                                                self.fuel_mix_eq, 
                                                self.biodiesel_eq,
                                                self.ethanol_eq,
                                                self.start,
                                                df)

    def find_net_metering_parameters(self):
        return find_net_metering_parameters(self.state)
    
    def load_net_metering_parameters(self):
        self.L, self.L_mult, self.rate, self.rate_w = self.find_net_metering_parameters()
    
    def calc_net_metering(self, df=True):         
        limit = determine_net_metering_limit(self.L, 
                                             self.L_mult, 
                                             self.elec_use,
                                             self.op_hours)
        return determine_net_metering_revenue(self.plant_years, 
                                              self.elec_gen,
                                              self.op_hours, 
                                              limit, 
                                              self.rate,
                                              self.rate_w,
                                              self.variable_incentive_frac_at_startup, 
                                              self.start,
                                              df)
    def calc_all_tax_incentives(self, df=True, include_federal=True):
        if include_federal:
            incentives = [
                self.calc_fed_credit(df),
                self.calc_fed_deduction(df),
                self.calc_state_credit(df),
                self.calc_state_refund(df),
                self.calc_state_deduction(df),
                self.calc_state_exemption(df),
            ]
        else:
            incentives = [
                self.calc_state_credit(df),
                self.calc_state_refund(df),
                self.calc_state_deduction(df),
                self.calc_state_exemption(df),
            ]
        if df:
            overall_cashflow = incentives[0].join(
                [i for i in incentives[1:] if i is not None]
            )
        else:
            overall_cashflow = sum([i.sum(1) for i in incentives if i is not None])
        return overall_cashflow

# TODO: Note from Yoel: This class still doesn't give enough freedome to calculate
# incentives. I would sugest creating an "AbstractTaxIncentives" class
# for the user to inherit and must implement a method that serves as a hook 
# to calculate incentives.

# class AbstractTaxIncentives:
#     """
#     Creates a AbstractTaxIncentives object which represents cashflows from various tax incentives.
#     The DataFrame output from this AbstractTaxIncentives object is meant to be included in a TEA 
#     object to assess the effect of tax incentives on biorefinery economics. An AbstractTaxIncentives 
#     object may be used to simulate new or theoretical incentives. If you would like to simulate
#     incentives that already exist in the United States, please use a TaxIncentives object instead.
   
#     Note: even if you only wish to simulate one incentive, you must input names, durations, parameters, and
#     multipliers formatted as a list, i.e. [name] or [name1, name2]
   
    
#    Parameters
#    ----------
#    names: list of strings
#        the names of the incentives you are simulating
       
#    durations: list of ints
#        the durations of the incentives you are simulating [years]
       
#    parameters: list of ints
#        the value of material/energy/cash flow that will determine the value of your incentive
#        ex) for an ethanol incentive your parameter might be 1e6 (the number of gal/year of ethanol produced)
#        Note: the units of your parameter should cancel the units of your multiplier so you end with USD/year 
       
#    multipliers: list of ints or floats
#        the amount the parameter is multiplied by to determine the value of the incentive
#        ex) for an ethanol incentive of 1 USD/gal, your multiplier will be 1.0
#        Note: the units of your multiplier should cancel the units of your parameter so you end with USD/year 
   
#    plant_years: int
#         number of years the plant will be operational
    
#    variable_incentive_frac_at_startup: float
#         fraction of variable costs occuring in first year of operation
    
        
#    Examples
#    --------
#     Simulate two theoretical incentives to assess their combined potential impact on biorefinery economics.
#     The first is a 25% refund of your total capital investment (TCI) during the first year of biorefinery 
#     operation. The second is an ethanol incentive payment of 5 USD/gal of ethanol produced for the
#     entire lifetime of the biorefinery. The biorefinery generates 1e6 gal/year of ethanol and the the TCI 
#     is 4e6 USD. The biorefinery will operate for 20 years and the variable startup fraction is 0.75.
    
#     >>> import incentives as ti
    
#     >>> newtax = NewTaxIncentives(['TCI Refund', 'Crazy Ethanol Payment'],
#                                   [1,20],
#                                   [4e6,1e6],
#                                   [.25,5],
#                                   20,
#                                   0.75)
    
#     >>> newtax.calc_all_incentives()
    
#     >>> newtax.overall_cashflow
#             TCI Refund  Crazy Ethanol Payment
#         0    1000000.0              3750000.0
#         1          0.0              5000000.0
#         2          0.0              5000000.0
#         3          0.0              5000000.0
#         4          0.0              5000000.0
#         5          0.0              5000000.0
#         6          0.0              5000000.0
#         7          0.0              5000000.0
#         8          0.0              5000000.0
#         9          0.0              5000000.0
#         10         0.0              5000000.0
#         11         0.0              5000000.0
#         12         0.0              5000000.0
#         13         0.0              5000000.0
#         14         0.0              5000000.0
#         15         0.0              5000000.0
#         16         0.0              5000000.0
#         17         0.0              5000000.0
#         18         0.0              5000000.0
#         19         0.0              5000000.0
      
#     """
    
#     def __init__(self,
#                  names,
#                  durations, 
#                  parameters,
#                  multipliers,
#                  plant_years, 
#                  variable_incentive_frac_at_startup=1.0):
        
#         self.names = names
#         self.durations = durations
#         self.parameters = parameters
#         self.multipliers = multipliers
#         self.plant_years = plant_years
#         self.variable_incentive_frac_at_startup = variable_incentive_frac_at_startup
        
#     def calc_all_incentives(self):
#         self.new_incentives = new_incentives(self.names,
#                                              self.durations,
#                                              self.parameters,
#                                              self.multipliers,
#                                              self.plant_years,
#                                              self.variable_incentive_frac_at_startup)
        
#         self.overall_cashflow = self.new_incentives
      

#csv_data = tax.overall_cashflow.to_csv('ocf.csv', index = True)
# pd.set_option('display.max_rows', 500)
# pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)       
