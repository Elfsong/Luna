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
                WHERE n.sr IN ['694745866', '694540632', '695268540', '695816345', '694117912', '695579249', '694515784', '694925180', '694641874', '695960852', '695138053', '694180958', '694208469', '695443169', '695684373', '694111541', '695138158', '695109716', '694180161', '694498853', '694642521', '695503784', '694624943', '694069586', '694913120', '695077555', '695644022', '695545329', '694249113', '694068972', '694105276', '693988553', '694168349', '694870141', '693929980', '694831371', '695942943', '695940399', '694925542', '695069319', '695618886', '694914231', '694482515', '695146873', '694180060', '694140893', '694571397', '694935054', '694952109', '694907945', '694888348', '695605404', '695571422', '695810508', '695648768']
                SET n:Metadata:Gold
                MATCH (n:Gold) 
                WHERE NOT ((n)-[:Has]->())
                SET n:Metadata:Gold:Empty
                RETURN n
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