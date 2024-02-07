# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 11/10/2023

from enum import Enum

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
        

