# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 22/12/2023

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
        overlap = match.size / len(a)
        correct = True if overlap > threshold else False
        return correct, overlap
    
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
        