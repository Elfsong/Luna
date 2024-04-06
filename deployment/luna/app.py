# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 06/04/2024

import time
import streamlit as st

import src.utils as uts
from src.filter import Filter
from src.caller import OpenAICaller
from src.evaluator import LCSEvaluator, NewSDASEvaluator

# Title
st.set_page_config(page_title="Luna", page_icon='🌙')
st.title('Hello, welcome to Luna 🌙')


# Status Initialization
if "config" not in st.session_state:
    st.session_state.config = None
    st.session_state.current_step = 0
    st.session_state.current_sr = None
    st.session_state.current_metadata = None
    st.session_state.current_notes = None
    st.session_state.metadata = None
    st.session_state.notes = None
    st.session_state.context = None
    st.session_state.llm_caller = None
    st.session_state.filter = None
    st.session_state.openai_api_key = None
    st.session_state.p_mapping = None
    st.session_state.s_mapping = None
    

# Information Initialization
st.markdown('#### Step 1. Information Initialization')

# OpenAI Token
st.session_state.openai_api_key = st.text_input(label='OpenAI Token', value='sk-XXXXXXXXXXXXX')

# Filter URL
st.session_state.filter_url = st.text_input(label="Filter URL (Empty it if you don't need the NN filter)", value='http://10.246.112.13:9001')

# Data
metadata_f = st.file_uploader("Choose the Metadata file (Don't choose if you wanna use the default config:)")
notes_f = st.file_uploader("Choose the Notes file (Don't choose if you wanna use the default config:)")

# Filter Options
with st.container():
    st.write("Filter Options")
    col1, col2 = st.columns([1, 1])
    regex_filter_switch = col1.checkbox('Enable Regex Filter')
    nn_filter_switch = col2.checkbox('Enable NN Filter')

if st.button("Confirm and Proceed", type="primary", key="information_checked_btn"):
    st.session_state.current_step = 1
    
# Resource Initialization
if st.session_state.current_step > 0:
    st.markdown('#### Step 2. Resource Initialization')
    with st.status("Resource Initialization..."):
        if not st.session_state.config:
            st.write("Loading configuration...")
            st.session_state.config = uts.get_config()
            st.session_state.config['openai_api_key'] = st.session_state.openai_api_key
            time.sleep(1)
        st.write("Configuration Loaded.")

        if not st.session_state.llm_caller:
            st.write("Loading LLM Caller...")
            st.session_state.llm_caller = OpenAICaller(st.session_state.config, console=None)
            time.sleep(2)
        st.write("LLM Caller Loaded.")
        
        if not st.session_state.filter:
            st.write("Loading Filter...")
            st.session_state.config['local_llm_url'] = st.session_state.filter_url
            st.session_state.filter = Filter(st.session_state.config) if st.session_state.filter_url else None
            time.sleep(2)
        st.write("Filter Loaded.")

        if not st.session_state.p_mapping:
            st.write("Loading P Mapping...")
            st.session_state.p_mapping = uts.get_p_mapping(st.session_state.config['p_mapping'])
            time.sleep(2)
        st.write("P Mapping Loaded.")
            
        if not st.session_state.s_mapping:
            st.write("Loading S Mapping...")
            st.session_state.s_mapping = uts.get_s_mapping(st.session_state.config['s_mapping'])
            time.sleep(2)
        st.write("S Mapping Loaded.")
        
        if not st.session_state.metadata or st.session_state.notes:
            st.write("Loading Raw Case_Metadata/Notes Data...")
            metadata_f = open(st.session_state.config["metadata_file"], "r") if not metadata_f else metadata_f
            notes_f = open(st.session_state.config["notes_file"], "r") if not notes_f else notes_f
            st.session_state.metadata, st.session_state.notes = uts.get_sr_data(metadata_f, notes_f)
        st.write("Raw Case_Metadata/Notes Data Loaded.")
        
        st.session_state.current_step = 2

    
