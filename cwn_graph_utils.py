import pdb
import re

class CwnGraphUtils:
    def __init__(self, V, E):
        self.V = V
        self.E = E

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
                   ret.append(v)
        return ret

    def find_edges(self, node_id, is_directed = True):
        ret = []
        for e, edata in self.E.items():
            if e[0] == node_id:
                ret.append((e[1], edata["edge_type"]))
            if e[1] == node_id and not is_directed:
                ret.append((e[0], edata["edge_type"] + "_of"))
        return ret
    
    def get_node_def(self, node_id):
        return self.get_node_data(node_id, "def")
    
    def get_node_label(self, node_id):
        ntype = self.get_node_data(node_id, "node_type")
        if ntype == "glyph":
            return self.get_node_data(node_id, "glyph")
        elif ntype == "lemma":
            return self.get_node_data(node_id, "lemma")
        elif ntype == "sense":
            return self.get_node_def(node_id)
        elif ntype == "facet":
            return self.get_node_def(node_id)
        else:
            return node_id

    def get_node_data(self, node_id, field_name = None):
        if node_id in self.V:
            node_data = self.V[node_id]
        else:
            node_data = {}
        
        if field_name is None:
            return node_data
        else:
            return node_data.get(field_name, "")
    
    def get_edge_data(self, edge_id, field_name = None):
        if edge_id in self.E:
            edge_data = self.E[edge_id]
        else:
            edge_data = {}
        
        if field_name is None:
            return edge_data
        else:
            return edge_data.get(field_name, "")

    def get_sense_defs(self, lemma_id):
        if lemma_id not in self.V: return []
        if self.get_node_data(lemma_id)["node_type"] != "lemma":
            return []

        sense_ids = [x[0] for x in self.find_edges(lemma_id)]
        return [self.get_node_def(x) for x in sense_ids]


