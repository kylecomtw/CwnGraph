import hashlib
from typing import Set, cast
from itertools import chain
from ..cwn_types import GraphStructure, CwnNode, CwnSense, CwnSynset
from ..cwn_types import CwnRelation
from .merged_annot import MergedAnnotation
from ..cwn_annotator import CwnAnnotator
from ..cwn_factory import CwnNodeFactory, CwnEdgeFactory

# TODO: implement conflict and merging reports
class AnnotationMerger:
    def __init__(self, annotx: CwnAnnotator, annoty: CwnAnnotator):
        self.x = annotx
        self.y = annoty        
        self.Vm = {}
        self.Em = {}
        self.merged_idmap = {}
        self.conflicts = []
        self.steps = []
        self.serial = 0
        self.trace = [annotx.meta["session_name"],
            annoty.meta["session_name"]]        

        m = hashlib.sha1()
        m.update(annotx.name + annoty.name)        
        hashHex = m.hexdigest()
        self.hashStr = hashHex[:6]        

    def merge(self) -> MergedAnnotation:
        if self.x.meta.get("base_hash") != \
            self.y.meta.get("base_hash"):
            print("WARNING: merging annotations from different base image")
        self.merge_nodes(self.x.V, self.y.V)
        self.merge_edges(self.x.E, self.y.E)

        meta_data = {
            "trace": self.trace,
            "conflicts": self.conflicts,
            "steps": self.steps
        }
        
        Gm = MergedAnnotation(meta_data, self.Vm, self.Em)
        
        return Gm
    
    def new_node_id(self, node_type):
        self.serial += 1
        return f"{self.hashStr}_{self.serial}"
    
    def map_new_edge_id(self, edge_id):
        from_id, to_id = edge_id
        
        ## We might not need check all x and y for from_id node data.
        ## But in case x and y came from different base image, we perform 
        ## this check, perhaps redundantly.
        if from_id not in self.merged_idmap and \
            not self.x.get_node_data(from_id) and \
            not self.y.get_node_data(from_id):
            raise ValueError(f"{from_id} not found when merging")

        if to_id not in self.merged_idmap and \
            not self.x.get_node_data(to_id) and \
            not self.y.get_node_data(to_id):
            raise ValueError(f"{to_id} not found when merging")
        
        return (self.merged_idmap.get(from_id, from_id),
                self.merged_idmap.get(to_id, to_id))

    def merge_nodes(self, Vx, Vy):                
        
        nodes_map = {}
        # index nodes in Vx
        for node_x in Vx:
            node_obj = CwnNodeFactory.createNode(node_x, self.x)            
            nodes_map.setdefault(node_obj, []).append(node_obj)
        
        # index nodes in Vy
        for node_y in Vy:
            node_obj = CwnNodeFactory.createNode(node_y, self.y)            
            nodes_map.setdefault(node_obj, []).append(node_obj)
        
        nodes_merged = {}
        for nodes_list in nodes_map.values():                                    
            if len(nodes_list) == 1:
                # node_x is unique in Vx, add it to nodes_merged
                node_x = nodes_list[0]
                new_id = self.new_node_id(node_x.node_type)
                nodes_merged[new_id] = node_x
                self.merged_idmap[node_x.id] = new_id
                self.steps.append(("unique", new_id, node_x.id))

            elif len(nodes_list) == 2:
                # there are two identitcal node in Vx and Vy
                node_x, node_y = nodes_list[0], nodes_list[1]
                new_id = self.new_node_id(node_x.node_type)
                node_m = self.merge_node(node_x, node_y)
                if node_x.node_type == "sense":                    
                    sense_x: CwnSense = self.merge_sense_node(node_x, node_y)
                    nodes_merged[new_id] = sense_x
                elif node_x.node_type == "synset":
                    synset_x: CwnSynset = self.merge_synset_node(node_x, node_y)
                    nodes_merged[new_id] = synset_x
                else:
                    nodes_merged[new_id] = node_x
                self.steps.append(("merged", new_id, f"{node_x.id},{node_y.id}"))
            else:
                print("ERROR: " + str(nodes_list))
                raise ValueError("More than two nodes are identical")

        # add all nodes into merged Graph nodes, Vm
        for node_id, node_m in nodes_merged.items():            
            self.Vm[node_id] = node_m.data()            

    def merge_node(self, 
        node_x: CwnNode, node_y: CwnNode) -> CwnNode:
        if node_y != node_x: return node_x
        
        node_x.annot = {
                self.x.name: node_x.annot,
                self.y.name: node_y.annot
            }
        return node_x

    def merge_sense_node(self, 
        sense_x: CwnSense, sense_y: CwnSense) -> CwnSense:        
        if sense_x != sense_y:
            return sense_x

        for ex_y in sense_y.examples:
            if ex_y not in sense_x.examples:
                sense_x.examples.append(ex_y)
        sense_x.domain = ",".join([sense_x.domain, sense_y.domain])
        return sense_x

    def merge_synset_node(self, 
        synset_x: CwnSynset, synset_y: CwnSynset) -> CwnSynset:        
        if synset_x != synset_y:
            return synset_x
        
        synset_x.pwn_id = ",".join([synset_x.pwn_id, synset_y.pwn_id])
        synset_x.pwn_word = ",".join([synset_x.pwn_word, synset_y.pwn_word])
        return synset_x

    def merge_edges(self, Ex, Ey):
        edges_map = {}
        # index nodes in Ex
        for edge_x in Ex:
            edge_obj = CwnEdgeFactory.createEdge(edge_x, self.x)            
            edges_map.setdefault(edge_obj, []).append(edge_obj)

        # index nodes in Ey
        for edge_y in Ey:
            edge_obj = CwnEdgeFactory.createEdge(edge_y, self.y)            
            edges_map.setdefault(edge_obj, []).append(edge_obj)
        
        edges_merged = {}              
        for edges_list in edges_map.values():                        
            if len(edges_list) == 1:
                edge_x = edges_list[0]
                new_edge_id = self.map_new_edge_id(edge_x.id)
                edges_merged[new_edge_id] = edge_x
                self.steps.append(("unique", new_edge_id, f"{edge_x.id}"))
            elif len(edges_list) == 2:
                edge_x, edge_y = edges_list
                try:
                    edge_x = self.merge_edge(edge_x, edge_y)
                    new_edge_id = self.map_new_edge_id(edge_x.id)
                    edges_merged[new_edge_id] = edge_x
                    self.steps.append(("merged", new_edge_id, f"{edge_x.id},{edge_y.id}"))
                except ValueError:
                    self.add_conflict_entry(edge_x, edge_y)                               
                    self.steps.append(("conflict", new_edge_id, f"{edge_x.id},{edge_y.id}"))                 
            else:
                print("ERROR: " + str(edges_list))
                raise ValueError("More than two edges are identical")
                           
        # add all edges into merged Graph edges, Vm
        for edge_id, edge_m in edges_merged.items():
            self.Em[edge_id] = edge_m.data()

    def merge_edge(self, 
        edge_x: CwnRelation, edges_set: Set[CwnRelation]) -> CwnRelation:
        for edge_y in edges_set:
            if edge_y != edge_x: continue    
            if edge_y.edge_type != edge_x.edge_type:
                raise ValueError("edge_type mismatch")                
            edge_x.annot = {
                self.x.name: edge_x.annot,
                self.y.name: edge_y.annot
            }
        return edge_x    

    def add_conflict_entry(self, elem_x, elem_y):
        entry = {
            "action": "USE_X|USE_Y|IGNORE",
            "xid": elem_x.id,
            "x": elem_x.data(),
            "yid": elem_y.id,
            "y": elem_y.data()
        }
        self.conflicts.append(entry)
        return 
        