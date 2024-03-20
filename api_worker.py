# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 27/02/2024

import json
import time
import argparse
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field
from rich.progress import track
from rich.console import Console
from src.graph import CiscoGraph
from typing import Union, Optional
from src.caller import OpenAICaller, TGICaller
from src.evaluator import LCSEvaluator, SDASEvaluator
from src.utils import get_product_mapping, get_swv_mapping, save_results, banner, config_generator, load_metadata, load_notes

console = Console(record=True)

# Step 1. Load Configuration
config_path = './config/gpt-3.json'
task = 'software'
with open(config_path, 'r') as config_f:
    config = json.load(config_f)
    
# Step 2. Load Handlers
graph_handler = CiscoGraph(config['graph_url'], config['graph_user'], config['graph_pwd'])
llm_caller = None
if config["type"] == "openai":
    llm_caller = OpenAICaller(config, console)
elif config["type"] == "llama":
    llm_caller = TGICaller(config, console)
else:
    raise NotImplementedError(f'Unknown Type [{config["type"]}]')

# Step 3. Loading software version mapping file
s_mapping = get_swv_mapping('./data/tech_subtech_swv.xlsx')
p_mapping = get_product_mapping('./data/tech_subtech_pnames.xlsx')


app = FastAPI()

class SRItem(BaseModel):
    question: str = Field(default='null')
    product_name: str = Field(default='null')
    p_str: str = Field(default='null')
    doc: str = Field(default='null')
    
@app.post("/process/{item_id}")
def process(sr: int, sr_data: SRItem):
    # Retrieving the node from the graph
    mnode = graph_handler.raw_excute(f"MATCH (n:Gold WHERE n.sr='{sr}') RETURN n")
    mnode_data = mnode[0]['n']
    mnode_sr = mnode_data["sr"]
    mnode_product = mnode_data["Product_Name__c"]
    mnode_tech = mnode_data["Technology_Text__c"]
    mnode_subtech = mnode_data["Sub_Technology_Text__c"]
    p_list = p_mapping[mnode_tech][mnode_subtech]
    p_str = "/ ".join(p_list)
    
    notes = list()  
    nnodes = graph_handler.raw_excute(f"MATCH (m:Metadata) WHERE (m.sr = '{mnode_sr}') MATCH ((m)-[:Has]->(n)) RETURN n")
    for nnode in nnodes:
        nnode_data = nnode["n"]
        if 'extracted_note' in nnode_data:
            note_content = nnode_data["extracted_note"]
            notes += [note_content]
    
    doc = ""
    if "notes" in config["fields"]:
        doc += "\n".join(notes)
    if "symptom" in config["fields"]:
        doc += "\n" + mnode_data["Customer_Symptom__c"]
    if "description" in config["fields"]:
        doc += "\n" + mnode_data["Description"]
    if "summary" in config["fields"]:
        doc += "\n" + mnode_data["Resolution_Summary__c"]
        
    question = f'Which product is principally discussed in these documents?'
    
    # Update fields
    if sr_data.question != 'null':
        question = sr_data.question
    if sr_data.product_name != 'null':
        mnode_product = sr_data.product_name
    if sr_data.p_str != 'null':
        p_str = sr_data.p_str
    if sr_data.doc != 'null':
        doc = sr_data.doc
    
    response = llm_caller.product_analysis([doc], question, p_str)
    
    prediction, summary, explanation = "", "", ""
    try:
        response_json = json.loads(response)
        prediction = response_json['product_name']
        summary = response_json['summary']
        explanation = response_json['explanation']
    except Exception as e:
        console.log(f"[bold red] [Worker] Json parse error: {e}. Using the original response instead.")
        prediction = response
    
    correct, overlap = LCSEvaluator.eval(mnode_product, prediction, 0.5)
        
    result = {
        "sr": mnode_sr,
        "product_name": mnode_product,
        "prediction": prediction,
        "explanation": explanation,
        "summary": summary,
        "overlap": overlap,
        "correct": correct,
    }
    
    return {"sr": sr, "result": result}