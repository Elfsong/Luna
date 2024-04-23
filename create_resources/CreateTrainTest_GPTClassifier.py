#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 11:33:53 2024

@author: sdas
"""
import json
import csv
import sys
import random 
import CRConfig as config
from Matcher import matchSWStrings, edmatch
from GPTClassifierTDUtils import loadCaseNotes, loadTST_SWVMap


tr_opfile=config.data_output_dir+"/train.csv"
ts_opfile=config.data_output_dir+"/test.csv"


data = json.load(open (config.metadataJSON, "r"))
cndata_file = config.caseNotesJSON
rows=[]
rowhead=[config.sr_key]

rowids=[0]
for field in config.fields:
    rowhead.append(field)
    rowids.append(len(rowids))
    


for ele in data:
    row=[ele[config.sr_key]]
    for field in config.fields:
        if field in ele:
            if ele[field] is None:
                #print (field+" is None for "+ele[config.sr_key])
                break            
            row.append(ele[field])
        else:
            #print (field+" not found for "+ele[config.sr_key])
            break
    
    if len(row)==len(config.fields)+1: #for SR
        rows.append(row)
        

    
print ("#rows="+str(len(rows)))

goldsrs=[]

if config.list_goldSRs!="":
    goldsrs = config.list_goldSRs.split()
        
print ("gold len(srids)="+str(len(goldsrs)))

sr_cn = loadCaseNotes(cndata_file)
print ("len(sr_cn)="+str(len(sr_cn)))


cp = csv.reader(open(config.pname_tst_map_file, "r"))

csvr = csv.reader(open(config.swv_tst_map_file, "r"))
header = {}
swv2nswv={}
for row in csvr:
    if len(header)==0:
        for rx, rele in enumerate(row):
            header[rele]=rx
        print (header)
        continue
    else:
        swv = row[header[config.sw_version_key]]
        nswv = row[header[config.norm_swv_key]]
        swv2nswv[swv.strip()] = nswv.strip()

header2 = {}
ts2p={}
for row in cp:
    if len(header2)==0:
        for rx, rele in enumerate(row):
            header2[rele]=rx
        print (header2)
        continue
    else:
        tech = row[header2[config.tech_key]]
        sub_tech = row[header2[config.subtech_key]]
        pname = row[header2[config.prod_name_key]]
        
        if str([tech,sub_tech]) in ts2p.keys():
            ts2p[str([tech,sub_tech])].append(pname)
        else:
            ts2p[str([tech,sub_tech])] = [pname]





print ("#normalized sw map entries "+str(len(swv2nswv)))
SEPARATOR_TOKEN=" <> "
header, pnmap, r_pnmap = loadTST_SWVMap(config.swv_tst_map_file, SEPARATOR_TOKEN)



prows=[]
nrows=[]
prows_sw=[]
nrows_sw=[]


src_list=config.sourcefield_names



seen={}
nomatchlist=[]
matchlist=[]



newrows=[]
for row in rows:
    
    srnum=row[rowhead.index(config.sr_key)]
    src=""
    pname_tgt=""
    swv_tgt=""
    ptechs=""
    psubtechs=""
    
    if srnum in seen:
        continue
    
    seen[srnum]=""
    
   
    for en in config.sourcefield_names:
        src += " "+row[rowhead.index(en)]
    
    swv_tgt = row[rowhead.index(config.sw_version_key)].strip()
    ptechs = row[rowhead.index(config.tech_key)]
    psubtechs = row[rowhead.index(config.subtech_key)]
    pname_tgt = row[rowhead.index(config.prod_name_key)]
    try:
        pname_list = ts2p[str([ptechs,psubtechs])]
    except:
        pname_list = [pname_tgt]
            
    key = ptechs.strip()+config.SEPARATOR_TOKEN+psubtechs.strip()
    cnotes = []
    if srnum in sr_cn:
        cnotes = sr_cn[srnum]
    
    ntgt = swv_tgt
    if swv_tgt in swv2nswv:
        ntgt = swv2nswv[swv_tgt]

    
    
    key = ptechs.strip()+config.SEPARATOR_TOKEN+psubtechs.strip()
    
    
    if key not in pnmap:
        print ("KEY not found in pnmap "+key)
        print ("Skipping SR "+srnum)
        continue
    
    plabels = pnmap[key] #[tgt]
    
    #print ("tgt "+tgt+" ntgt="+ntgt+" #potlabels="+str(len(plabels)))
    match=False
    match_sw = False
    words = src.split()
    for word in words:
        for ptgt in plabels:
            if ptgt.strip() in swv2nswv:
                nptgt = swv2nswv[ptgt.strip()]
            else:
                nptgt = ptgt
            if matchSWStrings(word, nptgt):
                match_sw=True

        for ptgt_2 in pname_list:
            if edmatch(word, ptgt_2):
                match=True
                print ("Match in metadata, word="+word+" pname=" + ptgt_2)
            
                #print ("Match in metadata, word="+word+" pname="+pname_tgt)
    
    if len(plabels)==0 or src.strip()=="":
        print ("DEBUG IGNORING entry since plabels/note is empty")
    else:
    
        if match:
            prows.append([srnum, "srmeta", src, str(plabels),str(pname_list), ntgt, pname_tgt,str(match),str(match_sw)])
        else:
            nrows.append([srnum, "srmeta", src, str(plabels),str(pname_list), ntgt, pname_tgt,str(match),str(match_sw)])
        if match_sw:
            prows_sw.append([srnum, "srmeta", src, str(plabels),str(pname_list), ntgt, pname_tgt,str(match),str(match_sw)])
        else:
            nrows_sw.append([srnum, "srmeta", src, str(plabels),str(pname_list), ntgt, pname_tgt,str(match),str(match_sw)])
        
    if len(cnotes)>10:
        random.shuffle(cnotes)
        cnotes = cnotes[0:10]
         
    for cx, cnote in enumerate(cnotes):
        (cntype, _, raw_note, ext_note) = cnote
        if ext_note=="":
            ext_note = raw_note
        
        match=False
        words = ext_note.split()
        for word in words:
            for ptgt in plabels:
                if ptgt.strip() in swv2nswv:
                    nptgt = swv2nswv[ptgt.strip()]
                else:
                    nptgt = ptgt
                if matchSWStrings(word, nptgt):
                    #print ("Match in metadata, word="+word+" pname_tgt="+pname_tgt)
                    match_sw=True
            for ptgt_2 in pname_list:
                if edmatch(word, ptgt_2):
                    match=True
                    print ("Match in metadata, word="+word+" pname="+ptgt_2)
            
        
        if len(plabels)==0 or ext_note.strip()=="":
            #print ("DEBUG IGNORING entry since plabels/note is empty")
            continue
            
            
        if match:
            prows.append([srnum, cntype.replace(" ","").strip(), \
                          ext_note, str(plabels),str(pname_list), ntgt, pname_tgt,str(match),str(match_sw)])
        else:
            nrows.append([srnum, cntype.replace(" ","").strip(), \
                          ext_note, str(plabels),str(pname_list), ntgt, pname_tgt,str(match),str(match_sw)])
            
        if match_sw:
            prows_sw.append([srnum, cntype.replace(" ","").strip(), \
                          ext_note, str(plabels),str(pname_list), ntgt, pname_tgt,str(match),str(match_sw)])
        else:
            nrows_sw.append([srnum, cntype.replace(" ","").strip(), \
                          ext_note, str(plabels),str(pname_list), ntgt, pname_tgt,str(match),str(match_sw)])
                        
        


print("len(prows)="+str(len(prows))+ " len(nrows)="+str(len(nrows)))
print("len(prows_sw)="+str(len(prows_sw))+ " len(nrows_sw)="+str(len(nrows_sw)))

testsrs=[]
if len(goldsrs)!=0:
    for srnum in goldsrs:
        if srnum in seen:
            testsrs.append(srnum)
trainsrs=[]
for srnum in seen:
    if srnum not in testsrs:
        trainsrs.append(srnum)

if len(testsrs)==0:
    random.shuffle(trainsrs)
    maxi = int (0.8*len(trainsrs))
    for ix in range(maxi, len(trainsrs)):
        testsrs.append(trainsrs[ix])
        
    trainsrs=trainsrs[0:maxi]
        
# print ("#goldsrs="+str(len(goldsrs)))
# print ("#trainsrs="+str(len(trainsrs)))
# print ("#testsrs="+str(len(testsrs)))

header=["SR","CNTYPE","source","swv_labels","pname_labels","SWV_VERSION","PROD_NAME","target_sw","target_pname"]

fout1 = open (tr_opfile, "w")
csvw1 = csv.writer(fout1, delimiter=",", quotechar='"', \
                  quoting=csv.QUOTE_MINIMAL)
csvw1.writerow(header)

fout2 = open (ts_opfile, "w")
csvw2 = csv.writer(fout2, delimiter=",", quotechar='"', \
                  quoting=csv.QUOTE_MINIMAL)

csvw2.writerow(header)    
   
trcnt=0
tscnt=0 
for prow in prows:
    
    hasnones=False
    for ele in prow:
        
        if ele is None or ele=="":
            hasnones=True
            break
    
    if hasnones:
        continue

    sr = prow[0]
    if sr not in testsrs:
        csvw1.writerow(prow)
        fout1.flush()
        trcnt += 1
    else:
        
        csvw2.writerow(prow)
        fout2.flush()
        tscnt += 1
    
for nrow in nrows:
    
    hasnones=False
    for ele in nrow:
        
        if ele is None or ele=="":
            hasnones=True
            break
    
    if hasnones:
        continue
        
    sr = nrow[0]
    if sr not in testsrs:
        csvw1.writerow(nrow)
        fout1.flush()
        trcnt += 1
    else:
       
        csvw2.writerow(nrow)
        fout2.flush()
        tscnt += 1
        
        

print ("#tr rows="+str(trcnt))
print ("#ts rows="+str(tscnt))
fout1.close()
fout2.close()
print ("##############################")
print ("Train/Test files written to ")
print (tr_opfile)
print (ts_opfile)
                    