#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 14:32:56 2024

@author: sdas
"""


metadata_jsonf="/home/mouad/sujatha_code/data/NUS_Case_Metadata.json"


outdir="/home/mouad/sujatha_code/data"
pname_lists_file = outdir+"/tech_subtech_pnames.csv"
swv_lists_file = outdir+"/tech_subtech_swv.csv"

SEPARATOR_TOKEN=" <> "
SR_KEY="sr"
TECH_FIELD_KEY="Technology_Text__c"
SUBTECH_FIELD_KEY="Sub_Technology_Text__c"
SW_FIELD_KEY="SW_Version__c"
PN_FIELD_KEY="Product_Name__c"
