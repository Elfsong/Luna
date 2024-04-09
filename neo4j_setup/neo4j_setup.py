# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 09/04/2024

import json
import argparse
from enum import Enum
from tqdm import tqdm
from src.graph import CiscoGraph


parser = argparse.ArgumentParser(description='Welcome to Luna 🌙')
parser.add_argument("-a", "--address", type=str, help='neo4j server address', default='bolt://localhost:7687')
parser.add_argument('-u', "--username", help='neo4j username', default="neo4j")
parser.add_argument('-p', "--passowrd", help='neo4j password', default="neo4j")
parser.add_argument('-n', "--note", help='neo4j case note file path', default="../data/Case_Notes.json")
parser.add_argument('-m', "--meta", help='neo4j metadata file path', default="../data/Case_Metadata.json")
args = parser.parse_args()

graph_handler = CiscoGraph(args.address, args.username, args.passowrd)
graph_handler.node_delete_all()

NodeType = Enum('NodeType', ['MetaData', 'Note'])
EdgeType = Enum('EdgeType', ['Belong'])

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
    """
    The function `load_metadata` loads metadata from a file, parses it, and returns a list of SR
    metadata instances.
    
    :param file_path: The `file_path` parameter is a string that represents the path to the file
    containing the metadata
    :return: a list of SR_Metadata objects.
    """
    with open(file_path) as file_handler:
        data = json.load(file_handler)
        
    sr_set, sr_data = set(), list()
    for instance in tqdm(data, desc=f"Parsing raw metadata from {file_path}..."):
        if instance["sr"] not in sr_set:
            sr_data += [SR_Metadata(instance)]
            sr_set.add(instance["sr"])
    
    return sr_data

def load_notes(file_path):
    """
    The function `load_notes` loads notes from a file and returns a list of `CiscoData.SR_Note`
    instances.
    
    :param file_path: The `file_path` parameter is a string that represents the path to the file
    containing the notes data that you want to load
    :return: a list of instances of the `CiscoData.SR_Note` class.
    """
    with open(file_path) as file_handler:
        data = json.load(file_handler)
    return [SR_Note(instance) for instance in tqdm(data, desc=f"Parsing raw notes from {file_path}...")]

metadata = load_metadata(args.meta)
notes = load_notes(args.note)

def add_metadata_to_graph(graph_handler, data):
    for instance in tqdm(data, desc="Uploading metadata to Neo4J..."):
        graph_handler.node_create(node_type="Metadata", node_attributes=instance.to_cypher())
add_metadata_to_graph(graph_handler, metadata)

def add_notes_to_graph(graph_handler, data):
    for instance in tqdm(data, desc="Uploading notes to Neo4J..."):
        note_node = graph_handler.node_create(node_type="Note", node_attributes=instance.to_cypher())
        note_node_id = note_node.element_id
        sr_node_id = graph_handler.node_id_query("Metadata", "sr", instance.sr_uuid)
        graph_handler.edge_create(sr_node_id, note_node_id, "Has", {})
add_notes_to_graph(graph_handler, notes)

def add_products_to_graph(graph_handler, data):
    product_node_ids = dict()
    
    for instance in tqdm(data, desc="Adding products to Neo4J..."):
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
    
    for instance in tqdm(data, desc="Adding tech to Neo4J..."):
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

