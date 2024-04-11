#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 13:25:19 2023

@author: sdas
"""

import json 
import csv
import re
import CRConfig as config
import Matcher as matcher

SWV_PATTERN = re.compile(r'(([0-9-]+){1,4}([0-9]+[a-zA-Z]{0,2}))')


def extractVersion(swv):    
    
    norm_swv = swv.replace(".","-").replace(")","-").replace("(","-").strip()

    flag=False
    predwds = norm_swv.strip()
    predwds = predwds.split("-")
    predIsNum = matcher.isNumericOnly(predwds)
    #print (swv+" "+str(predIsNum)+" is numeric flag")
    new_swv=""
    if predIsNum:
        # print ("NUMERIC "+swv+" "+norm_swv)
        new_swv = norm_swv.replace("-",".")
        if new_swv.endswith("."):
            new_swv = new_swv[0:len(new_swv)-1]
        if new_swv.startswith("."):
            new_swv = new_swv[1:len(new_swv)]
        
    else:
        predIsText = matcher.noNumeric(swv)
        if predIsText:
            # print ("TEXT ONLY"+ swv)
            new_swv =  swv
        else:
            temp=[]
            
            for m in re.finditer(SWV_PATTERN, norm_swv):
                temp.append(norm_swv[m.start():m.end()])
                
            #print (norm_swv)
            maxm=""
            #print (type(temp))
            for m in temp:
                
                if len(m)>len(maxm):
                    maxm = m
                    
            print ("MIXED "+swv+"\t"+norm_swv+"\t"+maxm)
            
            if not maxm.startswith("-"):
                print ("DEBUG CHECK CASE "+maxm)
                tempw = norm_swv.split()
                m=""
                for w in tempw:
                    if w.startswith(maxm):
                        flag=False
                        m=w
                        break
                if m=="":
                    print ("setting flag to true "+str(tempw)+" "+maxm)
                    flag=True
                
                    
            new_swv = maxm.replace("-",".")
            if new_swv.endswith("."):
                new_swv = new_swv[0:len(new_swv)-1]
            if new_swv.startswith("."):
                new_swv = new_swv[1:len(new_swv)]
            
    
  
    print (norm_swv+" Extracted= "+new_swv)
    if new_swv=="":
        return swv, True
    
    return new_swv, flag


if __name__=="__main__":

    
    nus_meta=None
    with open (config.metadataJSON, "r") as f:
        nus_meta = json.loads(f.read())
    
    f.close()
    
    print ("#SR casemeta: "+str(len(nus_meta)))
    
    
    SEPARATOR_TOKEN=config.SEPARATOR_TOKEN
    
    
        
        
    pncounts={}
    swvcounts={}
    
    for mx, mobj in enumerate(nus_meta):
    
        if config.sr_key in mobj: #mx<5:
            srid = mobj['sr'].strip()
            
            if config.tech_key not in mobj or mobj[config.tech_key] is None:
                continue
            if config.subtech_key not in mobj or mobj[config.subtech_key] is None:
                continue
            
            key = mobj[config.tech_key]+SEPARATOR_TOKEN+mobj[config.subtech_key]
            
            val=""
            if config.prod_name_key in mobj and mobj[config.prod_name_key] is not None:
                val = mobj[config.prod_name_key].strip()
                if val!="":
                    if key not in pncounts:
                        pncounts[key] = {}
                    if val not in pncounts[key]:
                        pncounts[key][val]=0
                    pncounts[key][val] += 1
            
            val=""
            if config.sw_version_key in mobj and mobj[config.sw_version_key] is not None:
                val = mobj[config.sw_version_key].strip()
                if val!="":
                    if key not in swvcounts:
                        swvcounts[key] = {}
                    if val not in swvcounts[key]:
                        swvcounts[key][val]=0
                    swvcounts[key][val] += 1
    
    
    fout = open (config.pname_tst_map_file, "w")
    
    
    csvw = csv.writer(fout, delimiter=',',
                        quotechar='"', quoting=csv.QUOTE_ALL)
    
    header=[config.tech_key, config.subtech_key, config.prod_name_key, "COUNT"]
    
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
    
    fout = open (config.swv_tst_map_file, "w")
    
    
    csvw = csv.writer(fout, delimiter=',',
                        quotechar='"', quoting=csv.QUOTE_ALL)
    
    header=[config.tech_key, config.subtech_key, config.sw_version_key,\
            config.norm_swv_key, "COUNT", "ManualCheck"]
    
    csvw.writerow(header)
    
    count=0
    for key in swvcounts:
        
        pngroup = swvcounts[key]
        
        for ele in pngroup:
            norm_ele, flag = extractVersion(ele)
            row=[key.split(SEPARATOR_TOKEN)[0], 
                 key.split(SEPARATOR_TOKEN)[1],
                 ele, norm_ele, pngroup[ele], flag
                 ]
            csvw.writerow(row)
            count += 1
            fout.flush()
            
    print ("#swv count="+str(count))
    fout.close()
    
    print ("##############################")
    print ("Product Names/Software Version Lists written to ")
    print (config.pname_tst_map_file)
    print (config.swv_tst_map_file)
    