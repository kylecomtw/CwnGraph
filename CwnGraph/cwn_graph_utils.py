import pdb
import re
from .cwn_types import *

class CwnGraphUtils:
    def __init__(self, V, E):
        self.V = V
        self.E = E
        self.edge_src_index = self.build_index(E.keys(), lambda x: x[0])
        self.edge_tgt_index = self.build_index(E.keys(), lambda x: x[1])

    def build_index(self, data, keyfunc):
        idx = {}        
        for k in data:                   
            idx_key = keyfunc(k)
            idx.setdefault(idx_key, []).append(k)
        return idx

    def find_glyph(self, instr):
        for v, vdata in self.V.items():
            if vdata["node_type"] == "glyph":
                if vdata["glyph"] == instr:               
                   return v
        return None
    
    def find_lemma(self, instr_regex):
        ret = []
        pat = re.compile(instr_regex)
        for v, vdata in self.V.items():
            if vdata["node_type"] == "lemma":
                if pat.match(vdata["lemma"]) is not None:               
                   ret.append(CwnLemma(v, self))
        return ret

    def find_edges(self, node_id, is_directed = True):
        ret = []
        
        for e in self.edge_src_index.get(node_id, []):  
            ret.append(CwnRelation(e, self))            
        if not is_directed:
            for e in self.edge_tgt_index.get(node_id, []):
                ret.append(CwnRelation(e, self, reversed=True))   

        return ret
    
    def connected(self, node_id, is_directed = True, maxConn=100, sense_only=True):
        ret = []
        visited = set()
        buf = [node_id]
        while buf:
            node_x = buf.pop()
            visited.add(node_x)
            conn_edges = self.find_edges(node_x, is_directed)            
            for conn_edge_x in conn_edges:
                conn_node_x = conn_edge_x[0]
                conn_rel = conn_edge_x[1]
                if sense_only and "has_sense" in conn_rel:
                    continue

                if conn_node_x in visited or conn_node_x in buf:
                    continue
                else:
                    buf.append(conn_node_x)
                ret.append((node_x, conn_rel, conn_node_x))
            if maxConn and len(ret) > maxConn:
                break                        
        return ret

    def get_node_data(self, node_id, field_name = None):
        return self.V.get(node_id, {})

    def get_edge_data(self, edge_id, field_name = None):
        return self.E.get(edge_id, {})



