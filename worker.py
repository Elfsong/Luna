# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 22/12/2023

import json
import argparse
import pandas as pd
from tqdm import tqdm
from src.graph import CiscoGraph
from src.evaluator import LCSEvaluator
from src.caller import OpenAICaller, LlamaCaller
from src.utils import get_product_mapping, save_results, banner


def worker(graph_handler, caller, config):
    print(f"[Graph] Retrieving nodes from the graph.")
    mnodes = graph_handler.raw_excute("MATCH (m:Gold) RETURN m")       
    print(f"[Graph] Got {len(mnodes)} nodes from the graph.")
     
    print(f"[Utils] Loading product mapping file...")
    p_mapping = get_product_mapping('./data/tech_subtech_pnames.xlsx')
    print(f'[Utils] Product mapping file loaded.')
    
    results = list()
    total, correct_sum = 0, 0

    print(f"[Worker] Start to process nodes...")
    for mnode in tqdm(list(mnodes)[:3]):
        mnode_data = mnode["m"]
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
        
        response = caller.analysis([doc], question, p_str)
        
        prediction, summary, explanation = "", "", ""
        try:
            response_json = json.loads(response)
            prediction = response_json['product_name']
            summary = response_json['summary']
            explanation = response_json['explanation']
        except Exception as e:
            print(f"[Worker] Json parse error: {e}. Using the original response instead")
            prediction = response
            
        correct, overlap = LCSEvaluator.eval(mnode_product, prediction, 0.5)
        
        total += 1
        correct_sum += correct
        
        results += [{
            "sr": mnode_sr,
            "product_name": mnode_product,
            "prediction": prediction,
            "explanation": explanation,
            "summary": summary,
            "overlap": overlap,
            "correct": correct,
        }]
        
    accuracy = correct_sum / total
    save_file_path = f"{config['model_name']}_{accuracy}.csv"
    save_results(pd.DataFrame.from_dict(results), save_file_path)
    print(f"[Worker] Finished. Please check the result at '{save_file_path}'.")


if __name__ == "__main__":
    banner()
        
    # Step 0. Load configuration
    
    # Version: gpt-4-1106-preview
    # config = {
    #     "type": "openai",
    #     "chunk_size": 12000,
    #     "chunk_overlap": 500,
    #     "model_name": "gpt-4-1106-preview",
    #     "openai_api_key": "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",
    #     "fields": ["notes", "symptom", "description"],
    # }
    
    # Version: gpt-3.5-turbo-1106
    # config = {
    #     "type": "openai",
    #     "chunk_size": 12000,
    #     "chunk_overlap": 500,
    #     "model_name": "gpt-3.5-turbo-1106",
    #     "openai_api_key": "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",
    #     "fields": ["notes"],
    # }
    
    # Version Llama-70b
    config = {
        "type": "llama",
        "chunk_size": 2048,
        "chunk_overlap": 256,
        "model_name": "Llama-70b",
        "service_url": 'http://127.0.0.1:8080',
        "fields": ["notes", "symptom", "description", "summary"],
    }
    
    # Step 1. Load graph handler
    graph_handler = CiscoGraph("bolt://10.245.89.103:7687", "neo4j", "yyids123")
    
    # Step 2. Load llm handler
    llm_caller = None
    if config["type"] == "openai":
        llm_caller = OpenAICaller(config)
    elif config["type"] == "llama":
        llm_caller = LlamaCaller(config)
    else:
        raise NotImplementedError(f'Unknown Type [{config["type"]}]')
    
    # Step 3. Let's go
    worker(graph_handler, llm_caller, config)
    