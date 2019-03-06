from enum import Enum
from .cwn_annot_types import CwnAnnotationInfo

class CwnRelationType(Enum):
    holonym = 1
    antonym = 2
    meronym = 3
    hypernym = 4
    hyponym = 5
    variant = 6
    nearsynonym = 7
    paranym = 8
    synonym = 9

class CwnLemma(CwnAnnotationInfo):
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu
        self.id = nid
        self.lemma = ndata.get("lemma", "")
        self.lemma_sno = ndata.get("lemma_sno", "")
        self.zhuyin = ndata.get("zhuyin", "")
        self.annot = ndata.get("annot", {})
        self._senses = None
    
    def __repr__(self):
        return "<CwnLemma: {lemma}_{lemma_sno}>".format(
            **self.__dict__
        )

    def data(self):
        data_fields = ["lemma", "lemma_sno", "zhuyin", "annot"]
        return {
            k: self.__dict__[k] for k in data_fields
        }

    @staticmethod
    def from_word(word, cgu):
        return cgu.find_lemma(word)

    @property
    def senses(self):                
        if self._senses is None:
            cgu = self.cgu
            sense_nodes = []
            edges = cgu.find_edges(self.id)
            for edge_x in edges:
                if edge_x[1] == "has_sense":
                    sense_nodes.append(CwnSense(edge_x[0], cgu))
            self._senses = sense_nodes
        return self._senses
    

class CwnSense(CwnAnnotationInfo):
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu
        self.id = nid
        self.pos = ndata.get("pos", "")
        self.definition = ndata.get("def", "")
        self.examples = ndata.get("examples", [])
        self.annot = ndata.get("annot", {})
        self._relations = None
        self._lemmas = None
    
    def __repr__(self):
        return "<CwnSense[{nid}]({head}): {definition}>".format(
            head=self.lemmas[0].lemma, **self.__dict__
        )
    
    def data(self):
        data_fields = ["pos", "examples", "annot"]
        data_dict= {
            k: self.__dict__[k] for k in data_fields
        }
        data_dict["def"] = self.definition
        return data_dict

    @property
    def lemmas(self):                
        if self._lemmas is None:
            cgu = self.cgu
            lemma_nodes = []
            edges = cgu.find_edges(self.id, is_directed=False)
            for edge_x in edges:
                if edge_x[1] == "has_sense_of":
                    lemma_nodes.append(CwnLemma(edge_x[0], cgu))
            self._lemmas = lemma_nodes
        return self._lemmas

    @property
    def relations(self):
        if self._relations is None:
            cgu = self.cgu
            relation_infos = []
            edges = cgu.find_edges(self.id, is_directed=False)
            for edge_x in edges:
                if not edge_x[1].startswith("has_sense"):
                    relation_infos.append((edge_x[1], CwnSense(edge_x[0], cgu)))
            self._relations = relation_infos
        return self._relations
    
    @property
    def hypernym(self):
        relation_infos = self.relations
        hypernym = [x[1] for x in relation_infos if x[0] == "hypernym"]
        return hypernym

class CwnRelation(CwnAnnotationInfo):
    def __init__(self, eid, cgu, reversed=False):
        edata = cgu.get_edge_data(eid)
        self.cgu = cgu
        self.id = eid        
        self.edge_type = edata.get("edge_type", "")
        self.annot = {}
        self.reversed = reversed
    
    def __repr__(self):
        src_id = self.id[0]
        tgt_id = self.id[1]
        if self.reversed:            
            return f"<CwnRelation> {self.edge_type}: {src_id} -> {tgt_id}"
        else:
            return f"<CwnRelation> {self.edge_type}: {tgt_id} <- {src_id}"

    def data(self):
        data_fields = ["pos", "examples", "annot"]
        data_dict= {
            k: self.__dict__[k] for k in data_fields
        }        
        return data_dict
    @property
    def edge_type(self):
        return self.edge_type
    
    @edge_type.setter
    def edge_type(self, x):
        if not isinstance(x, CwnRelationType):
            raise ValueError("x must be instance of CwnRelationType")
        else:
            self.edge_type = str(x)


        

