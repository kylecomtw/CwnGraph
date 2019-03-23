import os
import json
from datetime import datetime
from . import cwnio
from . import annot_merger
from .cwn_types import *
from .cwn_graph_utils import CwnGraphUtils

class CwnAnnotator:
    PREFIX = "annot/cwn_annot"
    def __init__(self, cgu, session_name):
        self.parent_cgu = cgu
        self.name = session_name
        self.V = {}        
        self.E = {}
        self.meta = {
            "session_name": session_name,
            "timestamp": "",
            "serial": 0,
            "base_hash": cgu.get_hash()
        }
                
        self.load(session_name)

    def load(self, name): 
           
        fpath = f"{CwnAnnotator.PREFIX}_{name}.json"
        if os.path.exists(fpath):
            print("loading saved session from ", fpath)
            
            self.meta, self.V, self.E = \
                cwnio.load_annot_json(fpath)
            base_hash = self.meta.get("base_hash", "")
            if base_hash and base_hash != self.parent_cgu.get_hash():
                print("WARNING: loading with a different base image")
            return True

        else:
            print("Creating new session", name)
            return False
        
    def save(self, with_timestamp=False):        
        name = self.meta["session_name"]
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        self.meta["snapshot"] = timestamp
        cwnio.ensure_dir("annot")
        if with_timestamp:
            cwnio.dump_annot_json(self.meta, self.V, self.E, 
                f"{CwnAnnotator.PREFIX}_{name}_{timestamp}.json")
        else:
            cwnio.dump_annot_json(self.meta, self.V, self.E, 
                f"{CwnAnnotator.PREFIX}_{name}.json")        
    
    def new_node_id(self):
        serial = self.meta.get("serial", 0) + 1
        session_name = self.meta.get("session_name", "")
        self.meta["serial"] = serial
        return f"{session_name}_{serial:06d}"

    def create_lemma(self, lemma):
        node_id = self.new_node_id()
        new_lemma = CwnLemma(node_id, self)
        new_lemma.lemma = lemma
        self.set_lemma(new_lemma)
        return new_lemma

    def create_sense(self, definition):
        node_id = self.new_node_id()
        new_sense = CwnSense(node_id, self)
        new_sense.definition = definition
        self.set_sense(new_sense)
        return new_sense

    def create_relation(self, src_id, tgt_id, rel_type):
        if not self.get_node_data(src_id):            
            raise ValueError(f"{src_id} not found")
        if not self.get_node_data(tgt_id):            
            raise ValueError(f"{tgt_id} not found")
        edge_id = (src_id, tgt_id)
        new_rel = CwnRelation(edge_id, self)
        new_rel.relation_type = rel_type
        self.set_relation(new_rel)
        return new_rel

    def set_lemma(self, cwn_lemma):
        self.V[cwn_lemma.id] = cwn_lemma.data()

    def set_sense(self, cwn_sense):
        self.V[cwn_sense.id] = cwn_sense.data()

    def set_relation(self, cwn_relation):
        self.E[cwn_relation.id] = cwn_relation.data()

    def remove_lemma(self, cwn_lemma):
        cwn_lemma.action = "delete"
        self.set_lemma(cwn_lemma)

    def remove_sense(self, cwn_sense):
        cwn_sense.action = "delete"
        self.set_sense(cwn_sense)
    
    def remove_relation(self, cwn_relation):
        cwn_relation.action = "delete"
        self.set_relation(cwn_relation)

    def find_glyph(self, instr):
        return self.parent_cgu.find_glyph(instr)
    
    def find_lemmas(self, instr_regex):
        cgu = CwnGraphUtils(self.V, self.E)
        lemmas = cgu.find_lemma(instr_regex)
        parent_lemmas = self.parent_cgu.find_lemma(instr_regex)
        ret = annot_merger.merge(lemmas, parent_lemmas, self)
        return ret
    
    def find_edges(self, node_id, is_directed = True):
        cgu = CwnGraphUtils(self.V, self.E)
        edges = cgu.find_edges(node_id, is_directed)        
        parent_edges = self.parent_cgu.find_edges(node_id, is_directed)
        ret = annot_merger.merge(edges, parent_edges, self)
        return ret
    
    def get_node_data(self, node_id):
        node_data = self.V.get(node_id, {})
        if not node_data:
            node_data = self.parent_cgu.get_node_data(node_id)
        
        return node_data
    
    def get_edge_data(self, edge_id):
        edge_data = self.E.get(edge_id, {})
        if not edge_data:
            edge_data = self.parent_cgu.get_edge_data(edge_id)
        
        return edge_data
    
    def connected(self, node_id, is_directed = True, maxConn=100, sense_only=True):
        raise NotImplementedError("connected() is not implemented in CwnAnnotator")

    
        
    