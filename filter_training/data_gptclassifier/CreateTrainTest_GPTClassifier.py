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
import GPTClassifierTDConfig as config
from Matcher import matchSWStrings
from GPTClassifierTDUtils import loadCaseNotes, loadTST_SWVMap


tr_opfile=config.output_dir+"/train_data.csv"
ts_opfile=config.output_dir+"/test_gold_data.csv"


data = json.load(open (config.metadata_json_file, "r"))
cndata_file = config.casenotes_json_file
rows=[]

for ele in data:
    row=[ele[config.sr_key]]
    for field in config.fields:
        if field in ele:
            if ele[field] is None:
                print (field+" is None for "+ele[config.sr_key])
                break            
            row.append(ele[field])
        else:
            print (field+" not found for "+ele[config.sr_key])
            break
    
    if len(row)==8:
        rows.append(row)
        

    
print ("#rows="+str(len(rows)))



csvr = csv.reader(open(config.gold_csv_file, "r"))
header=[]
goldsrs=[]
for row in csvr:
    if len(header)==0:
        header = row
        continue
    else:
        srid = row[config.srcolid].strip()
        if srid not in goldsrs:
            goldsrs.append(srid)
        
print ("gold len(srids)="+str(len(goldsrs)))

sr_cn = loadCaseNotes(cndata_file)
print ("len(sr_cn)="+str(len(sr_cn)))




csvr = csv.reader(open(config.tst_swv_mapfile, "r"))
header = {}
swv2nswv={}
for row in csvr:
    if len(header)==0:
        for rx, rele in enumerate(row):
            header[rele]=rx
        print (header)
        continue
    else:
        swv = row[header["SW_Version__c"]]
        nswv = row[header["Norm_SWV"]]
        swv2nswv[swv.strip()] = nswv.strip()
        

print ("#normalized sw map entries "+str(len(swv2nswv)))
SEPARATOR_TOKEN=" <> "
header, pnmap, r_pnmap = loadTST_SWVMap(config.tst_swv_mapfile, SEPARATOR_TOKEN)



prows=[]
nrows=[]


src_list=config.sourcefield_names



seen={}
nomatchlist=[]
matchlist=[]

#fields=["Technology_Text__c", "Sub_Technology_Text__c", "Product_Name__c",\
 #      "SW_Version__c", "Customer_Symptom__c","Description","Resolution_Summary__c"]
 



newrows=[]
for row in rows:
    
    srnum=row[config.srcolid]
    src=""
    pname_tgt=""
    swv_tgt=""
    ptechs=""
    psubtechs=""
    
    if srnum in seen:
        continue
    
    seen[srnum]=""
    
   
    
    for ex, ele in enumerate(row):
        
        
        if ex in config.srcids:
            src += " "+row[ex]
        
        if ex==config.swvid:
            swv_tgt = row[ex].strip()
        
        if ex==config.ptechid:
            ptechs = row[ex]
            
        if ex==config.psubtechid:
            psubtechs = row[ex]
        
        if ex==config.pnameid:
            pname_tgt=row[ex]
        
            
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
    words = src.split()
    for word in words:
        for ptgt in plabels:
            if ptgt.strip() in swv2nswv:
                nptgt = swv2nswv[ptgt.strip()]
            else:
                nptgt = ptgt
            
            if matchSWStrings(word, nptgt):
                match=True
                #print ("Match in metadata, word="+word+" ntgt="+ntgt+" nptgt="+nptgt)
    
    if len(plabels)==0 or src.strip()=="":
        print ("DEBUG IGNORING entry since plabels/note is empty")
    else:
    
        if match:
            prows.append([srnum, "srmeta", src, str(plabels), ntgt, pname_tgt])
        else:
            nrows.append([srnum, "srmeta", src, str(plabels), ntgt, pname_tgt])
        
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
                    #print ("Match in metadata, word="+word+" ntgt="+ntgt+" nptgt="+nptgt)
                    match=True
        
        
        if len(plabels)==0 or ext_note.strip()=="":
            print ("DEBUG IGNORING entry since plabels/note is empty")
            continue
            
            
        if match:
            prows.append([srnum, cntype.replace(" ","").strip(), \
                          ext_note, str(plabels), ntgt, pname_tgt])
        else:
            nrows.append([srnum, cntype.replace(" ","").strip(), \
                          ext_note, str(plabels), ntgt, pname_tgt])
                        
        
#     #print ("match is "+str(match)+" for "+srnum+"\n\n")
#     if not match:
#         nomatchlist.append(srnum)
#     else:
#         matchlist.append(srnum)
        
# print("=========no match list=========")        
# print (len(nomatchlist))
# print (nomatchlist)
# print("=========good list=========")
# print (len(goodlist))
# print (goodlist)
# print("=========match list=========")
# print (len(matchlist))
# print (matchlist)
print("len(prows)="+str(len(prows))+ " len(nrows)="+str(len(nrows)))

header=["SR","CNTYPE","source","plabels","SWV_VERSION","PROD_NAME","target"]

fout1 = open (tr_opfile, "w")
csvw1 = csv.writer(fout1, delimiter=",", quotechar='"', \
                  quoting=csv.QUOTE_MINIMAL)
csvw1.writerow(header)

fout2 = open (ts_opfile, "w")
csvw2 = csv.writer(fout2, delimiter=",", quotechar='"', \
                  quoting=csv.QUOTE_MINIMAL)
header.append("GOLDTYPE")
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
        
    
    tgt = "True"
    prow.append(tgt)
    sr = prow[0]
    if sr not in goldsrs:
        csvw1.writerow(prow)
        fout1.flush()
        trcnt += 1
    else:
        if sr in config.goodlist:
            prow.append("TYPE3")
        else:
            prow.append("NOTTYPE3")
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
        
    tgt = "False"
    nrow.append(tgt)
    sr = nrow[0]
    if sr not in goldsrs:
        csvw1.writerow(nrow)
        fout1.flush()
        trcnt += 1
    else:
        if sr in config.goodlist:
            nrow.append("TYPE3")
        else:
            nrow.append("NOTTYPE3")
            
        csvw2.writerow(nrow)
        fout2.flush()
        tscnt += 1
        
        

print ("#tr rows="+str(trcnt))
print ("#ts rows="+str(tscnt))
fout1.close()
fout2.close()

                    