# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 22/12/2023

import json
import time
import argparse
import pandas as pd
from rich.console import Console
from src.graph import CiscoGraph
from src.evaluator import LCSEvaluator
from src.caller import OpenAICaller, LlamaCaller
from src.utils import get_product_mapping, save_results, banner, config_generator


def worker(console, graph_handler, caller, config):
    with console.status("[bold green] Loading product mapping file...") as status:
        p_mapping = get_product_mapping('./data/tech_subtech_pnames.xlsx')
        time.sleep(3)
        console.log(f'Product mapping file loaded.')
    
    with console.status("[bold green]Retrieving nodes from the graph...") as status:
        mnodes = graph_handler.raw_excute("MATCH (m:Gold) RETURN m")
        time.sleep(3)
        console.log(f"Got {len(mnodes)} nodes from the graph.")
    
    results = list()
    total, correct_sum = 0, 0
    
    with console.status("[bold green] Node Processing...") as status:
        for index, mnode in enumerate(mnodes):
            console.log("=" * 30)
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
            
            console.log(f"Current node {mnode_sr} [{index+1}/{len(mnodes)}]")
            
            response = caller.analysis([doc], question, p_str, status)
            
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
            
            total += 1
            correct_sum += correct
            
            console.log(f'Ground truth: [bold green]{mnode_product}[/bold green] Prediction: [bold yellow]{prediction}[/bold yellow] Overlap: {overlap} Passed: {str(correct)}')
            console.log(f'Explanation: [i]{explanation}[/i]')
            
            results += [{
                "sr": mnode_sr,
                "product_name": mnode_product,
                "prediction": prediction,
                "explanation": explanation,
                "summary": summary,
                "overlap": overlap,
                "correct": correct,
            }]
    
    with console.status("[bold green] Result Saving...") as status:
        accuracy = correct_sum / total
        save_file_path = f"./results/{config['model_name']}_{accuracy}.csv"
        save_results(pd.DataFrame.from_dict(results), save_file_path)
        time.sleep(3)
        console.log(f"Well done. The accuracy for this run is {accuracy}. Please check the detailed result at '{save_file_path}'.")


if __name__ == "__main__":
    console = Console()
    banner()
    
    # Step 0. Load configuration
    parser = argparse.ArgumentParser(description='Luna 0.1')
    parser.add_argument('--config_path', type=str,default=None, help='Configuration File Path')
    args = parser.parse_args()
    
    if args.config_path:
        console.log(f"Config {args.config_path} detected!")
        with open(args.config_path, 'r') as config_f:
            config = json.load(config_f)
    else:
        console.log(f"No config detected. Let me ask you a few questions:)")
        config = config_generator(console)
        
        config = {
            "type": "llama",
            "chunk_size": 2048,
            "chunk_overlap": 256,
            "model_name": "Llama-70b",
            "llm_url": 'http://127.0.0.1:8080',
            "graph_url": 'bolt://10.245.89.103:7687',
            'graph_user': 'neo4j',
            'graph_pwd': 'yyids123',
            "fields": ["notes", "symptom", "description", "summary"],
        }
        
    with console.status("[bold green]Loading components...") as status:
        # Step 1. Load graph handler
        graph_handler = CiscoGraph(config['graph_url'], config['graph_user'], config['graph_pwd'])
        time.sleep(3)
        console.log(f"[bold cyan]Graph Handler[/bold cyan] Load Completed!")
    
        # Step 2. Load llm handler
        llm_caller = None
        if config["type"] == "openai":
            llm_caller = OpenAICaller(config, console)
        elif config["type"] == "llama":
            llm_caller = LlamaCaller(config, console)
        else:
            raise NotImplementedError(f'Unknown Type [{config["type"]}]')
        time.sleep(3)
        console.log(f"[bold cyan]LLM Handler[/bold cyan] Load Completed!")
    
    # Step 3. Let's go
    worker(console, graph_handler, llm_caller, config)
    