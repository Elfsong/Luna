import json
import time
import argparse
import pandas as pd
from rich.progress import track
from rich.console import Console
from src.filter import Filter
from src.graph import CiscoGraph
from src.caller import OpenAICaller, TGICaller
from src.evaluator import LCSEvaluator, SDASEvaluator
from src.utils import get_product_mapping, get_swv_mapping, save_results, banner, config_generator, load_metadata, load_notes

def graph_worker(console, graph_handler, config):
    metadata = load_metadata(config["graph_metadata"])
    notes = load_notes(config['graph_notes'])

    graph_handler.node_delete_all()
    # Loding Metadata
    for instance in track(metadata, description="Loading metadata to Neo4J..."):
        graph_handler.node_create(node_type="Metadata", node_attributes=instance.to_cypher())
    
    # Loading Notes
    for instance in track(notes, description="Loading notes to Neo4J..."):
        note_node = graph_handler.node_create(node_type="Note", node_attributes=instance.to_cypher())
        note_node_id = note_node.element_id
        sr_node_id = graph_handler.node_id_query("Metadata", "sr", instance.sr_uuid)
        graph_handler.edge_create(sr_node_id, note_node_id, "Has", {})
    
    # Assign Gold Nodes
    graph_handler.add_gold_set()
    
    console.log("Data Loaded Successfully!")

def general_worker(console, graph_handler, caller, config):
    graph_worker(console, graph_handler,config)
    with console.status("[bold green] Loading software version mapping file...") as status:
        s_mapping = get_swv_mapping('./data/tech_subtech_swv.xlsx')
        time.sleep(3)
        console.log(f'Software version mapping file loaded.')

    with console.status("[bold green] Loading product mapping file...") as status:
        p_mapping = get_product_mapping('./data/tech_subtech_pnames.xlsx')
        time.sleep(3)
        console.log(f'Product mapping file loaded.')

    with console.status("[bold green] Loading NN Filter...") as status:
        filter = Filter(config,console)
        time.sleep(3)
        console.log(f'filter loaded.')
    
    with console.status("[bold green]Retrieving nodes from the graph...") as status:
        if config['test_sr'] == []:
            mnodes = graph_handler.raw_excute("MATCH (m:Metadata) WHERE (m)--() RETURN m")
        else:
            mnodes = graph_handler.raw_excute("MATCH (m:Metadata) WHERE m.sr IN " + str(config['test_sr']) + " RETURN m")
        time.sleep(3)
        console.log(f"Got {len(mnodes)} nodes from the graph.")
    
    results = list()
    total, correct_sum, correct_sum_p = 0, 0, 0
    valid_total = 0
    
    with console.status("[bold green] Node Processing...") as status:
        for index, mnode in enumerate(mnodes):
            console.log("=" * 30)
            mnode_data = mnode["m"]
            mnode_sr = mnode_data["sr"]
            if config["eval"]:
                mnode_swv = mnode_data["SW_Version__c"]
                mnode_product = mnode_data["Product_Name__c"]
            mnode_tech = mnode_data["Technology_Text__c"]
            mnode_subtech = mnode_data["Sub_Technology_Text__c"]
            s_list = s_mapping[mnode_tech][mnode_subtech]
            s_str = "/ ".join(s_list)
            p_list = p_mapping[mnode_tech][mnode_subtech]
            p_str = "/ ".join(p_list)
            
            notes = list()  
            sw_notes = list()
            nnodes = graph_handler.raw_excute(f"MATCH (m:Metadata) WHERE (m.sr = '{mnode_sr}') MATCH ((m)-[:Has]->(n)) RETURN n")
            
            for nnode in nnodes:
                nnode_data = nnode["n"]
                if 'extracted_note' not in nnode_data:
                    nnode_data['extracted_note'] = nnode_data['Note__c']
                note_content = nnode_data["extracted_note"]
                if filter.filter_by_local_classifier(note_content, s_list):
                    sw_notes +=[note_content]
                notes += [note_content]
            
            if len(sw_notes) == 0:
                sw_notes=  notes
            doc,doc_sw = "" , ""
            if "notes" in config["fields"]:
                doc += "\n".join(notes)
                doc_sw += "\n".join(sw_notes)
            if "symptom" in config["fields"]:
                doc += "\n" + mnode_data["Customer_Symptom__c"]
                doc_sw += "\n" + mnode_data["Customer_Symptom__c"]
            if "description" in config["fields"]:
                doc += "\n" + mnode_data["Description"]
                doc_sw += "\n" + mnode_data["Description"]
            if "summary" in config["fields"]:
                doc += "\n" + mnode_data["Resolution_Summary__c"]
                doc_sw += "\n" + mnode_data["Resolution_Summary__c"]



            if config['mcq']:
                question = f'Which product is principally discussed in these documents?'
                console.log(f"Current node {mnode_sr} [{index+1}/{len(mnodes)}]")
                response_p = caller.product_analysis([doc], question, p_str, status)
            else:
                question = f'What product is principally discussed in these documents?'
                console.log(f"Current node {mnode_sr} [{index+1}/{len(mnodes)}]")
                response_p = caller.product_analysis([doc], question, None, status)
            
            # question = f'Which software version of {mnode_product} is principally discussed in these documents? Answer "None" if you cannot find answer in the given documents.'
            question = f'Which software version is principally discussed in these documents?'
            
            response = caller.software_analysis([doc_sw], question, s_str, status)
            
            prediction, summary, explanation = "", "", ""
            try:
                response_json = json.loads(response)
                prediction = response_json['software_version']
                summary = response_json['summary']
                explanation = response_json['explanation']
            except Exception as e:
                console.log(f"[bold red] [Worker] Json parse error: {e}. Using the original response instead.")
                prediction = response

            prediction_p, summary_p, explanation_p = "", "", ""
            try:
                response_json_p = json.loads(response_p)
                prediction_p = response_json_p['product_name']
                summary_p = response_json_p['summary']
                explanation_p = response_json_p['explanation']
            except Exception as e:
                console.log(f"[bold red] [Worker] Json parse error: {e}. Using the original response instead.")
                prediction = response

            if config["eval"]:
                valid_sr = mnode_swv in doc
                correct = SDASEvaluator.eval(mnode_swv, prediction, 0.3)
                correct_p, overlap = LCSEvaluator.eval(mnode_product, prediction_p, 0.5)
                total += 1
                valid_total += 1 if valid_sr else 0
                correct_sum += correct
                correct_sum_p += correct_p
                
                console.log(f'Ground truth: [bold green]{mnode_swv}[/bold green] Prediction: [bold yellow]{prediction}[/bold yellow] Valid: {str(valid_sr)} Passed: {str(correct)}')
                console.log(f'Explanation: [i]{explanation}[/i]')
                console.log(f'Ground truth: [bold green]{mnode_product}[/bold green] Prediction: [bold yellow]{prediction_p}[/bold yellow] Overlap: {overlap} Passed: {str(correct_p)}')
                console.log(f'Explanation: [i]{explanation_p}[/i]')
                
                results += [{
                    "sr": mnode_sr,
                    "software_version": mnode_swv,
                    "product_name": mnode_product,
                    "prediction_sw": prediction,
                    "explanation_sw": explanation,
                    "valid_sr": valid_sr,
                    "summary": summary,
                    "correct": correct,
                    "prediction_p": prediction_p,
                    "explanation_p": explanation_p,
                    "summary_p": summary_p,
                    "overlap": overlap,
                    "correct_sw": correct,
                    "correct_p": correct_p,
                }]
                
            else: 
                results += [{
                    "sr": mnode_sr,
                    "prediction_sw": prediction,
                    "prediction_p": prediction_p,
                    "explanation_sw": explanation,
                    "summary_sw": summary,
                    "explanation_p": explanation,
                    "summary_p": summary_p,
                }]
                console.log(f' Prediction: [bold yellow]{prediction}[/bold yellow]')
                console.log(f'Explanation: [i]{explanation}[/i]')
                console.log(f' Prediction: [bold yellow]{prediction_p}[/bold yellow]')
                console.log(f'Explanation: [i]{explanation_p}[/i]')

    
    with console.status("[bold green] Result Saving...") as status:
        
        save_file_path = f"./results/{config['model_name']}_{correct_sum}.csv"
        save_results(pd.DataFrame.from_dict(results), save_file_path)
        time.sleep(3)
        if config["eval"]:
            console.log(f"Well done. There are {valid_total} valid instances. We have {correct_sum} correct predictions. Please check the detailed result at '{save_file_path}'.")
            accuracy_sw = correct_sum / len(mnodes)
            accuracy_p = correct_sum_p / len(mnodes)
            console.log(f"The accuracy for the software version prediction is {accuracy_sw}, and the accuracy for the product name prediction is {accuracy_p}")
        else:
            console.log(f" Please check the detailed result at '{save_file_path}'.")
    graph_handler.close()

