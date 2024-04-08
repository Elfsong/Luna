
# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "3"
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from langchain.text_splitter import TokenTextSplitter



device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Caller(object):
    def __init__(self, config, console=None) -> None:
        self.config = config
        self.console = console
        self.text_splitter = TokenTextSplitter(chunk_size=config['chunk_size'], chunk_overlap=config['chunk_overlap'])
            
    def call(self, prompt: str) -> str:
        raise NotImplementedError("Don't call the interface directly")
    
    def product_analysis(self, docs: str, question: str, choice_list, status=None) -> str:
        raise NotImplementedError("Don't call the interface directly")
    
    def software_analysis(self, docs: str, question: str, choice_list, status=None) -> str:
        raise NotImplementedError("Don't call the interface directly")

class OpenAICaller(Caller):
    def __init__(self, config, console) -> None:
        super().__init__(config, console)
        self.client = OpenAI(api_key=config['openai_api_key'])
        
    
    def call(self, prompt) -> str:
        response = self.client.chat.completions.create(
            model=self.config['model_name'],
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a helpful Cisco assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    def product_analysis(self, docs, question, choice_list, status=None) -> str:
        chunks = list()
        assert isinstance(docs, list)
        
        # Step 0. split docs into chunks
        for doc in docs:
            chunks += self.text_splitter.split_text(doc)
        if self.console:
            self.console.log(f"Document input length: {len(doc)}, which has been split into {len(chunks)} chunks.")
            
        # Step 1. map these chunks
        map_results = list()
        for index, chunk in enumerate(chunks):
            if status:
                status.update(f"[bold green] Mapping chunk [{index+1}/{len(chunks)}]...")
            
            # MCQ Switch
            if choice_list:
                map_prompt = f'Question: {question} \n \
                    The ONLY product_name should be selected from the given product list: {choice_list} \
                    Response in this JSON format: \n {{"product_name": "","explanation": "", "summary": ""}} \n {chunk}'
            else:
                map_prompt = f'Question: {question} \n \
                    Response in this JSON format: \n {{"product_name": "","explanation": "", "summary": ""}} \n {chunk}'
                    
            result = self.call(map_prompt)
            map_results.append(result)
        # Step 2. reduce these results        
        reduce_results = map_results[::-1]
        while True:
            if status:
                status.update(f"[bold green] Reducing chunks from {len(reduce_results)} -> 1...")
            if len(reduce_results) == 1: break
            
            reduce_result_str = ""
            while reduce_results and len(self.text_splitter.split_text(reduce_result_str)) <= 1:
                reduce_result_str += reduce_results.pop()
            
            reduce_prompt = f'Question: {question} \n \
                Response in this JSON format: \n {{"product_name": "","explanation": "", "summary": ""}} \n {reduce_result_str}'
                
            reduce_results.append(self.call(reduce_prompt))
            
        return reduce_results[0]
    
    def software_analysis(self, docs, question, choice_list, status=None) -> str:
        chunks = list()
        assert isinstance(docs, list)
        
        # Step 0. split docs into chunks
        for doc in docs:
            chunks += self.text_splitter.split_text(doc)
        if self.console:
            self.console.log(f"Document input length: {len(doc)}, which has been split into {len(chunks)} chunks.")
            
        # Step 1. map these chunks
        map_results = list()
        for index, chunk in enumerate(chunks):
            if status:
                status.update(f"[bold green] Mapping chunk [{index+1}/{len(chunks)}]...")
            
            # MCQ Switch
            if choice_list:
                map_prompt = f'Question: {question} \n \
                    The ONLY software version should be selected from the given software version list: {choice_list} \
                    Response in this JSON format: \n {{"software_version": "","explanation": "", "summary": ""}} \n {chunk}'
            else:
                map_prompt = f'Question: {question} \n \
                    Response in this JSON format: \n {{"software_version": "","explanation": "", "summary": ""}} \n {chunk}'
                    
            result = self.call(map_prompt)
            map_results.append(result)

        # Step 2. reduce these results        
        reduce_results = map_results[::-1]
        while True:
            if status:
                status.update(f"[bold green] Reducing chunks from {len(reduce_results)} -> 1...")
            if len(reduce_results) == 1: break
            
            reduce_result_str = ""
            while reduce_results and len(self.text_splitter.split_text(reduce_result_str)) <= 1:
                reduce_result_str += reduce_results.pop()
            
            reduce_prompt = f'Question: {question} \n \
                Response in this JSON format: \n {{"software_version": "","explanation": "", "summary": ""}} \n {reduce_result_str}'
                
            reduce_results.append(self.call(reduce_prompt))
            
        return reduce_results[0]
    
class LocalCaller(Caller):
    def __init__(self, config, console=None) -> None:
        super().__init__(config, console)
        self.tokenizer = AutoTokenizer.from_pretrained(config['model_path'],local_files_only=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(config['model_path'],local_files_only=True).to(device)
            
    def call(self, prompt) -> str:
        self.model.eval()
        with torch.no_grad():
            ids = self.tokenizer.encode(prompt, return_tensors="pt").to(device, dtype = torch.long)
            generated_ids = self.model.generate(input_ids = ids,max_length= 20)
            preds = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        response = preds.strip()
        return response