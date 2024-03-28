# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 11/10/2023

from neo4j import GraphDatabase

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
                WHERE n.sr IN ['695942943', '694068972', '695810508', '695648768', '695618886', '695605404', '695545329', '695940399', '695503784', '695571422', '695579249', '695684373', '695960852']
                SET n:Metadata:Gold
            """
            session.run(query)
            return None
    def add_gold_set_2(self,nodes):
        with self.driver.session() as session:
            query = """
                MATCH (n:Metadata)
                WHERE n.sr IN """ + str(nodes) + """
                SET n:Metadata:Gold
            """
            session.run(query)
            return None
    def get_nodes(self, nodes):
        with self.driver.session() as session:
            query = """
                MATCH (n:Metadata)
                WHERE n.sr IN """ + str(nodes) + """
                RETURN n
            """
            notes = dict()
            records = session.run(query)
            for record in records:
                node_id = record.values()[0]._element_id
                data = record.values()[0]._properties
                notes[node_id] = data
            return notes

        
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