if __name__ == "__main__":
    console = Console(record=True)
    banner()
        
    # Step 1. Load Configuration
    with console.status("[bold green] Loading configuration...") as status:
        parser = argparse.ArgumentParser(description='Luna 0.2')
        parser.add_argument('--config_path', type=str,default='./config/gpt-3.json', help='Configuration File Path')
        parser.add_argument('--task', type=str,default='graph', help='Task Assigning')
        parser.add_argument('--openai_key', type=str,default=None,help="enter the openai key")
        parser.add_argument('--eval', type=bool,default=False,help="evaluate on glod SRs")
        args = parser.parse_args()
        
        if args.config_path:
            console.log(f"Config {args.config_path} detected!")
            with open(args.config_path, 'r') as config_f:
                config = json.load(config_f)
        else:
            console.log(f"No config detected. Let me ask you a few questions:)")
            config = config_generator(console)

        if args.openai_key:
            config['openai_api_key'] = args.openai_key
        if args.eval:
            config['eval'] = args.eval
    # Step 2. Load Handlers
    with console.status("[bold green] Loading components...") as status:
        # Step 2.1. Load graph handler
        graph_handler = CiscoGraph(config['graph_url'], config['graph_user'], config['graph_pwd'])
        time.sleep(3)
        console.log(f"[bold cyan]Graph Handler[/bold cyan] Load Completed!")
    
        # Step 2.2. Load llm handler
        llm_caller = None
        if config["type"] == "openai":
            llm_caller = OpenAICaller(config, console)
        elif config["type"] == "llama":
            llm_caller = TGICaller(config, console)
        else:
            raise NotImplementedError(f'Unknown Type [{config["type"]}]')
        time.sleep(3)
        console.log(f"[bold cyan]LLM Handler[/bold cyan] Load Completed!")
    
    # Step 3. Let's go
    console.log(f"[bold cyan]Worker[/bold cyan] Current task: {args.task}")
    if args.task == "graph":
        graph_worker(console, graph_handler, config)
    elif args.task == "general":
        general_worker(console, graph_handler, llm_caller, config)
    