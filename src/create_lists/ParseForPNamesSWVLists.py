#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 13:25:19 2023

@author: sdas
"""
import sys
import json 
import random
import csv
import ParseListsConfig as config



nus_meta=None
with open (config.metadata_jsonf, "r") as f:
    nus_meta = json.loads(f.read())

f.close()

print ("#SR casemeta: "+str(len(nus_meta)))


SEPARATOR_TOKEN=config.SEPARATOR_TOKEN
tech_key = config.TECH_FIELD_KEY
subtech_key = config.SUBTECH_FIELD_KEY
prod_name_key = config.PN_FIELD_KEY
sw_version_key = config.SW_FIELD_KEY


    
    
pncounts={}
swvcounts={}

for mx, mobj in enumerate(nus_meta):

    if "sr" in mobj: #mx<5:
        srid = mobj['sr'].strip()
        
        if tech_key not in mobj or mobj[tech_key] is None:
            continue
        if subtech_key not in mobj or mobj[subtech_key] is None:
            continue
        
        key = mobj[tech_key]+SEPARATOR_TOKEN+mobj[subtech_key]
        
        val=""
        if prod_name_key in mobj and mobj[prod_name_key] is not None:
            val = mobj[prod_name_key].strip()
            if val!="":
                if key not in pncounts:
                    pncounts[key] = {}
                if val not in pncounts[key]:
                    pncounts[key][val]=0
                pncounts[key][val] += 1
        
        val=""
        if sw_version_key in mobj and mobj[sw_version_key] is not None:
            val = mobj[sw_version_key].strip()
            if val!="":
                if key not in swvcounts:
                    swvcounts[key] = {}
                if val not in swvcounts[key]:
                    swvcounts[key][val]=0
                swvcounts[key][val] += 1


fout = open (config.pname_lists_file, "w")


csvw = csv.writer(fout, delimiter=',',
                    quotechar='"', quoting=csv.QUOTE_ALL)

header=[tech_key, subtech_key, prod_name_key, "COUNT"]

csvw.writerow(header)

count=0
for key in pncounts:
    
    pngroup = pncounts[key]
    
    for ele in pngroup:
        row=[key.split(SEPARATOR_TOKEN)[0], 
             key.split(SEPARATOR_TOKEN)[1],
             ele, pngroup[ele]
             ]
        count += 1
        csvw.writerow(row)
        fout.flush()
        
fout.close()
print ("#pn count="+str(count))

fout = open (config.swv_lists_file, "w")


csvw = csv.writer(fout, delimiter=',',
                    quotechar='"', quoting=csv.QUOTE_ALL)

header=[tech_key, subtech_key, sw_version_key, "COUNT"]

csvw.writerow(header)

count=0
for key in swvcounts:
    
    pngroup = swvcounts[key]
    
    for ele in pngroup:
        row=[key.split(SEPARATOR_TOKEN)[0], 
             key.split(SEPARATOR_TOKEN)[1],
             ele, pngroup[ele]
             ]
        csvw.writerow(row)
        count += 1
        fout.flush()
        
print ("#swv count="+str(count))
fout.close()