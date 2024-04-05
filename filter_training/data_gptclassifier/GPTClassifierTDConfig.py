#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 12:56:07 2024

@author: sdas
"""

gold_csv_file="gold_data.csv"


metadata_json_file="/home/mouad/sujatha_code/data/NUS_Case_Metadata.json"
casenotes_json_file="/home/mouad/sujatha_code/data/NUS_Case_Notes.json"
tst_swv_mapfile="/home/mouad/sujatha_code/data/tech_subtech_swv_norm2.csv"
output_dir="/home/mouad/sujatha_code/tmp"
SEPARATOR_TOKEN=" <> "


sr_key="sr"
tech_key = "Technology_Text__c"
subtech_key = "Sub_Technology_Text__c"
prod_name_key = "Product_Name__c"
sw_version_key = "SW_Version__c"
sourcefield_names="Customer_Symptom__c Description  Resolution_Summary__c".split()

fields=["Technology_Text__c", "Sub_Technology_Text__c", "Product_Name__c",\
       "SW_Version__c", "Customer_Symptom__c","Description","Resolution_Summary__c"]

#map to above entries in gold_csv
srcolid=0
ptechid=1
psubtechid=2
pnameid=3
swvid=4
srcids=[5, 6, 7]
    
    
    
goodlist="694540632 695146873 695268540 \
695443169 695503784 695545329 695571422 695579249 694571397 \
695644022 694117912 695816345 694641874 694888348".split()
