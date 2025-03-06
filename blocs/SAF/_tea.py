#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 16:38:37 2024

@author: wenjun
"""

from biosteam import TEA
import biosteam as bst
import thermosteam as tmo
from biorefineries.cornstover import CellulosicEthanolTEA



__all__ = ('SAF_TEA', 'create_SAF_tea')


class SAF_TEA(CellulosicEthanolTEA):
    def ___init__(self, system, IRR, duration, depreciation, income_tax,
                 operating_days, lang_factor, construction_schedule,
                 startup_months, startup_FOCfrac, startup_VOCfrac,
                 startup_salesfrac, WC_over_FCI,  finance_interest,
                 finance_years, finance_fraction, OSBL_units, warehouse,
                 site_development, additional_piping, proratable_costs,
                 field_expenses, construction, contingency,
                 other_indirect_costs, labor_cost, labor_burden,
                 property_insurance, maintenance, steam_power_depreciation,
                 boiler_turbogenerator, feedstock_trans_d, SAF_trans_d,
                 truck_CI, train_CI, RFS_credit, LCFS_credit):
        super().__init__(system, IRR, duration, depreciation, income_tax, operating_days, lang_factor, construction_schedule, \
                         startup_months, startup_FOCfrac, startup_VOCfrac, startup_salesfrac, WC_over_FCI, finance_interest, \
                         finance_years, finance_fraction, OSBL_units, warehouse, site_development, additional_piping, \
                         proratable_costs, field_expenses, construction, contingency, other_indirect_costs, labor_cost, \
                         labor_burden, property_insurance, maintenance, steam_power_depreciation, boiler_turbogenerator)
        self.feedstock_trans_d = feedstock_trans_d
        self.SAF_trans_d = SAF_trans_d
        self.truck_CI = truck_CI
        self.train_CI = train_CI
        self.RFS_credit = RFS_credit
        self.LCFS_credit = LCFS_credit
    _TCI_ratio_cached = 1




def create_SAF_tea(sys, OSBL_units=None):
    if OSBL_units is None: OSBL_units = bst.get_OSBL(sys.cost_units)
    try:
        BT = tmo.utils.get_instance(OSBL_units, (bst.BoilerTurbogenerator, bst.Boiler))
    except:
        BT = None
    SAF_tea = SAF_TEA(
        system=sys,
        IRR=0.10,  # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        duration=(2023, 2053),  # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        depreciation='MACRS7', 
        income_tax=0.35, # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        operating_days=0.9*365,  # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        lang_factor=None, 
        construction_schedule=(0.08, 0.60, 0.32),  # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        startup_months=3, 
        startup_FOCfrac=1, # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        startup_salesfrac=0.5, # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        startup_VOCfrac=0.75,  # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        WC_over_FCI=0.05,
        finance_interest=0.08, # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        finance_years=10,  # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        finance_fraction=0.4,
        OSBL_units=OSBL_units,
        warehouse=0.04, # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        site_development=0.09,  # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        additional_piping=0.045, # From 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks' (Ling Tao)
        proratable_costs=0.10, 
        field_expenses=0.10, 
        construction=0.20,
        contingency=0.10, 
        other_indirect_costs=0.10,
        labor_cost=2.4e6, # =90*0.9*365*24*33.64 more workers than 60 workers in 'Techno-economic analysis for upgrading the biomass-derived ethanol-to-jet blendstocks'(Ling Tao); 33.64 is employment cost of average 2023 from https://data.bls.gov/cgi-bin/srgate
        labor_burden=0.90,
        property_insurance=0.007, 
        maintenance=0.03,
        steam_power_depreciation='MACRS20',
        boiler_turbogenerator=BT,
        
        )
    return SAF_tea
