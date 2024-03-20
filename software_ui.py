# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 19/03/2024


import json
import time
import streamlit as st
from src.filter import Filter
from src.graph import CiscoGraph
from src.caller import OpenAICaller
from src.evaluator import NewSDASEvaluator
from src.utils import get_norm_swv_mapping


# Title
st.set_page_config(page_title="Luna", page_icon='🌘')
st.header('🌘 Luna - Software Version Prediction Demo', divider='rainbow')

# Status Initialization
if "sr" not in st.session_state:
    st.session_state.config = None
    st.session_state.sr = '12345'
    st.session_state.metadata = None
    st.session_state.casenote = None
    st.session_state.step = 0
    st.session_state.graph_handler = None
    st.session_state.s_mapping = None
    st.session_state.gold_nodes = None
    st.session_state.casenotes = None
    st.session_state.context = None
    st.session_state.llm_caller = None
    st.session_state.filter = None
    
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

with st.spinner('Loading the Case Note Filter...'):
    if not st.session_state.filter:
        st.session_state.filter = Filter(st.session_state.config)
        time.sleep(2)
st.success('Case Note Filter Initialized!', icon="✅")

with st.spinner('Loading software mapping file...'):
    if not st.session_state.s_mapping:
        st.session_state.s_mapping = get_norm_swv_mapping('./data/tech_subtech_swv_norm.xlsx')
        time.sleep(1)
st.success('Software Mapping File Loaded!', icon="✅")

with st.spinner('Retrieving nodes from the graph...'):
    if not st.session_state.gold_nodes:
        node_results = st.session_state.graph_handler.raw_excute("MATCH (m:Gold) RETURN m")
        st.session_state.gold_nodes = dict()
        for node in node_results:
            node_data = node['m']
            node_sr = node_data['sr']
            # Force overload
            if node_sr in ["694540632", "695146873", "695268540", "695443169", "695503784", "695545329", "695571422", "695579249", "694571397", "695644022", "694117912", "695816345", "694641874", "694888348"]:
                st.session_state.gold_nodes[node_sr] = node_data
        time.sleep(1)
st.success(f'Got [{len(st.session_state.gold_nodes)}] nodes from the graph!', icon="✅")

# SR
st.markdown('#### Step 2. SR Selection')
time.sleep(2)
sr_id = st.selectbox('Which SR you would like to proceed?', tuple(st.session_state.gold_nodes.keys()))
st.session_state.metadata = st.session_state.gold_nodes[sr_id]

# Software Mapping
st.markdown('#### Step 3. Software Mapping')
time.sleep(1)
node_tech = st.session_state.metadata["Technology_Text__c"]
node_subtech = st.session_state.metadata["Sub_Technology_Text__c"]
st.markdown(f"""
        * **Technology:** {node_tech}
        * **Sub_Technology:** {node_subtech}
    """)
s_list = list(set(st.session_state.s_mapping[node_tech][node_subtech]))
new_s_list = st.multiselect('MCQ Software Mapping', s_list, s_list)
s_str = "/ ".join(new_s_list)

# Case Notes
st.markdown('#### Step 4. Case Note Retrieval')
filter_count = 0
col1, col2 = st.columns([1, 1])
regex_filter_switch = col1.checkbox('Enable Regex Filter')
nn_filter_switch = col2.checkbox('Enable NN Filter')

with st.status("Loading Case Notes..."):
    time.sleep(1)
    sr_str = st.session_state.metadata["sr"]
    st.session_state.casenotes = st.session_state.graph_handler.raw_excute(f"MATCH (m:Metadata) WHERE (m.sr = '{sr_str}') MATCH ((m)-[:Has]->(n)) RETURN n")
    
    notes = list()
    editable_casenotes = list()
    for index, nnode in enumerate(st.session_state.casenotes):
        st.write(f"===== Processing [{index}/{len(st.session_state.casenotes)}] Node =====")
        nnode_data = nnode["n"]
        
        if 'extracted_note' not in nnode_data:
            nnode_data['extracted_note'] = nnode_data['Note__c']
        
        # Filter by Regex
        if regex_filter_switch and not st.session_state.filter.filter_by_regex(nnode_data, new_s_list):
            st.write(f"Node [{index}] is opt out: Regex Filter.")
            filter_count += 1
            continue
        
        # Filter by NN
        if nn_filter_switch and not st.session_state.filter.filter_by_classifier(nnode_data, new_s_list):
            st.write(f"Node [{index}] is opt out: NN Classifier.")
            filter_count += 1
            continue
        
        st.write(f"Node [{index}] is opt in.")
        editable_casenotes += [nnode_data]
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

st.success(f'Case Note [{len(st.session_state.casenotes)}] are loaded and [{filter_count}] are filted out!', icon="✅")
st.session_state.casenotes = st.data_editor(editable_casenotes, use_container_width=True)

# Metadata
st.markdown('#### Step 5. Metadata Collection')
with st.spinner('Metadata Processing...'):
    time.sleep(3)
    st.session_state.metadata = st.data_editor(st.session_state.metadata, use_container_width=True)


st.markdown('#### Step 7. Software Version Inference')
with st.spinner('Predicting...'):
    question = f'Which software version is principally discussed in these documents?'
    response = st.session_state.llm_caller.software_analysis([st.session_state.context], question, s_str)

    prediction, summary, explanation = "", "", ""
    try:
        response_json = json.loads(response)
        prediction = response_json['software_version']
        summary = response_json['summary']
        explanation = response_json['explanation']
    except Exception as e:
        prediction = response
        
    mnode_product = st.session_state.metadata["SW_Version__c"]
    correct = NewSDASEvaluator.eval(mnode_product, prediction)

    st.markdown(f"""
        * **Prediction:** {prediction}
        * **Explanation:** {explanation}
        * **Summary:** {summary}
    """)

st.success(f'Ground Truth: [{mnode_product}] Prediction: [{prediction}]')








    