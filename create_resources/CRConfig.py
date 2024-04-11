#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 09:54:02 2024

@author: sdas
"""

##TO EDIT
caseNotesJSON="/home/sdas/cisco/moh_data/Final2/NUS_Case_Notes.json"
##TO EDIT
metadataJSON="/home/sdas/cisco/moh_data/Final2/NUS_Case_Metadata.json"




sr_key="sr"
tech_key = "Technology_Text__c"
subtech_key = "Sub_Technology_Text__c"
prod_name_key = "Product_Name__c"
sw_version_key = "SW_Version__c"
norm_swv_key = "Norm_SWV"
sourcefield_names="Customer_Symptom__c Description  Resolution_Summary__c".split()


###### Product Names and Software Version Lists specific, Only Metadata file 
##is used for the following
##TO EDIT
pname_tst_map_file="/tmp/tech_subtech_pnames.csv"
##TO EDIT
swv_tst_map_file="/tmp/tech_subtech_swv_norm2.csv"

SEPARATOR_TOKEN=" <> "


#Classifier specific

##TO EDIT
data_output_dir="/tmp"
fields=["Technology_Text__c", "Sub_Technology_Text__c", "Product_Name__c",\
       "SW_Version__c", "Customer_Symptom__c","Description","Resolution_Summary__c"]


#if these are known we use them while creating the "test" split for evaluation

list_goldSRs="" #694540632 695146873 695268540 \
#695443169 695503784 695545329 695571422 695579249 694571397 \
#695644022 694117912 695816345 694641874 694888348" 


