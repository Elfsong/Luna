# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 22/12/2023

from difflib import SequenceMatcher


class Evaluator(object):
    @classmethod
    def eval(cls, a: str, b: str, threshold: float) -> bool:
        raise NotImplementedError("Don't call the abstrct interface directly")
    
    
class LCSEvaluator(Evaluator):    
    @classmethod
    def eval(cls, a: str, b: str, threshold: float) -> bool:
        match = SequenceMatcher(None, a, b).find_longest_match()
        overlap = match.size / len(a)
        correct = 1 if overlap > threshold else 0
        return correct, overlap
        