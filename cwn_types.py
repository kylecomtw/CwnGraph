class CwnLemma:
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu
        self.nid = nid
        self.lemma = ndata["lemma"]
        self.sno = ndata["lemma_sno"]
        self.zhuyin = ndata["zhuyin"]        
        self._senses = None
    
    def __repr__(self):
        return "<CwnLemma: {lemma}_{sno}>".format(
            **self.__dict__
        )

    @property
    def senses(self):                
        if self._senses is None:
            cgu = self.cgu
            sense_nodes = []
            edges = cgu.find_edges(self.nid)
            for edge_x in edges:
                if edge_x[1] == "has_sense":
                    sense_nodes.append(CwnSense(edge_x[0], cgu))
            self._senses = sense_nodes
        return self._senses

class CwnSense:
    def __init__(self, nid, cgu):
        ndata = cgu.get_node_data(nid)
        self.cgu = cgu
        self.nid = nid
        self.pos = ndata["pos"]
        self.definition = ndata["def"]
        self.examples = ndata["examples"]                
        self._relations = None
        self._lemmas = None
    
    def __repr__(self):
        return "<CwnSense[{nid}]: {definition}>".format(
            **self.__dict__
        )
    
    @property
    def lemmas(self):                
        if self._lemmas is None:
            cgu = self.cgu
            lemma_nodes = []
            edges = cgu.find_edges(self.nid, is_directed=False)
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
            edges = cgu.find_edges(self.nid, is_directed=False)
            for edge_x in edges:
                if not edge_x[1].startswith("has_sense"):
                    relation_infos.append((edge_x[1], CwnSense(edge_x[0], cgu)))
            self._relations = relation_infos
        return self._relations
    
    @property
    def hypernym(self):
        relation_infos = self.relations
