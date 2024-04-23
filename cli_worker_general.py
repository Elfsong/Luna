import json
import time
import argparse
import pandas as pd
from rich.progress import track
from rich.console import Console
from src.filter import Filter
from src.caller import OpenAICaller
from src.evaluator import LCSEvaluator, SDASEvaluator
from src.utils import get_product_mapping, get_swv_mapping, save_results, banner, config_generator, get_sr_data, get_price, create_summary

def general_worker(console, caller, config):
    with console.status("[bold green] Loading software version mapping file...") as status:
        cm, cn = get_sr_data(config["filepath_metadata"], config['filepath_notes'])
        time.sleep(3)
        console.log(f'Metadata & Case notes file loaded.')
    
    with console.status("[bold green] Loading software version mapping file...") as status:
        s_mapping, swv_map = get_swv_mapping(config["tech_subtech_sw_map"])
        time.sleep(3)
        console.log(f'Software version mapping file loaded.')

    with console.status("[bold green] Loading product mapping file...") as status:
        p_mapping = get_product_mapping(config["tech_subtech_pnames_map"])
        time.sleep(3)
        console.log(f'Product mapping file loaded.')

    with console.status("[bold green] Loading NN Filter...") as status:
        filter = Filter(config,console)
        time.sleep(3)
        console.log(f'filter loaded.')
    garbage = list()
    with console.status("[bold green]Retrieving metadata from the file...") as status:
        if config['test_sr'] == []:
            mnodes = cm
        else:
            mnodes = {}
            for x in config['test_sr']:
                try:
                    mnodes[x] = cm[x]
                #mnodes = {x:cm[x] for x in config['test_sr']}
                except:
                    console.log(f"The SR with ID: {x} does not exist in the metadata file provided, and will be ignored")
                    garbage.append(x)
                    pass
        time.sleep(3)
        console.log(f"Got {len(mnodes)} nodes from the file.")
    
    results = list()
    total, correct_sum, correct_sum_p = 0, 0, 0
    total_price_p , total_price_sw = 0 ,0
    total_price_reduced_p , total_price_reduced_sw = 0 ,0
    valid_total = 0
    with console.status("[bold green] Node Processing...") as status:
        for index, mnode in enumerate(mnodes):
            console.log("=" * 30)

            mnode_data = mnodes[mnode]
            mnode_sr = mnode
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
            p_notes = list()
            sw_notes = list()
            nnodes = cn[mnode]
            
            for nnode in nnodes:
                if 'extracted_note' in nnode:
                    if nnode['extracted_note'] is None:
                        nnode['extracted_note'] = nnode['Note__c']
                    note_content = nnode["extracted_note"]
                else:
                    note_content=nnode['Note__c']
                if filter.filter_by_local_classifier(note_content, s_list,False):
                    sw_notes +=[note_content]
                if filter.filter_by_local_classifier(note_content, p_list,True):
                    p_notes +=[note_content]
                notes += [note_content]
                
            if len(sw_notes) == 0:
                sw_notes=  notes
            
            doc, doc_sw, doc_p = "" , "", ""


            if config["include_notes"]:
                doc += "\n".join(notes)
                doc_sw += "\n".join(sw_notes)
                doc_p += "\n".join(p_notes)
            for field in config["fields"]:
                doc += "\n" + mnode_data[field]
                doc_sw += "\n" + mnode_data[field]
                doc_p += "\n" + mnode_data[field]



            if config['mcq']:
                question = f'Which product is principally discussed in these documents?'
                console.log(f"Current node {mnode_sr} [{index+1}/{len(mnodes)}]")
                response_p, price_p, num_tokens_p = caller.product_analysis([doc_p], question, p_str, status)
            else:
                question = f'What product is principally discussed in these documents?'
                console.log(f"Current node {mnode_sr} [{index+1}/{len(mnodes)}]")
                response_p, price_p, num_tokens_p = caller.product_analysis([doc_p], question, None, status)
            
            # question = f'Which software version of {mnode_product} is principally discussed in these documents? Answer "None" if you cannot find answer in the given documents.'
            question = f'Which software version is principally discussed in these documents?'
            
            response, price_sw, num_tokens_sw = caller.software_analysis([doc_sw], question, s_str, status)

            price_original_sw, num_tokens_original_sw = get_price(config["model_name"],f'Question: {question} \n \
                    The ONLY software version should be selected from the given software version list: {s_str} \
                    Response in this JSON format: \n {{"software_version": "","explanation": "", "summary": ""}} \n {doc}')
            
            price_original_p, num_tokens_original_p = get_price(config["model_name"],f'Question: {question} \n \
                    The ONLY product name should be selected from the given product name list: {p_str} \
                    Response in this JSON format: \n {{"product_name": "","explanation": "", "summary": ""}} \n {doc}')
            
            total_price_sw = total_price_sw + price_original_sw
            total_price_p = total_price_p + price_original_p
            total_price_reduced_sw = total_price_reduced_sw + price_sw
            total_price_reduced_p = total_price_reduced_p + price_p

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
                prediction_p = response_p

            if config["eval"]:
                valid_sr = mnode_swv in doc_p
                correct = SDASEvaluator.eval(swv_map[mnode_swv], prediction, 0.2)
                correct_p, overlap = LCSEvaluator.eval(mnode_product, prediction_p, 0.5)
                total += 1
                valid_total += 1 if valid_sr else 0
                correct_sum += correct
                correct_sum_p += correct_p
                
                console.log(f'Ground truth: [bold green]{swv_map[mnode_swv]}[/bold green] Prediction: [bold yellow]{prediction}[/bold yellow] Valid: {str(valid_sr)} Passed: {str(correct)}')
                console.log(f'Explanation: [i]{explanation}[/i]')
                console.log(f'Ground truth: [bold green]{mnode_product}[/bold green] Prediction: [bold yellow]{prediction_p}[/bold yellow] Overlap: {overlap} Passed: {str(correct_p)}')
                console.log(f'Explanation: [i]{explanation_p}[/i]')
                
                results += [{
                    "sr": mnode_sr,
                    "software_version": mnode_swv,
                    "product_name": mnode_product,
                    "prediction_sw": prediction,
                    "explanation_sw": explanation,
                    "summary_sw": summary,
                    "valid_sr_sw": valid_sr,
                    "correct_sw": correct,
                    "num_tokens_sw": num_tokens_sw,
                    "price_sw" : price_sw,
                    "original_price_sw" : price_original_sw,
                    "original_num_tokens_sw" : num_tokens_original_sw,
                    "prediction_p": prediction_p,
                    "explanation_p": explanation_p,
                    "summary_p": summary_p,
                    "overlap": overlap,
                    "correct_p": correct_p,
                    "num_tokens_p": num_tokens_p,
                    "price_p" : price_p,
                    "original_price_p" : price_original_p,
                    "original_num_tokens_p" : num_tokens_original_p,
                }]
                
            else: 
                results += [{
                    "sr": mnode_sr,
                    "prediction_sw": prediction,
                    "explanation_sw": explanation,
                    "summary_sw": summary,
                    "num_tokens_sw": num_tokens_sw,
                    "price_sw" : price_sw,
                    "original_price_sw" : price_original_sw,
                    "original_num_tokens_sw" : num_tokens_original_sw,
                    "prediction_p": prediction_p,
                    "explanation_p": explanation,
                    "summary_p": summary_p,
                    "num_tokens_p": num_tokens_p,
                    "price_p" : price_p,
                    "original_price_p" : price_original_p,
                    "original_num_tokens_p" : num_tokens_original_p,
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
            console.log(f"Well done. There are {valid_total} valid instances. We have {correct_sum} correct predictions out of the {len(mnodes)} SRs. Please check the detailed result at '{save_file_path}'.")
            if len(garbage)!=0:
                console.log(f"Found in the test_sr list invalid SR(s) that are not mentioned in the metadata file: {garbage}.")
            accuracy_sw = round(100*correct_sum / len(mnodes),2)
            accuracy_p = round(100*correct_sum_p / len(mnodes),2)
            console.log(f"The accuracy for the software version prediction is {accuracy_sw}%, and the accuracy for the product name prediction is {accuracy_p}%")
            console.log(f"Using the filter saved us {round(total_price_p-total_price_reduced_p,3)}$ on product name prediction, and {round(total_price_sw-total_price_reduced_sw,3)}$ on software version prediction. \
                        These saving translate to {round(100*(total_price_p-total_price_reduced_p)/total_price_p,2)}% of the original cost of product name prediction, and {round(100*(total_price_sw-total_price_reduced_sw)/total_price_sw,2)}% of the original cost of software version prediction. ")
            conetent = f"Well done. There are {valid_total} valid instances. We have {correct_sum} correct predictions out of the {len(mnodes)} SRs. Please check the detailed result at '{save_file_path}'. \n\
Found in the test_sr list invalid SR(s) that are not mentioned in the metadata file: {garbage}. \n\
The accuracy for the software version prediction is {accuracy_sw}%, and the accuracy for the product name prediction is {accuracy_p}% \n\
Using the filter saved us {round(total_price_p-total_price_reduced_p,3)}$ on product name prediction, and {round(total_price_sw-total_price_reduced_sw,3)}$ on software version prediction.  \n\
These saving translate to {round(100*(total_price_p-total_price_reduced_p)/total_price_p,2)}% of the original cost of product name prediction, and {round(100*(total_price_sw-total_price_reduced_sw)/total_price_sw,2)}% of the original cost of software version prediction.\n "
            create_summary('summary.txt', conetent)

        else:
            console.log(f"Using the filter saved us {round(total_price_p-total_price_reduced_p,3)}$ on product name prediction, and {round(total_price_sw-total_price_reduced_sw,3)}$ on software version prediction. these saving translate to {round(100*(total_price_p-total_price_reduced_p)/total_price_p,2)}% of the original cost of product name prediction, and {round(100*(total_price_sw-total_price_reduced_sw)/total_price_sw,2)}% of the original cost of software version prediction. ")
            console.log(f"Please check the detailed result at '{save_file_path}'.")
            conetent = f"Using the filter saved us {round(total_price_p-total_price_reduced_p,3)}$ on product name prediction, and {round(total_price_sw-total_price_reduced_sw,3)}$ on software version prediction.  \n \
These saving translate to {round(100*(total_price_p-total_price_reduced_p)/total_price_p,2)}% of the original cost of product name prediction, and {round(100*(total_price_sw-total_price_reduced_sw)/total_price_sw,2)}% of the original cost of software version prediction.\n \
Please check the detailed result at '{save_file_path}'."
            create_summary('summary.txt', conetent)

if __name__ == "__main__":
    console = Console(record=True)
    banner()
        
    # Step 1. Load Configuration
    with console.status("[bold green] Loading configuration...") as status:
        parser = argparse.ArgumentParser(description='Luna 0.2')
        parser.add_argument('--config_path', type=str,default='./config/gpt-3.json', help='Configuration File Path')
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
        #  Load llm handler
        llm_caller = OpenAICaller(config, console)
        time.sleep(3)
        console.log(f"[bold cyan]LLM Handler[/bold cyan] Load Completed!")
    
    # Step 3. Let's go
    general_worker(console, llm_caller, config)
    