# SR Selection
if st.session_state.current_step > 1:
    st.markdown('#### Step 3. SR Selection')
    sr_id = st.selectbox('Which SR you would like to proceed?', tuple(st.session_state.metadata.keys()))
    st.session_state.current_metadata = st.session_state.metadata[sr_id]
    if st.button("Confirm and Proceed", type="primary", key="sr_checked_btn"):
        st.session_state.current_step = 3
        
# Mapping List Retrival
if st.session_state.current_step > 2:
    st.markdown('#### Step 4. Mapping List Retrival')

    node_tech = st.session_state.current_metadata["Technology_Text__c"]
    node_subtech = st.session_state.current_metadata["Sub_Technology_Text__c"]
    st.markdown(f"""\n* **Technology:** {node_tech}\n* **Sub_Technology:** {node_subtech}""")
    
    p_list = st.session_state.p_mapping[node_tech][node_subtech]
    s_list = st.session_state.s_mapping[node_tech][node_subtech]
    new_p_list = st.multiselect('P Mapping', p_list, p_list)
    new_s_list = st.multiselect('S Mapping', s_list, s_list)
    p_str = "/ ".join(new_p_list)
    s_str = "/ ".join(new_s_list)
    
    st.session_state.current_step = 4
        

# Case Notes Retrieval
if st.session_state.current_step > 3:
    st.markdown('#### Step 5. Case Note Retrieval')
    
    with st.status('Loading Case Notes...'):
        time.sleep(1)
        sr_str = st.session_state.current_metadata["sr"]
        st.session_state.current_notes = st.session_state.notes[sr_str]
                    
        note_contents, editable_casenotes = uts.note_filter(
            notes=st.session_state.current_notes, 
            filter=st.session_state.filter, 
            filter_list=new_p_list+new_s_list, 
            regex_filter_switch=regex_filter_switch, 
            nn_filter_switch=nn_filter_switch,
        )

        st.session_state.context = uts.context_constrct(
            note_contents=note_contents, 
            metadata=st.session_state.current_metadata, 
            option_list=st.session_state.config['fields'],
        )

    st.success(f'Case Note [{len(editable_casenotes)} out of {len(st.session_state.current_notes)}] Loaded!', icon="✅")
    st.session_state.current_notes = st.data_editor(editable_casenotes, use_container_width=True)
    st.session_state.current_step = 6

    
# Metadata Collection
if st.session_state.current_step > 5:
    st.markdown('#### Step 6. Metadata Collection')
    with st.spinner('Metadata Processing...'):
        time.sleep(3)
        st.session_state.current_metadata = st.data_editor(st.session_state.current_metadata, use_container_width=True)
    st.session_state.current_step = 6


# Product Name Inference 
if st.session_state.current_step > 5:
    st.markdown('#### Step 7. Product Name Inference')
    with st.spinner('Predicting...'):            
        prediction, summary, explanation = uts.product_prediction(
            llm_caller=st.session_state.llm_caller, 
            context=st.session_state.context, 
            p_str=p_str
        )
            
        mnode_product = st.session_state.current_metadata["Product_Name__c"] if "Product_Name__c" in st.session_state.current_metadata else "None"
        correct, overlap = LCSEvaluator.eval(mnode_product, prediction, 0.5)

        st.markdown(f"* **Ground Truth:** {mnode_product}\n* **Prediction:** {prediction}\n* **Explanation:** {explanation}\n* **Summary:** {summary}")
    st.session_state.current_step = 7
    

# Software Version Inference
if st.session_state.current_step > 6:
    st.markdown('#### Step 8. Software Version Inference')
    with st.spinner('Predicting...'):
        prediction, summary, explanation = uts.software_prediction(
            llm_caller=st.session_state.llm_caller, 
            context=st.session_state.context, 
            s_str=s_str
        )
            
        mnode_software = st.session_state.current_metadata["SW_Version__c"] if "SW_Version__c" in st.session_state.current_metadata else "None"
        correct = NewSDASEvaluator.eval(mnode_software, prediction)

        st.markdown(f"* **Ground Truth:** {mnode_software}\n* **Prediction:** {prediction}\n* **Explanation:** {explanation}\n* **Summary:** {summary}\n")
        
        st.session_state.current_step = 8
        
# Bingo
if st.session_state.current_step > 7:
    st.balloons()