# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 29/12/2023

from openai import OpenAI
from rich.progress import track
from huggingface_hub import InferenceClient
from langchain.text_splitter import TokenTextSplitter

class Caller(object):
    def __init__(self, config, console) -> None:
        self.config = config
        self.console = console
        self.text_splitter = TokenTextSplitter(chunk_size=config['chunk_size'], chunk_overlap=config['chunk_overlap'])
            
    def call(self, prompt) -> str:
        raise NotImplementedError("Don't call the interface directly")
    
    def analysis(self, docs, question, choice_list) -> str:
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
    
    def analysis(self, docs, question, choice_list) -> str:
        chunks = list()
        assert isinstance(docs, list)
        
        # Step 0. split docs into chunks
        for doc in docs:
            chunks += self.text_splitter.split_text(doc)
            
        # Step 1. map these chunks
        map_results = list()
        for chunk in chunks:
            map_prompt = f'Question: {question} \n \
                The ONLY product_name should be selected from the given product list: {choice_list} \
                Response in this JSON format: \n {{"product_name": "","explanation": "", "summary": ""}} \n {chunk}'
            result = self.call(map_prompt)
            map_results.append(result)
            
        # Step 2. reduce these results        
        reduce_results = map_results[::-1]
        while True:
            if len(reduce_results) == 1: break
            
            reduce_result_str = ""
            while reduce_results and len(self.text_splitter.split_text(reduce_result_str)) <= 1:
                reduce_result_str += reduce_results.pop()
            
            reduce_prompt = f'Question: {question} \n \
                Response in this JSON format: \n {{"product_name": "","explanation": "", "summary": ""}} \n {reduce_result_str}'
                
            reduce_results.append(self.call(reduce_prompt))
            
        return reduce_results[0]
    
class LlamaCaller(Caller):
    def __init__(self, config, console) -> None:
        super().__init__(config, console)
        self.client = InferenceClient(model=config['llm_url'])
    
    def call(self, prompt) -> str:
        response = self.client.text_generation(prompt=prompt, max_new_tokens=1024, stop_sequences=['\n\n', '"}'])
        response = response.strip()
        return response
    
    def analysis(self, docs, question, choice_list, status) -> str:
        chunks = list()
        assert isinstance(docs, list)
        
        # Step 0. split docs into chunks
        for doc in docs:
            chunks += self.text_splitter.split_text(doc)
        self.console.log(f"Document input length: {len(doc)}, which has been split into {len(chunks)} chunks.")
            
        # Step 1. map these chunks
        map_results = list()
        for index, chunk in enumerate(chunks):
            status.update(f"[bold green] Mapping chunk [{index+1}/{len(chunks)}]...")
            map_prompt = f'Question: {question} \n \
                The ONLY product_name should be selected from the given product list: {choice_list} \
                Response in this JSON format: \n {{"product_name": "","explanation": "<less_than_50_words>", "summary": "<less_than_50_words>"}} \n {chunk} \n \
                Response:\n'
            result = self.call(map_prompt)
            map_results.append(result)
            
            
        # Step 2. reduce these results 
        reduce_results = map_results[::-1]
        while True:
            status.update(f"[bold green] Reducing chunks from {len(reduce_results)} -> 1...")
            if len(reduce_results) == 1: break
            
            reduce_result_str = ""
            while reduce_results and len(self.text_splitter.split_text(reduce_result_str)) <= 1:
                reduce_result_str += reduce_results.pop()
            
            reduce_prompt = f'Given the following results, answer this question: {question} \n \
                {reduce_result_str} \n \
                Response ONLY one JSON in this format: \n {{"product_name": "<product_name>","explanation": "<less_than_50_words>", "summary": "<less_than_50_words>"}} \n \
                Response:\n'
            
            result = self.call(reduce_prompt)
            reduce_results.append(result)
            
        return reduce_results[0]
    
    
    
    
    