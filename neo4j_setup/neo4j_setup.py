# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 09/04/2024

import json
import argparse
from enum import Enum
from tqdm import tqdm
from neo4j import GraphDatabase


parser = argparse.ArgumentParser(description='Welcome to Luna 🌙')
parser.add_argument("-a", "--address", type=str, help='neo4j server address', default='bolt://localhost:7687')
parser.add_argument('-u', "--username", help='neo4j username', default="neo4j")
parser.add_argument('-p', "--passowrd", help='neo4j password', default="neo4j")
parser.add_argument('-n', "--note", help='neo4j case note file path', default="../data/Case_Notes.json")
parser.add_argument('-m', "--meta", help='neo4j metadata file path', default="../data/Case_Metadata.json")
args = parser.parse_args()

NodeType = Enum('NodeType', ['MetaData', 'Note'])
EdgeType = Enum('EdgeType', ['Belong'])

class CiscoGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()
    
    # Node Operations
    def node_create(self, node_type, node_attributes):
        with self.driver.session() as session:
            query = f"CREATE (n:{node_type} $params) RETURN n"
            parameter_dict = {'params': node_attributes}
            records = session.run(query, parameters=parameter_dict)
            return records.single()[0]
        
    def node_delete_all(self):
        with self.driver.session() as session:
            query = f"MATCH (n) DETACH DELETE n"
            session.run(query)
    
    def node_id_query(self, node_type, key, value):
        with self.driver.session() as session:
            query = f"MATCH (n:{node_type}) WHERE n.{key} = '{value}' RETURN elementID(n)"
            records = session.run(query)
            return records.single()[0]

    def raw_excute(self, query):
        with self.driver.session() as session:
            response = session.run(query)
            return response.data()
    
    def add_gold_set(self):
        with self.driver.session() as session:
            query = """
                MATCH (n:Metadata)
                WHERE n.sr IN ['694745866', '694540632', '695268540', '695816345', '694117912', '695579249', '694515784', '694925180', '694641874', '695960852', '695138053', '694180958', '694208469', '695443169', '695684373', '694111541', '695138158', '695109716', '694180161', '694498853', '694642521', '695503784', '694624943', '694069586', '694913120', '695077555', '695644022', '695545329', '694249113', '694068972', '694105276', '693988553', '694168349', '694870141', '693929980', '694831371', '695942943', '695940399', '694925542', '695069319', '695618886', '694914231', '694482515', '695146873', '694180060', '694140893', '694571397', '694935054', '694952109', '694907945', '694888348', '695605404', '695571422', '695810508', '695648768']
                SET n:Metadata:Gold
            """
            session.run(query)
            return None

    def get_all_notes(self, sr):
        with self.driver.session() as session:
            query = f"""
                MATCH (n:Metadata) 
                WHERE n.sr = '635211645' 
                MATCH (n)-[*]-(connected) 
                RETURN connected
            """
            records = session.run(query)
            
            notes = dict()
            for record in records:
                node_id = record.values()[0]._element_id
                data = record.values()[0]._properties
                notes[node_id] = data
            return notes
            
    # Edge Operations
    def edge_create(self, node_a_id, node_b_id, edge_type, edge_attributes):
        with self.driver.session() as session:
            query = f"""
                MATCH (a) where elementID(a) = '{node_a_id}'
                MATCH (b) where elementID(b) = '{node_b_id}'
                CREATE (a)-[e:{edge_type} $params]->(b)
                RETURN e
            """
            
            parameter_dict = {'params': edge_attributes}
            result = session.run(query, parameters=parameter_dict)
            return result.single()[0]

class SR_Metadata(object):
    def __init__(self, data) -> None:
        self.uuid = data["sr"]
        self.metadata = data
        
    def to_cypher(self):
        self.metadata["name"] = self.uuid
        for key in self.metadata:
            self.metadata[key] = str(self.metadata[key])
        return self.metadata
    
class SR_Note(object):
    def __init__(self, data) -> None:
        self.uuid = data["Case_C3Number__c"]
        self.sr_uuid = data["sr"]
        self.metadata = data
    
    def to_cypher(self):
        self.metadata["name"] = self.uuid
        for key in self.metadata:
            self.metadata[key] = str(self.metadata[key])
        return self.metadata
    
