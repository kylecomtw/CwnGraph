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
    generic = -1
    has_sense = 91
    has_lemma = 92
    has_facet = 93

    @staticmethod
    def from_zhLabel(zhlabel):
        label_map = {
            "全體詞": CwnRelationType.holonym,
            "反義詞": CwnRelationType.antonym,
            "部分詞": CwnRelationType.meronym,
            "上位詞": CwnRelationType.hypernym,
            "下位詞": CwnRelationType.hyponym,
            "異體": CwnRelationType.variant,
            "近義詞": CwnRelationType.nearsynonym,
            "類義詞": CwnRelationType.paranym,
            "同義詞": CwnRelationType.synonym            
        }

        return label_map.get(zhlabel, CwnRelationType.generic)

class CwnNode:
    def __init__(self):
        self.id = None
        self.node_type = None
    
    def data(self):
        raise NotImplementedError("abstract method: CwnNode.data")
    
    def __eq__(self, other):
        raise NotImplementedError()
    
    def __hash__(self):
        raise NotImplementedError()

class CwnGlyph(CwnAnnotationInfo):
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.glyph = ndata.get("glyph", "")
        self.annot = ndata.get("annot", {})
    
    def __repr__(self):
        return "<CwnLemma: {lemma}_{lemma_sno}>".format(
            **self.__dict__
        )
    
    def __eq__(self, other):
        if isinstance(other, CwnGlyph):
            return self.glyph == other.glyph
        else:
            return False
    
    def __hash__(self):
        return hash(self.glyph)

    def data(self):
        data_fields = ["node_type", "glyph"]
        return {
            k: self.__dict__[k] for k in data_fields
        }  

class CwnLemma(CwnAnnotationInfo):
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu
        self.id = nid
        self.node_type = "lemma"
        self.lemma = ndata.get("lemma", "")
        self.lemma_sno = ndata.get("lemma_sno", 1)
        self.zhuyin = ndata.get("zhuyin", "")
        self.annot = ndata.get("annot", {})
        self._senses = None
    
    def __repr__(self):
        return "<CwnLemma: {lemma}_{lemma_sno}>".format(
            **self.__dict__
        )

    def __eq__(self, other):
        if isinstance(other, CwnLemma):
            return self.lemma == other.lemma and \
                self.zhuyin == other.zhuyin
        else:
            return False
    
    def __hash__(self):
        return hash((self.lemma, self.zhuyin))

    def data(self):
        data_fields = ["node_type", "lemma", "lemma_sno", "zhuyin", "annot"]
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
                if edge_x.edge_type == "has_sense":
                    sense_nodes.append(CwnSense(edge_x.tgt_id, cgu))
            self._senses = sense_nodes
        return self._senses
    

class CwnSense(CwnAnnotationInfo):
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu
        self.id = nid
        self.pos = ndata.get("pos", "")
        self.node_type = "sense"
        self.definition = ndata.get("def", "")
        self.src = ndata.get("src", None)
        self.examples = ndata.get("examples", [])
        self.domain = ndata.get("domain", "")
        self.annot = ndata.get("annot", {})        
        self._relations = None
        self._lemmas = None
    
    def __repr__(self):
        try:
            head_word = self.lemmas[0].lemma
        except (IndexError, AttributeError):
            head_word = "----"
        return "<CwnSense[{id}]({head}): {definition}>".format(
            head=head_word, **self.__dict__
        )

    def __eq__(self, other):
        if isinstance(other, CwnSense):
            return self.definition == other.definition and \
                self.pos == other.pos and \
                (self.src and other.src and self.src == other.src)
        else:
            return False
    
    def __hash__(self):
        return hash((self.definition, self.pos, self.src))

    def data(self):
        data_fields = ["node_type", "pos", "examples", "domain", "annot"]
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
                if edge_x.edge_type == "has_sense":
                    lemma_nodes.append(CwnLemma(edge_x.src_id, cgu))
            self._lemmas = lemma_nodes
        return self._lemmas

    @property
    def relations(self):
        if self._relations is None:
            cgu = self.cgu
            relation_infos = []
            edges = cgu.find_edges(self.id, is_directed=False)
            for edge_x in edges:
                if edge_x.edge_type.startswith("has_sense"):
                    continue
                
                if not edge_x.reversed:
                    relation_infos.append((edge_x.edge_type, 
                        CwnSense(edge_x.tgt_id, cgu)))
                else:
                    relation_infos.append((edge_x.edge_type + "(rev)", 
                        CwnSense(edge_x.src_id, cgu)))

            self._relations = relation_infos
        return self._relations
    
    @property
    def hypernym(self):
        relation_infos = self.relations
        hypernym = [x[1] for x in relation_infos if x[0] == "hypernym"]
        return hypernym

class CwnFacet(CwnSense):
    def __init__(self, nid, cgu):
        super(CwnFacet, self).__init__(nid, cgu)
        self.node_type = "facet"

class CwnSynset(CwnAnnotationInfo):
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu    
        self.id = nid    
        self.node_type = "synset"
        self.gloss = ndata.get("gloss", "")
        self.pwn_word = ndata.get("pwn_word", "")
        self.pwn_id = ndata.get("pwn_id", "")
    
    def __repr__(self):    
        return "<CwnSynset[{id}]: {gloss}>".format(
            **self.__dict__
        )
    
    def data(self):
        data_fields = ["node_type", "gloss", "pwn_word", "pwn_id"]
        data_dict= {
            k: self.__dict__[k] for k in data_fields
        }        
        return data_dict
    
    def __eq__(self, other):
        if isinstance(other, CwnSynset):
            return self.gloss == other.gloss                
        else:
            return False
    
    def __hash__(self):
        return hash(self.gloss)

class CwnRelation(CwnAnnotationInfo):
    def __init__(self, eid, cgu, reversed=False):
        edata = cgu.get_edge_data(eid)
        self.cgu = cgu
        self.id = eid        
        self.edge_type = edata.get("edge_type", "generic")
        self.annot = {}
        self.reversed = reversed
    
    def __repr__(self):
        src_id = self.id[0]
        tgt_id = self.id[1]
        if not self.reversed:            
            return f"<CwnRelation> {self.edge_type}: {src_id} -> {tgt_id}"
        else:
            return f"<CwnRelation> {self.edge_type}(rev): {tgt_id} <- {src_id}"

    def data(self):
        data_fields = ["edge_type", "annot"]
        data_dict= {
            k: self.__dict__[k] for k in data_fields
        }        
        return data_dict
    
    @property
    def src_id(self):
        return self.id[0]

    @property
    def tgt_id(self):
        return self.id[1]

    @property
    def relation_type(self):
        return self.edge_type
    
    @relation_type.setter
    def relation_type(self, x):        
        if not isinstance(x, CwnRelationType):
            raise ValueError("x must be instance of CwnRelationType")
        else:
            self.edge_type = x.name

class GraphStructure:
    def __init__(self):
        self.V = {}
        self.E = {}
        self.meta = {}

        

