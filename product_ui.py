# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 12/03/2024


import json
import time
import argparse
import pandas as pd
import streamlit as st
from rich.progress import track
from rich.console import Console
from src.graph import CiscoGraph
from src.caller import OpenAICaller, TGICaller
from src.evaluator import LCSEvaluator, SDASEvaluator
from src.utils import get_product_mapping, get_swv_mapping, save_results, banner, config_generator, load_metadata, load_notes


# Title
st.set_page_config(page_title="Luna", page_icon='🌘')
st.header('🌘 Luna - Product Name Prediction Demo', divider='rainbow')

# Status Initialization
if "sr" not in st.session_state:
    st.session_state.config = None
    st.session_state.sr = '12345'
    st.session_state.metadata = None
    st.session_state.casenote = None
    st.session_state.step = 0
    st.session_state.graph_handler = None
    st.session_state.p_mapping = None
    st.session_state.gold_nodes = None
    st.session_state.casenotes = None
    st.session_state.context = None
    st.session_state.llm_caller = None
    
st.markdown('#### Step 1. Resource Initialization')

# Config
with st.spinner('Loading configuration...'):
    if not st.session_state.config:
        with open("./config/gpt-4.json", 'r') as config_f:
            st.session_state.config = json.load(config_f)
        time.sleep(1)
st.success('Configuration Loaded!', icon="✅")

with st.spinner('Loading the Graph Handler...'):
    if not st.session_state.graph_handler:
        st.session_state.graph_handler = CiscoGraph(st.session_state.config['graph_url'], st.session_state.config['graph_user'], st.session_state.config['graph_pwd'])
        time.sleep(2)
st.success('Graph Handler Initialized!', icon="✅")

with st.spinner('Loading the LLM Caller...'):
    if not st.session_state.llm_caller:
        st.session_state.llm_caller = OpenAICaller(st.session_state.config, console=None)
        time.sleep(2)
st.success('LLM Caller Initialized!', icon="✅")

with st.spinner('Loading product mapping file...'):
    if not st.session_state.p_mapping:
        st.session_state.p_mapping = get_product_mapping('./data/tech_subtech_pnames.xlsx')
        time.sleep(1)
st.success('Product Mapping File Loaded!', icon="✅")

with st.spinner('Retrieving nodes from the graph...'):
    if not st.session_state.gold_nodes:
        node_results = st.session_state.graph_handler.raw_excute("MATCH (m:Gold) RETURN m")
        st.session_state.gold_nodes = dict()
        for node in node_results:
            node_data = node['m']
            st.session_state.gold_nodes[node_data['sr']] = node_data
        time.sleep(1)
st.success(f'Got {len(st.session_state.gold_nodes)} nodes from the graph!', icon="✅")

# SR
st.markdown('#### Step 2. SR Selection')
time.sleep(2)
sr_id = st.selectbox('Which SR you would like to proceed?', tuple(st.session_state.gold_nodes.keys()))
st.session_state.metadata = st.session_state.gold_nodes[sr_id]

# Case Notes
st.markdown('#### Step 3. Case Note Retrieval')
with st.spinner('Loading Case Notes...'):
    time.sleep(1)
    sr_str = st.session_state.metadata["sr"]
    st.session_state.casenotes = st.session_state.graph_handler.raw_excute(f"MATCH (m:Metadata) WHERE (m.sr = '{sr_str}') MATCH ((m)-[:Has]->(n)) RETURN n")
    
    notes = list()
    for nnode in st.session_state.casenotes:
        nnode_data = nnode["n"]
        if 'extracted_note' in nnode_data:
            note_content = nnode_data["extracted_note"]
            notes += [note_content]

    context = ""
    option_list = ['notes', 'symptom', 'description', 'summary']
    
    if "notes" in option_list:
        context += "\n".join(notes)
    if "symptom" in option_list:
        context += "\n" + st.session_state.metadata["Customer_Symptom__c"]
    if "description" in option_list:
        context += "\n" + st.session_state.metadata["Description"]
    if "summary" in option_list:
        context += "\n" + st.session_state.metadata["Resolution_Summary__c"]
    
    st.session_state.context = context

st.success(f'Case Note [{len(st.session_state.casenotes)}] Loaded!', icon="✅")
st.session_state.casenotes = st.data_editor(st.session_state.casenotes, use_container_width=True)

st.markdown('#### Step 4. Product Mapping')
time.sleep(1)
node_tech = st.session_state.metadata["Technology_Text__c"]
node_subtech = st.session_state.metadata["Sub_Technology_Text__c"]
st.markdown(f"""
        * **Technology:** {node_tech}
        * **Sub_Technology:** {node_subtech}
    """)
p_list = st.session_state.p_mapping[node_tech][node_subtech]
new_p_list = st.multiselect('MCQ Product Mapping', p_list, p_list)
p_str = "/ ".join(new_p_list)

# Metadata
st.markdown('#### Step 5. Metadata Collection')
with st.spinner('Metadata Processing...'):
    time.sleep(3)
    st.session_state.metadata = st.data_editor(st.session_state.metadata, use_container_width=True)

st.markdown('#### Step 6. Product Name Inference')
with st.spinner('Predicting...'):
    question = f'Which product is principally discussed in these documents?'
    response = st.session_state.llm_caller.product_analysis([st.session_state.context], question, p_str)

    prediction, summary, explanation = "", "", ""
    try:
        response_json = json.loads(response)
        prediction = response_json['product_name']
        summary = response_json['summary']
        explanation = response_json['explanation']
    except Exception as e:
        prediction = response
        
    mnode_product = st.session_state.metadata["Product_Name__c"]
    correct, overlap = LCSEvaluator.eval(mnode_product, prediction, 0.5)

    st.markdown(f"""
        * **Prediction:** {prediction}
        * **Explanation:** {explanation}
        * **Summary:** {summary}
    """)

if correct:
    st.success(f'Ground Truth: [{mnode_product}] Prediction: [{prediction}] Overlap: [{overlap}]')
    st.balloons()
else:
    st.error(f'Ground Truth: [{mnode_product}] Prediction: [{prediction}] Overlap: [{overlap}]')








    