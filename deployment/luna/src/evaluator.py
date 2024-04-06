# coding: utf-8

# Author: Copy directly from Sujatha (idssdg@nus.edu.sg).
# Date: 22/12/2023

import re
import editdistance
from difflib import SequenceMatcher


class Evaluator(object):
    @classmethod
    def eval(cls, a: str, b: str, threshold: float) -> bool:
        raise NotImplementedError("Don't call the abstrct interface directly")
    
    
class LCSEvaluator(Evaluator):    
    @staticmethod
    def eval(a: str, b: str, threshold: float) -> bool:
        match = SequenceMatcher(None, a, b).find_longest_match()
        overlap = match.size / (len(a) + 1e-5)
        correct = True if overlap > threshold else False
        return correct, overlap
    
class NewSDASEvaluator(Evaluator):
    """
    Created on Fri Jan 12 10:50:27 2024

    @author: sdas
    """
    @staticmethod
    def eval(pred, tgt, edthresh=0.2, matchthresh=0.6):
        predwds = pred.replace(".","-").replace(")","-").replace("(","-").strip()
        predwds = predwds.split("-")
        predIsNum = NewSDASEvaluator.isNumericOnly(predwds)
        
        tgtwds = tgt.replace(".","-").replace(")","-").replace("(","-").strip()
        tgtwds = tgtwds.split("-")
        tgtIsNum = NewSDASEvaluator.isNumericOnly(tgtwds)
        
        if predIsNum and tgtIsNum:
            return NewSDASEvaluator.matchBothNumeric(predwds, tgtwds)
        if NewSDASEvaluator.noNumeric(pred) and NewSDASEvaluator.noNumeric(tgt):
            #print ("HERE")
            return NewSDASEvaluator.edmatch(pred, tgt, edthresh)
        if predIsNum and not tgtIsNum:
            return NewSDASEvaluator.matchIsContained(predwds, tgtwds, matchthresh)
        elif not predIsNum and tgtIsNum:
            return NewSDASEvaluator.matchIsContained(tgtwds, predwds, matchthresh)
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
            
            if nstr_t==nstr_p and NewSDASEvaluator.edmatch(nnstr_p, nnstr_t, edthresh):
                return True
        return False
    
    @staticmethod
    def noNumeric(text):
        swv = text.strip()
        replaced_swv = re.sub('\d', '', swv).strip()
        if len(replaced_swv)==len(swv):
            return True
        else:
            return False
    
    @staticmethod 
    def matchBothNumeric(predwds, tgtwds):
        try:
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
        except Exception as e:
            return False
        return False
    
    @staticmethod
    def isNumericOnly(wds):
        for wd in wds:
            if wd!="" and not wd.isnumeric():
                return False
        return True

    @staticmethod 
    def edmatch(s1, s2, thresh):
        maxl = max(len(s1), len(s2))
        ed = editdistance.eval(s1, s2)
        #print (ed/maxl)
        if (ed/maxl) <= thresh:
            return True
        # elif s1 in s2 or s2 in s1:
        #     return True
        
        return False
    
    @staticmethod 
    def matchIsContained(s1wds, s2wds, matchthresh): #check if s1 is contained in s2
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
            
        if temp1 in temp2 and len(temp1)>=(matchthresh)*len(temp2):
            return True
        return False
            
    
class SDASEvaluator(Evaluator):
    """
    Created on Fri Jan 12 10:50:27 2024
    @author: sdas
    """

    @staticmethod
    def eval(pred, tgt, thresh=0.2):
        #characters to be treated as equivalent in SW strings
        # .)(-
        predwds = pred.replace(".","-").replace(")","-").replace("(","-").strip()
        predwds = predwds.split("-")
        predIsNum = SDASEvaluator.isNumericOnly(predwds)
        
        tgtwds = tgt.replace(".","-").replace(")","-").replace("(","-").strip()
        tgtwds = tgtwds.split("-")
        tgtIsNum = SDASEvaluator.isNumericOnly(tgtwds)
        
        if predIsNum and tgtIsNum:
            return SDASEvaluator.matchBothNumeric(predwds, tgtwds)
        
        if predIsNum and not tgtIsNum:
            return SDASEvaluator.matchIsContained(predwds, tgtwds)
        elif not predIsNum and tgtIsNum:
            return SDASEvaluator.matchIsContained(tgtwds, predwds)
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
            
            if nstr_t==nstr_p and SDASEvaluator.edmatch(nnstr_p, nnstr_t, thresh):
                return True
            
        return False
    
    @staticmethod
    def matchBothNumeric(predwds, tgtwds):
        temp1=""
        for wd in predwds:
            temp1 +="."+str(int(wd)) #to catch 04 and 4
        temp2=""
        for wd in tgtwds:
            temp2 +="."+str(int(wd)) 
            
        if temp1==temp2:
            return True
        
        return False
    
    @staticmethod
    def matchIsContained(s1wds, s2wds): #check if s1 is contained in s2
        temp1=""
        for wd in s1wds:
            temp1 +="."+str(int(wd)) #to catch 04 and 4
            
        temp2=""
        for wd in s2wds:
            if wd.isnumeric():
                temp2 +="."+str(int(wd)) 
            else:
                temp2 +="."+wd
            
        if temp1 in temp2:
            return True
        
        return False

    @staticmethod
    def isNumericOnly(wds):
        for wd in wds:
            if not wd.isnumeric():
                return False
        
        return True

    @staticmethod
    def edmatch(s1, s2, thresh=0.2):
        maxl = max(len(s1), len(s2))
        ed = editdistance.eval(s1, s2)
        #print (ed/maxl)
        if (ed/maxl) <= thresh:
            return True
        elif s1 in s2 or s2 in s1:
            return True
        
        return False
        