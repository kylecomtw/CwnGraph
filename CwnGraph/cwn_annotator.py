import json
import datetime
import cwnio

class CwnAnnotator:
    def __init__(self, cgu, session_name=None):
        self.cgu = cgu
        self.V = {}
        self.E = {}
        if session_name:
            self.load_session(session_name)
    
    def load_session(self, name):
        

    def save_session(self, name):
        pass

    def snapshot(self, name):

    def get_timestamp(self):
        return datetime.strftime("%y%m%d%H%M%S")
    
    def find_glyph(self, instr):
        pass
    
    def find_lemma(self, instr_regex):
        pass
    
    def find_edges(self, node_id, is_directed = True):
        pass
    
    def get_node_data(self, node_id, field_name = None):
        pass
    
    def get_edge_data(self, edge_id, field_name = None):
        pass
    

    
        
    