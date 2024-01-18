# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 22/12/2023

import json
import time
import argparse
import pandas as pd
from rich.console import Console
from src.graph import CiscoGraph
from src.caller import OpenAICaller, LlamaCaller
from src.evaluator import LCSEvaluator, SDASEvaluator
from src.utils import get_product_mapping, get_swv_mapping, save_results, banner, config_generator


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

def software_worker(console, graph_handler, caller, config):
    with console.status("[bold green] Loading software version mapping file...") as status:
        s_mapping = get_swv_mapping('./data/tech_subtech_swv.xlsx')
        time.sleep(3)
        console.log(f'Software version mapping file loaded.')
    
    with console.status("[bold green]Retrieving nodes from the graph...") as status:
        mnodes = graph_handler.raw_excute("MATCH (m:Gold) RETURN m")
        time.sleep(3)
        console.log(f"Got {len(mnodes)} nodes from the graph.")
    
    results = list()
    total, correct_sum = 0, 0
    valid_total = 0
    
    with console.status("[bold green] Node Processing...") as status:
        for index, mnode in enumerate(mnodes):
            console.log("=" * 30)
            mnode_data = mnode["m"]
            mnode_sr = mnode_data["sr"]
            mnode_swv = mnode_data["SW_Version__c"]
            mnode_product = mnode_data["Product_Name__c"]
            
            mnode_tech = mnode_data["Technology_Text__c"]
            mnode_subtech = mnode_data["Sub_Technology_Text__c"]
            s_list = s_mapping[mnode_tech][mnode_subtech]
            s_str = "/ ".join(s_list)
            
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

            question = f'Which software version of {mnode_product} is principally discussed in these documents?'
            
            console.log(f"Current node {mnode_sr} [{index+1}/{len(mnodes)}]")
            
            # response = caller.software_analysis([doc], question, s_str, status)
            
            prediction, summary, explanation = "", "", ""
            # try:
            #     response_json = json.loads(response)
            #     prediction = response_json['software_version']
            #     summary = response_json['summary']
            #     explanation = response_json['explanation']
            # except Exception as e:
            #     console.log(f"[bold red] [Worker] Json parse error: {e}. Using the original response instead.")
            #     prediction = response
            
            valid_sr = mnode_swv in doc
            correct = SDASEvaluator.eval(mnode_swv, prediction, 0.2)
            
            total += 1
            valid_total += 1 if valid_sr else 0
            correct_sum += correct
            
            console.log(f'Ground truth: [bold green]{mnode_swv}[/bold green] Prediction: [bold yellow]{prediction}[/bold yellow] Valid: {str(valid_sr)} Passed: {str(correct)}')
            console.log(f'Explanation: [i]{explanation}[/i]')
            
            results += [{
                "sr": mnode_sr,
                "software_version": mnode_swv,
                "prediction": prediction,
                "explanation": explanation,
                "valid_sr": valid_sr,
                "summary": summary,
                "correct": correct,
            }]
    
    with console.status("[bold green] Result Saving...") as status:
        accuracy = correct_sum / valid_total
        save_file_path = f"./results/{config['model_name']}_{accuracy}.csv"
        save_results(pd.DataFrame.from_dict(results), save_file_path)
        time.sleep(3)
        console.log(f"Well done. There are {valid_total} valid instances. The accuracy for this run is {accuracy}. Please check the detailed result at '{save_file_path}'.")

if __name__ == "__main__":
    console = Console()
    banner()
    
    # Step 0. Load configuration
    parser = argparse.ArgumentParser(description='Luna 0.1')
    parser.add_argument('--config_path', type=str,default='./data/gpt-3.json', help='Configuration File Path')
    args = parser.parse_args()
    
    if args.config_path:
        console.log(f"Config {args.config_path} detected!")
        with open(args.config_path, 'r') as config_f:
            config = json.load(config_f)
    else:
        console.log(f"No config detected. Let me ask you a few questions:)")
        config = config_generator(console)
        
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
    # worker(console, graph_handler, llm_caller, config)
    software_worker(console, graph_handler, llm_caller, config)
    