// This file uses typescript to describe the data structure in CwnGraph.
// CwnGraph itself uses python only.

type CwnNodes = {[nodeid: string]: CwnNodeData};
type CwnNodeData = CwnGlyph | CwnLemma | CwnSense | CwnFacet
type CwnEdges = {[edgeTuple: string]: CwnEdgeData};
type CwnEdgeData = CwnRelationEdge
type RelationType = 
    "holonym" | "antonym" | "meronym" |
    "hypernym" | "hyponym" | "variant" |
    "paranym" | "synonym"

class CwnGlyph {
    node_type: "glyph";
    glyph: string;
}

class CwnLemma {
    node_type: "lemma";
    lemma: string;
    lemma_sno: number;
    zhuyin: string;
}

class CwnSense {
    node_type: "sense";
    def: string;
    domain: string;
    pos: string | string[];
    examples: string[];
}

class CwnFacet {
    node_type: "facet";
    def: string;
    domain: string;
    pos: string;
}

class CwnRelationEdge {
    edge_type: RelationType;    
}
