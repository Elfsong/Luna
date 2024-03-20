# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 29/12/2023

import json
import pandas as pd
from rich import print
from rich.prompt import Prompt
from rich.progress import track
from collections import defaultdict
from src.datatypes import SR_Metadata, SR_Note

def banner():
    with open('./data/banner', 'r') as banner_f:
        print(banner_f.read())
        
def load_metadata(file_path):
    with open(file_path) as file_handler:
        data = json.load(file_handler)

    sr_set, sr_data = set(), list()
    for instance in track(data, description=f"Parsing raw metadata from {file_path}..."):
        if instance["sr"] not in sr_set:
            sr_data += [SR_Metadata(instance)]
            sr_set.add(instance["sr"])
    
    return sr_data

def load_notes(file_path):
    with open(file_path) as file_handler:
        data = json.load(file_handler)
        
    sr_data = list()
    for instance in track(data, description=f"Parsing raw notes from {file_path}..."):
        sr_data += [SR_Note(instance)]
        
    return sr_data

def config_generator(console):
    config = dict()
    # type
    while True:
        print('[blue]Luna[/blue]: Which model type do you want to preceed? [openai/[u]llama[/u]]')
        type_input = Prompt.ask('You')
        if type_input in ['llama', 'openai']:
            config['type'] = type_input
            break
        elif type_input == "":
            config['type'] = 'llama'
            break
        else:
            print('[blue]Luna[/blue]: Model type should be picked from [openai/llama].')
                
    # model_name
    while True:
        model_name_default = '[u]Llama-70b[/u]' if config['type'] == 'llama' else '[gpt-4-preview-1106/[u]gpt-3.5-turbo-1106[/u]]'
        print(f'[blue]Luna[/blue]: Which specific model you would like to try? [{model_name_default}]')
        model_name_input = Prompt.ask('You')
        if model_name_input == "":
            config['model_name'] = model_name_default
            break
        else:
            config['model_name'] = model_name_input
            break
    
    # llm
    if config['type'] == 'llama':
        while True:
            llm_url_default = 'http://10.246.112.13:8080'
            print(f'[blue]Luna[/blue]: Cool! What is your llm server address? [[u]{llm_url_default}[/u]]')
            llm_url_input = Prompt.ask('You')
            if llm_url_input == "":
                config['llm_url'] = llm_url_default
                break
            else:
                config['llm_url'] = llm_url_default
                break
            
    elif config['type'] == 'openai':
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
        chunk_size_default = 2048 if config['type'] == 'llama' else 12800
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
        chunk_overlap_default = 256 if config['type'] == 'llama' else 512
        print(f'[blue]Luna[/blue]: How about the chunk overlap? [[u]{chunk_overlap_default}[/u]]')
        chunk_overlap_input = Prompt.ask('You')
        chunk_overlap_input = int(chunk_overlap_input) if chunk_overlap_input else chunk_overlap_default
        if 0 < chunk_overlap_input < 128000:
            config['chunk_overlap'] = chunk_overlap_input
            break
        else:
            print('[blue]Luna[/blue]: chunk_overlap should between 0 to 128000. It depends on the model you choose.')
                
    # graph_url
    while True:
        graph_url_default = 'bolt://10.245.89.103:7687'
        print(f'[blue]Luna[/blue]: What is your graph server address? [[u]{graph_url_default}[/u]]')
        graph_url_input = Prompt.ask('You')
        if graph_url_input == "":
            config['graph_url'] = graph_url_default
            break
        else:
            config['graph_url'] = graph_url_input
            break
    
    # graph_user
    while True:
        graph_user_default = 'neo4j'
        print(f'[blue]Luna[/blue]: What is your graph server username? [[u]{graph_user_default}[/u]]')
        graph_user_input = Prompt.ask('You')
        if graph_user_input == "":
            config['graph_user'] = graph_user_default
            break
        else:
            config['graph_user'] = graph_user_input
            break
    
    # graph_pwd
    while True:
        graph_pwd_default = 'yyids123'
        print(f'[blue]Luna[/blue]: What is your graph server password? [[u]{graph_pwd_default}[/u]]')
        graph_pwd_input = Prompt.ask('You')
        if graph_pwd_input == "":
            config['graph_pwd'] = graph_pwd_default
            break
        else:
            config['graph_pwd'] = graph_pwd_input
            break
    
    # graph_metadata
    while True:
        graph_metadata_default = './data/NUS_Case_Metadata.json'
        print(f'[blue]Luna[/blue]: Where is your metadata path? [[u]{graph_metadata_default}[/u]]')
        graph_metadata_input = Prompt.ask('You')
        if graph_metadata_input == "":
            config['graph_metadata'] = graph_metadata_default
            break
        else:
            config['graph_metadata'] = graph_metadata_input
            break
    
    # graph_notes
    while True:
        graph_notes_default = './data/NUS_Case_Notes.json'
        print(f'[blue]Luna[/blue]: Where is your notes path? [[u]{graph_notes_default}[/u]]')
        graph_notes_input = Prompt.ask('You')
        if graph_notes_input == "":
            config['graph_notes'] = graph_notes_default
            break
        else:
            config['graph_notes'] = graph_notes_input
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
    df = pd.read_excel(file_path)
    p_mapping = defaultdict(lambda: defaultdict(lambda: list()))

    for _, row in df.iterrows():
        tech = row["Technology_Text__c"]
        sub_tech = row["Sub_Technology_Text__c"]
        p = row["Product_Name__c"]
        p_mapping[tech][sub_tech] += [str(p)]
        
    return p_mapping

def get_swv_mapping(file_path: str) -> dict:
    df = pd.read_excel(file_path)
    s_mapping = defaultdict(lambda: defaultdict(lambda: list()))

    for _, row in df.iterrows():
        tech = row["Technology_Text__c"]
        sub_tech = row["Sub_Technology_Text__c"]
        s = row["SW_Version__c"]
        s_mapping[tech][sub_tech] += [str(s)]
        
    return s_mapping

def get_norm_swv_mapping(file_path: str) -> dict:
    df = pd.read_excel(file_path)
    s_mapping = defaultdict(lambda: defaultdict(lambda: list()))

    for _, row in df.iterrows():
        tech = row["Technology_Text__c"]
        sub_tech = row["Sub_Technology_Text__c"]
        s = row["Norm_SWV"]
        s_mapping[tech][sub_tech] += [str(s)]
        
    return s_mapping

def save_results(df: pd.DataFrame, file_path: str) -> None:
    df.to_csv(file_path)