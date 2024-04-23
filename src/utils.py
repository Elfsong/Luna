# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 29/12/2023
import os
import json
import pandas as pd
from rich import print
from rich.prompt import Prompt
from rich.progress import track
from collections import defaultdict

import tiktoken

def banner():
    with open('./data/banner', 'r') as banner_f:
        print(banner_f.read())
        
def config_generator(console):
    config = dict()
    # model_name
    while True:
        model_name_default = '[gpt-4-preview-1106/[u]gpt-3.5-turbo-1106[/u]]'
        print(f'[blue]Luna[/blue]: Which specific model you would like to try? [{model_name_default}]')
        model_name_input = Prompt.ask('You')
        if model_name_input == "":
            config['model_name'] = 'gpt-3.5-turbo-1106'
            break
        else:
            config['model_name'] = model_name_input
            break
    
    while True:
        openai_api_key_default = 'OPENAI_KEY'
        print(f'[blue]Luna[/blue]: Well, what is your openai api key? [[u]{openai_api_key_default}[/u]]')
        openai_api_key_input = Prompt.ask('You')
        if openai_api_key_input == "":
            config['openai_api_key'] = openai_api_key_default
            break
        else:
            config['openai_api_key'] = openai_api_key_input
            break
    
    # chunk_size
    while True:
        chunk_size_default =  16000
        print(f'[blue]Luna[/blue]: How about the chunk size? [[u]{chunk_size_default}[/u]]')
        chunksize_input = Prompt.ask('You')
        chunksize_input = int(chunksize_input) if chunksize_input else chunk_size_default
        if 128 < chunksize_input < 128000:
            config['chunk_size'] = chunksize_input
            break
        else:
            print('[blue]Luna[/blue]: chunk_size should between 128 to 128000. It depends on the model you choose.')
        
    # chunk_overlap
    while True:
        chunk_overlap_default = 512
        print(f'[blue]Luna[/blue]: How about the chunk overlap? [[u]{chunk_overlap_default}[/u]]')
        chunk_overlap_input = Prompt.ask('You')
        chunk_overlap_input = int(chunk_overlap_input) if chunk_overlap_input else chunk_overlap_default
        if 0 < chunk_overlap_input < 128000:
            config['chunk_overlap'] = chunk_overlap_input
            break
        else:
            print('[blue]Luna[/blue]: chunk_overlap should between 0 to 128000. It depends on the model you choose.')

    
    # file_metadata
    while True:
        file_metadata_default = './data/NUS_Case_Metadata.json'
        print(f'[blue]Luna[/blue]: Where is your metadata path? [[u]{file_metadata_default}[/u]]')
        file_metadata_input = Prompt.ask('You')
        if file_metadata_input == "":
            config['filepath_metadata'] = file_metadata_default
            break
        else:
            config['filepath_metadata'] = file_metadata_input
            break
    
    # file_notes
    while True:
        file_notes_default = './data/NUS_Case_Notes.json'
        print(f'[blue]Luna[/blue]: Where is your notes path? [[u]{file_notes_default}[/u]]')
        file_notes_input = Prompt.ask('You')
        if file_notes_input == "":
            config['filepath_notes'] = file_notes_default
            break
        else:
            config['filepath_notes'] = file_notes_input
            break
        
    # fields
    while True:
        fields_default = ["notes", "symptom", "description", "summary"]
        print(f'[blue]Luna[/blue]: What fields do you want to count in? Split fields using comma. [[u]{fields_default}[/u]]')
        fields_input = Prompt.ask('You')
        
        if fields_input == '':
            config['fields'] = fields_default
            break
        else:
            config['fields'] = fields_input.split(',')
            break
    
    # mcq
    while True:
        mcq_default = True
        print(f'[blue]Luna[/blue]: Would like like to use MCQ mode? [[u]{mcq_default}[/u]]')
        mcq_input = Prompt.ask('You')
        
        if mcq_input == '':
            config['mcq'] = mcq_default
            break
        else:
            config['mcq'] = mcq_input.split(',')
            break
        
    console.log(config)
    print("[blue]Luna[/blue]: Ok, you are good to go :rocket:")
    return config

def get_product_mapping(file_path: str) -> dict:
    ext = os.path.splitext(file_path)[1]
    if ext == '.psv':
        df = pd.read_psv(file_path)
    elif ext == '.csv':
        df = pd.read_csv(file_path)
    elif ext == '.xlsx':
        df = pd.read_excel(file_path)
    p_mapping = defaultdict(lambda: defaultdict(lambda: list()))

    for _, row in df.iterrows():
        tech = row["Technology_Text__c"]
        sub_tech = row["Sub_Technology_Text__c"]
        p = row["Product_Name__c"]
        p_mapping[tech][sub_tech] += [str(p)]
        
    return p_mapping

def get_swv_mapping(file_path: str) -> dict:
    ext = os.path.splitext(file_path)[1]
    if ext == '.psv':
        df = pd.read_psv(file_path)
    elif ext == '.csv':
        df = pd.read_csv(file_path)
    elif ext == '.xlsx':
        df = pd.read_excel(file_path)
    s_mapping = defaultdict(lambda: defaultdict(lambda: list()))
    swv_map = dict()
    for _, row in df.iterrows():
        tech = row["Technology_Text__c"]
        sub_tech = row["Sub_Technology_Text__c"]
        if "Norm_SWV" in row:
            s = row["Norm_SWV"]
            swv_map[row["SW_Version__c"]] = row["Norm_SWV"]
        else:
            s = row["SW_Version__c"]

        s_mapping[tech][sub_tech] += [str(s)]
        
    return s_mapping , swv_map


def save_results(df: pd.DataFrame, file_path: str) -> None:
    df.to_csv(file_path)

def get_sr_data(metadata_file, notes_file):
    mf, cf = list(), list()
    case_metadata, case_notes = dict(), dict()
    
    if metadata_file and notes_file:
        metadata_f = open(metadata_file, "r")
        notes_f = open(notes_file, "r")

        mf = json.load(metadata_f)
        cf = json.load(notes_f)

        metadata_f.close()
        notes_f.close()
    
    for m in mf:
        case_metadata[m["sr"]] = m
        case_notes[m["sr"]] = list()
        
    for c in cf:
        case_notes[c["sr"]] += [c]
        
    return case_metadata, case_notes

def get_price(model_name, text):
    price_base = 0
    if model_name == 'gpt-4-0125-preview' or model_name == 'gpt-4-1106-preview' :
        price_base  = 1/100000
    if model_name == 'gpt-4':
        price_base  = 3/100000
    if model_name == 'gpt-3.5-turbo-0125':
        price_base  = 5/10000000
    if model_name == 'gpt-3.5-turbo-instruct':
        price_base  = 15/10000000
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(text))
    price  = num_tokens * price_base
    return price, num_tokens

def create_summary(filename,content):
    with open(filename, 'w') as file:
        file.write(content)