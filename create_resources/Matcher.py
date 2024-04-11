#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 12 10:50:27 2024

@author: sdas
"""

import regex as re
import editdistance
EDTHRESH=0.2
MATCHTHRESH2=0.6
#characters to be treated as equivalent in SW strings
# .)(-


def noNumeric(text):
    swv = text.strip()
    replaced_swv = re.sub('\d', '', swv).strip()
    if len(replaced_swv)==len(swv):
        return True
    else:
        return False
    
def matchSWStrings(pred, tgt):
    
    predwds = pred.replace(".","-").replace(")","-").replace("(","-").strip()
    predwds = predwds.split("-")
    predIsNum = isNumericOnly(predwds)
    
    tgtwds = tgt.replace(".","-").replace(")","-").replace("(","-").strip()
    tgtwds = tgtwds.split("-")
    tgtIsNum = isNumericOnly(tgtwds)
    
    if predIsNum and tgtIsNum:
        return matchBothNumeric(predwds, tgtwds)
    if noNumeric(pred) and noNumeric(tgt):
        #print ("HERE")
        return edmatch(pred, tgt)
    if predIsNum and not tgtIsNum:
        return matchIsContained(predwds, tgtwds)
    elif not predIsNum and tgtIsNum:
        return matchIsContained(tgtwds, predwds)
    else: #mix of words and numerics
        
        
        nstr_p=""
        nnstr_p=""
        for wd in predwds:
            if wd.isnumeric():
                nstr_p += "."+str(int(wd))
            else:
                nnstr_p += "."+wd
                
        nstr_t=""
        nnstr_t=""
        for wd in tgtwds:
            if wd.isnumeric():
                nstr_t += "."+str(int(wd))
            else:
                nnstr_t += "."+wd
        
        if nstr_t==nstr_p and edmatch(nnstr_p, nnstr_t):
            return True
            
        
    return False
    
def matchBothNumeric(predwds, tgtwds):
    
    temp1=""
    for wd in predwds:
        if wd=="":
            continue
        
        temp1 +="."+str(int(wd)) #to catch 04 and 4
    temp2=""
    for wd in tgtwds:
        temp2 +="."+str(int(wd)) 
        
    if temp1==temp2:
        return True
    
    return False
    
def matchIsContained(s1wds, s2wds): #check if s1 is contained in s2

    temp1=""
    for wd in s1wds:
        if wd=="":
            continue
        temp1 +="."+str(int(wd)) #to catch 04 and 4
        
    temp2=""
    for wd in s2wds:
        if wd.isnumeric():
            temp2 +="."+str(int(wd)) 
        else:
            temp2 +="."+wd
        
    if temp1 in temp2 and len(temp1)>=(MATCHTHRESH2)*len(temp2):
        return True
    
    return False


def match_split(src2):   

    src2 = src2.replace(".","-").replace(")","-").replace("(","-").strip()
    srcwds = src2.split("-")
    return srcwds

def isNumericOnly(wds):
    
    for wd in wds:
    
        if wd!="" and not wd.isnumeric():
            return False
        
    
    return True


def edmatch(s1, s2):
    maxl = max(len(s1), len(s2))
    ed = editdistance.eval(s1, s2)
    #print (ed/maxl)
    if (ed/maxl) <= EDTHRESH:
        return True
    # elif s1 in s2 or s2 in s1:
    #     return True
    
    return False

if __name__=="__main__":
    s1="9.16.2.3"
    s11="9.16.2.3"
    print (matchSWStrings(s1, s11))
    s1="9.16(2)3"
    s11="9.16.2.3"
    print (matchSWStrings(s1, s11))
    s2="15.5(1)SY1"
    s21="15.5.1"
    print (matchSWStrings(s21, s2))
    print (matchSWStrings(s1, s2))
    s3="ise-2.6.0.156.SPA.x86_64.iso"
    s4="ise-2.6.0.156"
    print (matchSWStrings(s3, s4))
    s5="cat9k_iosxe.16.12.04.SPA.bin"
    s6="cat9k_lite_iosxe.16.12.04.SPA.bin"
    print (matchSWStrings(s5, s6))
