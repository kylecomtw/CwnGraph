from typing import Set, cast
from ..cwn_types import GraphStructure, CwnNode, CwnSense, CwnSynset
from .merger_types import MergedAnnotation
from ..cwn_annotator import CwnAnnotator
from ..cwn_factory import CwnNodeFactory

class AnnotationMerger:
    def __init__(self, annotx: CwnAnnotator, annoty: CwnAnnotator):
        self.x = annotx
        self.y = annoty
        self.Vm = {}
        self.Em = {}
        self.trace = [annotx.meta["session_name"],
            annoty.meta["session_name"]]        

    def merge(self):
        self.merge_nodes(self.x.V, self.y.V)
        self.merge_edges(self.x.E, self.y.E)

        meta_data = {
            "trace": self.trace
        }
        Gm = MergedAnnotation(meta_data, self.Vm, self.Em)

        return Gm
    
    def merge_nodes(self, Vx, Vy):                
        nodes_base = {CwnNodeFactory.createNode(y, self.y.cgu) for y in Vy}
        nodes_merged = set()
        for node_id_x in Vx.keys():
            node_x: CwnNode = CwnNodeFactory.createNode(node_id_x, self.x.cgu)
            
            if node_x in nodes_base:
                # there are two identitcal node in Vx and Vy
                node_x = self.merge_node(node_x, nodes_base)
                if node_x.node_type == "sense":                    
                    sense_x: CwnSense = self.merge_sense_node(node_x, nodes_base)
                    nodes_merged.add(sense_x)
                elif node_x.node_type == "synset":
                    synset_x: CwnSynset = self.merge_synset_node(node_x, nodes_base)
                    nodes_merged.add(synset_x)
                else:
                    nodes_merged.add(node_x)
            else:
                # node_x is unique in Vx, add it to nodes_base
                nodes_merged.add(node_x)
            
        # add all nodes into merged Graph nodes, Vm
        for node_m in nodes_merged:
            self.Vm[node_m.id] = node_m.data()

    def merge_node(self, 
        node_x: CwnNode, nodes_set: Set[CwnNode]) -> CwnNode:
        for node_y in nodes_set:
            if node_y != node_x: continue                        
            node_x.annot = {
                self.x.name: node_x.annot,
                self.y.name: node_y.annot
            }
        return node_x

    def merge_sense_node(self, 
        sense_x: CwnSense, nodes_set: Set[CwnNode]) -> CwnSense:
        for node_y in nodes_set:
            if node_y != sense_x: continue
            sense_y: CwnSense = cast(CwnSense, node_y)
            for ex_y in sense_y.examples:
                if ex_y not in sense_x.examples:
                    sense_x.examples.append(ex_y)
            sense_x.domain = ",".join([sense_x.domain, sense_y.domain])
        return sense_x

    def merge_synset_node(self, 
        synset_x: CwnSynset, nodes_set: Set[CwnNode]) -> CwnSynset:
        for node_y in nodes_set:
            if node_y != synset_x: continue
            synset_y: CwnSynset = cast(CwnSynset, node_y)
            synset_x.pwn_id = ",".join([synset_x.pwn_id, synset_y.pwn_id])
            synset_x.pwn_word = ",".join([synset_x.pwn_word, synset_y.pwn_word])
        return synset_x

    def merge_edges(self, Ex, Ey):
        pass