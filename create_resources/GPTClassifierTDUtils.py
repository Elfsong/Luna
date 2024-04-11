#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 13:01:27 2024

@author: sdas
"""

import csv 
import json
import CRConfig as config
from Matcher import matchSWStrings


def loadTST_SWVMap(inpfile, sep_token):

    rx = 0
    header=[]
    
    pnmap={}
    r_pnmap={}
    
    with open (inpfile, "r") as fin:
        csvreader = csv.reader(fin, delimiter=",", quotechar='"')
        for row in csvreader:
            rx += 1
            if rx==1:
                header = row
                continue
            
            
            
            tech_text = row[header.index(config.tech_key)]
            subtech_text = row[header.index(config.subtech_key)]
            swv = row[header.index(config.norm_swv_key)]
            
            key = tech_text+config.SEPARATOR_TOKEN+subtech_text
            
            if key not in pnmap:
                pnmap[key]=[]
            
            if swv=="":
                continue
            
            prevlabels=pnmap[key]
            seen=False
            for label in prevlabels:
                if matchSWStrings(swv, label):
                    print ("Match found for pair ("+swv+", "+label+")")
                    seen=True
                    break
            if not seen:
                pnmap[key].append(swv)
                
                
    return header, pnmap, r_pnmap


def loadCaseNotes(inpjsonf):
    # print ("#case notes: "+str(len(case_notes)))
    
    case_notes=None
    with open (inpjsonf, "r") as f:
        case_notes = json.loads(f.read())
    
    f.close()
    
    print (case_notes[0].keys())
    sr_cn={}
    ntypes={}
    xc=0
    for cobj in case_notes:
        if 'extracted_note' not in cobj:
            ext_note=""
        else:
            ext_note=cobj['extracted_note']
            xc += 1
        
        if 'NoteType__c' in cobj:
            nt = cobj['NoteType__c'].lower().strip()
            
            if nt not in ntypes:
                ntypes[nt]=0
            ntypes[nt]+=1
         
        # if "email" not in nt.lower():
        #     continue
        srid = cobj['sr'].strip()
        
        if srid not in sr_cn:
            sr_cn[srid]=[]
            
        
        sr_cn[srid].append((nt, cobj['CreatedDate'], cobj['Note__c'], ext_note))

    print("DEBUG CaseNotes Types\n"+str(ntypes))
    
    return sr_cn
