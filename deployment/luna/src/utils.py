# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 06/04/2024

import json
import pandas as pd
from collections import defaultdict

def get_config(config_path='./config/default.json') -> dict:
    with open(config_path, 'r') as config_f:
        return json.load(config_f)
    
def get_p_mapping(file_path: str) -> dict:
    df = pd.read_excel(file_path)
    p_mapping = defaultdict(lambda: defaultdict(lambda: list()))

    for _, row in df.iterrows():
        tech = row["Technology_Text__c"]
        sub_tech = row["Sub_Technology_Text__c"]
        p = row["Product_Name__c"]
        p_mapping[tech][sub_tech] += [str(p)]
        
    return p_mapping

def get_s_mapping(file_path: str) -> dict:
    df = pd.read_excel(file_path)
    s_mapping = defaultdict(lambda: defaultdict(lambda: list()))

    for _, row in df.iterrows():
        tech = row["Technology_Text__c"]
        sub_tech = row["Sub_Technology_Text__c"]
        s = row["SW_Version__c"]
        s_mapping[tech][sub_tech] += [str(s)]
        
    return s_mapping

def get_sr_data(metadata_file, notes_file):
    mf, cf = list(), list()
    case_metadata, case_notes = dict(), dict()
    
    if metadata_file and notes_file:
        mf = json.load(metadata_file)
        cf = json.load(notes_file)
    
    for m in mf:
        case_metadata[m["sr"]] = m
        case_notes[m["sr"]] = list()
        
    for c in cf:
        case_notes[c["sr"]] += [c]
        
    return case_metadata, case_notes

def note_filter(notes, filter, filter_list, regex_filter_switch, nn_filter_switch):
    note_contents = list()
    editable_casenotes = list()
    for _, note in enumerate(notes):

        # Filter by Empty
        if 'extracted_note' not in note:
            note['extracted_note'] = note['Note__c']
        
        # Filter by Regex
        if regex_filter_switch and not filter.filter_by_regex(note, filter_list):
            continue
        
        # Filter by NN
        if nn_filter_switch and not filter.filter_by_classifier(note, filter_list):
            continue
        
        editable_casenotes += [note]               
        note_contents += [note["extracted_note"]]
    
    return note_contents, editable_casenotes

def context_constrct(note_contents, metadata, option_list):
    context = ""
    if "notes" in option_list:
        context += "\n".join(note_contents)
    if "symptom" in option_list:
        context += "\n" + metadata["Customer_Symptom__c"]
    if "description" in option_list:
        context += "\n" + metadata["Description"]
    if "summary" in option_list:
        context += "\n" + metadata["Resolution_Summary__c"] 
    return context


def product_prediction(llm_caller, context, p_str):
    question = f'Which product is principally discussed in these documents?'
    response = llm_caller.product_analysis([context], question, p_str)

    prediction, summary, explanation = "", "", ""
    try:
        response_json = json.loads(response)
        prediction = response_json['product_name']
        summary = response_json['summary']
        explanation = response_json['explanation']
    except Exception as e:
        prediction = response
        
    return prediction, summary, explanation


def software_prediction(llm_caller, context, s_str):
    question = f'Which software version is principally discussed in these documents?'
    response = llm_caller.software_analysis([context], question, s_str)

    prediction, summary, explanation = "", "", ""
    try:
        response_json = json.loads(response)
        prediction = response_json['software_version']
        summary = response_json['summary']
        explanation = response_json['explanation']
    except Exception as e:
        prediction = response
    
    return prediction, summary, explanation