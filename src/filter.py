#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sat Feb 24 13:55:19 2024
@author: sdas
"""

from . caller import TGICaller, LocalCaller
from . evaluator import NewSDASEvaluator


class Filter():
    def __init__(self, config,console=None) -> None:
        self.llm_caller = TGICaller(config,console)
        self.llm_caller_local = LocalCaller(config,console)
        self.console = console
    
    @staticmethod
    def get_note_content(case_note):
        # Copy directly / Improve needed
        raw_note = case_note['Note__c'] if 'Note__c' in case_note else ""
        ext_note = case_note['extracted_note'] if 'extracted_note' in case_note else ""
        ext_note = raw_note if ext_note.strip() else ext_note
        return ext_note

    def filter_by_regex(self, case_note, s_list):
        ext_note = Filter.get_note_content(case_note)
        for word in ext_note.split():
            for s in s_list:
                if NewSDASEvaluator.eval(word, s):
                    return True
        return False
    
    def filter_by_classifier(self, case_note, s_list):
        ext_note = Filter.get_note_content(case_note)
        prompt = f"Question: Given the list of labels, does the passage contain any of the labels? \
                   Answer True or False. Labels={str(s_list)} passage={ext_note}"
        # print(prompt)
        response = self.llm_caller.call(prompt=prompt, max_new_tokens=10)
        # print(f"Response: [{response}]")
        print(response)
        return True if response == "True" else False
    
    def filter_by_local_classifier(self, case_note, s_list):
        ext_note = case_note
        prompt = f"Question: Given the list of labels, does the passage contain any of the labels? \
                   Answer True or False. Labels={str(s_list)} passage={ext_note}"

        response = self.llm_caller_local.call(prompt=prompt)

        return True if response == "True" else False