def load_metadata(file_path):
    with open(file_path) as file_handler:
        data = json.load(file_handler)
        
    sr_set, sr_data = set(), list()
    for instance in tqdm(data, desc=f"[1/6] Parsing raw metadata from {file_path}..."):
        if instance["sr"] not in sr_set:
            sr_data += [SR_Metadata(instance)]
            sr_set.add(instance["sr"])
    
    return sr_data

def load_notes(file_path):
    with open(file_path) as file_handler:
        data = json.load(file_handler)
    return [SR_Note(instance) for instance in tqdm(data, desc=f"[2/6] Parsing raw notes from {file_path}...")]

metadata = load_metadata(args.meta)
notes = load_notes(args.note)

graph_handler = CiscoGraph(args.address, args.username, args.passowrd)
graph_handler.node_delete_all()

def add_metadata_to_graph(graph_handler, data):
    for instance in tqdm(data, desc="[3/6] Uploading metadata to Neo4J..."):
        graph_handler.node_create(node_type="Metadata", node_attributes=instance.to_cypher())
add_metadata_to_graph(graph_handler, metadata)

def add_notes_to_graph(graph_handler, data):
    for instance in tqdm(data, desc="[4/6] Uploading notes to Neo4J..."):
        note_node = graph_handler.node_create(node_type="Note", node_attributes=instance.to_cypher())
        note_node_id = note_node.element_id
        sr_node_id = graph_handler.node_id_query("Metadata", "sr", instance.sr_uuid)
        graph_handler.edge_create(sr_node_id, note_node_id, "Has", {})
add_notes_to_graph(graph_handler, notes)

def add_products_to_graph(graph_handler, data):
    product_node_ids = dict()
    
    for instance in tqdm(data, desc="[5/6] Adding products to Neo4J..."):
        sr_node_id = graph_handler.node_id_query("Metadata", "sr", instance.uuid)
        product_name = instance.metadata["Product_Name__c"]
        product_family = instance.metadata["Product_Family__c"]
        if product_name not in product_node_ids:
            note_node = graph_handler.node_create(node_type="Product", node_attributes={
                "name": product_name, 
                "product_name": product_name,
                "product_family": product_family
            })
            product_node_ids[product_name] = note_node.element_id
            product_node_id = note_node.element_id
        else:
            product_node_id = product_node_ids[product_name]
            
        graph_handler.edge_create(sr_node_id, product_node_id, "Mention", {})
add_products_to_graph(graph_handler, metadata)

def add_tech_to_graph(graph_handler, data):
    technology_ids = dict()
    sub_technology_ids = dict()
    technology_dict = dict()
    
    for instance in tqdm(data, desc="[6/6] Adding tech to Neo4J..."):
        sr_node_id = graph_handler.node_id_query("Metadata", "sr", instance.uuid)
        technology = instance.metadata["Technology_Text__c"]
        sub_technology = instance.metadata["Sub_Technology_Text__c"]
        
        if technology:
            if (technology not in technology_ids):
                technology_dict[technology] = list()
                note_node = graph_handler.node_create(node_type="Technology", node_attributes={
                    "name": technology, 
                    "technology": technology,
                })
                technology_ids[technology] = note_node.element_id

            technology_node_id = technology_ids[technology]
            graph_handler.edge_create(sr_node_id, technology_node_id, "Mention", {})
        
            if sub_technology:
                if (sub_technology not in sub_technology_ids):
                    note_node = graph_handler.node_create(node_type="SubTechnology", node_attributes={
                        "name": technology, 
                        "technology": technology,
                        "subtechnology": sub_technology,
                    })
                    sub_technology_ids[sub_technology] = note_node.element_id
            
                sub_technology_node_id = sub_technology_ids[sub_technology]
                graph_handler.edge_create(sr_node_id, sub_technology_node_id, "Mention", {})
                
                if sub_technology not in technology_dict[technology]:
                    graph_handler.edge_create(technology_node_id, sub_technology_node_id, "Has", {})
                    technology_dict[technology] += [sub_technology]
add_tech_to_graph(graph_handler, metadata)

