import sqlite3
import logging
import pdb
from cwn_sql_template import *

logger = logging.getLogger("CWN_Graph")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("cwn_graph.log", "w", encoding="UTF-8")
ch = logging.StreamHandler()
fh.setLevel(logging.NOTSET)
ch.setLevel(logging.ERROR)
logger.addHandler(ch)
logger.addHandler(fh)


class CWN_Graph:
    def __init__(self, dbconn):
        self.logger = logging.getLogger("CWN_Graph")
        self.cur = dbconn.cursor()
        self.V = {}
        self.E = {}
        self.glyph = {}
        self.import_nodes()
        self.import_edges()
    
    def import_nodes(self):
        self.import_node_cwn_glyph()
        self.import_node_cwn_lemma()
        self.import_node_cwn_sense()
        self.import_node_cwn_facet()
        print("V cardinality: %d " % (len(self.V),))

    def import_edges(self):
        self.import_edge_cwn_lemma()
        self.import_edge_cwn_sense()
        self.import_edge_cwn_facet()
        self.import_edge_cwn_antonym()
        self.import_edge_cwn_holo()
        self.import_edge_cwn_hypo()
        self.import_edge_cwn_mero()
        self.import_edge_cwn_nearsyno()
        self.import_edge_cwn_synonym()
        self.import_edge_cwn_upword()
        self.import_edge_varword()
        self.import_edge_relations()
        print("E cardinality: %d " % (len(self.E),))
        return
    
    def import_node_cwn_glyph(self):
        print("importing glyph nodes")
        rows = self.select_query("SELECT cwn_lemma FROM cwn_lemma")
        counter = 0
        for r in rows:
            gtxt = r[0]
            if r[0] is None: continue
            if r[0][-1] in "0123456789":
                gtxt = r[0][:-1]
            
            if gtxt not in self.glyph:
                counter += 1
                node_data = {
                    "node_type": "glyph",
                    "glyph": gtxt
                }
                gid = "G" + str(counter)
                self.glyph[gtxt] = gid
                self.add_node(gid, node_data)
        
    def import_node_cwn_lemma(self):
        print("importing lemma nodes")
        rows = self.select_query("SELECT * FROM cwn_lemma")
        for r in rows:        
            if r[0] is None or len(r[0]) == 0:
                logger.info("Skip lemma with no id: %s" % (r[1],))
                continue

            node_id = r[0]
            node_data = {
                "node_type": "lemma",
                "lemma": r[1],
                "zhuyin": r[3]
            }
            self.add_node(node_id, node_data)

    def import_node_cwn_sense(self):
        print("importing sense nodes")
        rows = self.select_query(
                "SELECT sense_id, sense_def, domain_id, group_concat(pos) " + 
                "FROM cwn_sense " +
                "LEFT JOIN pos " +
                "ON cwn_sense.sense_id == pos.cwn_id " + 
                "GROUP BY sense_id")
                
        rows += self.select_query(
                "SELECT sense_tmpid, sense_def, domain_id, group_concat(pos) " + 
                "FROM cwn_sensetmp " +
                "LEFT JOIN pos " +
                "ON cwn_sensetmp.sense_tmpid == pos.cwn_id " + 
                "GROUP BY sense_tmpid"
                )

        for r in rows:
            if r[0] is None or len(r[0]) == 0:
                continue
            node_id = r[0]
            node_data = {
                "node_type": "sense",
                "def": r[1],
                "domain": r[2] if r[2] is not None else "",
                "pos": r[3] if r[3] is not None else ""
                }
            self.add_node(node_id, node_data)


    def import_node_cwn_facet(self):
        print("importing facet nodes")
        rows = self.select_query(
                "SELECT facet_id, facet_def, domain_id, group_concat(pos) " + 
                "FROM cwn_facet " +
                "LEFT JOIN pos " +
                "ON cwn_facet.facet_id == pos.cwn_id " + 
                "GROUP BY facet_id")
                
        rows += self.select_query(
                "SELECT facet_tmpid, facet_def, domain_id, group_concat(pos) " + 
                "FROM cwn_facettmp " +
                "LEFT JOIN pos " +
                "ON cwn_facettmp.facet_tmpid == pos.cwn_id " + 
                "GROUP BY facet_tmpid"
                )

        for r in rows:
            if r[0] is None or len(r[0]) == 0:
                continue
            node_id = r[0]
            node_data = {
                "node_type": "facet",
                "def": r[1],
                "domain": r[2] if r[2] is not None else "",
                "pos": r[3] if r[3] is not None else ""
                }
            self.add_node(node_id, node_data)
    
    def import_edge_cwn_lemma(self):
        print("importing lemma edges")
        rows = self.select_query(
                "SELECT cwn_lemma, lemma_id FROM cwn_lemma "
               )

        for r in rows:
            gtxt = r[0]
            if r[0][-1] in "0123456789":
                gtxt = r[0][:-1]
            
            if gtxt in self.glyph:
                gid = self.glyph[gtxt]
                self.add_edge(gid, r[1], {"edge_type": "has_lemma"})        

    def import_edge_cwn_sense(self):
        print("importing sense edges")
        rows = self.select_query(
                "SELECT lemma_id, sense_id FROM cwn_sense " + 
                "UNION " +
                "SELECT lemma_id, sense_tmpid FROM cwn_sensetmp"
               )
        for r in rows:
            self.add_edge(r[0], r[1], {"edge_type": "has_sense"})        

    def import_edge_cwn_facet(self):
        print("importing facet edges")
        rows = self.select_query(
                "SELECT sense_id, facet_id FROM cwn_facet "+
                "UNION " +
                "SELECT sense_tmpid, facet_tmpid FROM cwn_facettmp "
               )
        for r in rows:
            self.add_edge(r[0], r[1], {"edge_type": "has_facet"})        

    def import_edge_cwn_antonym(self):
        print("importing antonym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_antonym", "cwn_antotmp", "antonym_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "antonym"})        
        
    def import_edge_cwn_synonym(self):
        print("importing synonym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_synonym", "cwn_synotmp", "synonym_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "synonym"})        
    
    def import_edge_cwn_holo(self):
        print("importing holonym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_holo", "cwn_holotmp", "holo_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "holonym"})        

    def import_edge_cwn_hypo(self):
        print("importing hyponym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_hypo", "cwn_hypotmp", "hypo_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "hyponym"})        

    def import_edge_cwn_mero(self):
        print("importing meronym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_mero", "cwn_merotmp", "mero_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "meronym"})        

    def import_edge_cwn_nearsyno(self):
        print("importing nearsynonym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_nearsyno", "cwn_nearsynotmp", "nearsyno_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "nearsynonym"})        
            
    def import_edge_cwn_upword(self):
        print("importing hypernym edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_upword", "cwn_uptmp", "up_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "hypernym"})        

    def import_edge_varword(self):
        print("importing varwords edges")
        rows = self.select_query(
               self.prepare_relation_sql(
                   "cwn_varword", "cwn_vartmp", "var_word")
               )
        for r in rows:
            resolved_id = self.resolve_refid(r[1], r[2], r[3])            
            self.add_edge(r[0], resolved_id, {"edge_type": "varword"})        

    def import_edge_relations(self):
        print("importing other relation edges")
        rows = self.select_query(cwn_sql_other_relations)
        for r in rows:
            resolved_id = self.resolve_refid(r[4], r[5], r[3])            
            from_cwn_id = r[0]+r[1]+r[2]
            self.add_edge(from_cwn_id, resolved_id, {"edge_type": "varword"})        

    def prepare_relation_sql(self, tbl, tbltmp, wfield):
        sql = cwn_sql_relations_templ.format(tbl, tbltmp, wfield)
        return sql
        

    def add_node(self, node_id, node_data):
        V = self.V
        if len(node_id) == 0: 
            logger.warning("Empty node id: %a" % (node_data, ))
            return

        if node_id not in V:
            V[node_id] = node_data
        else:
            logger.warning("Duplicate node id: %s" % (node_id,))
    
    def add_edge(self, from_id, to_id, edge_data):
        V = self.V
        E = self.E
        if from_id not in V:
            self.logger.warning("Cannot find the from node when adding edge: "+
                    "%s - %s" % (from_id, to_id))
            return
        
        if to_id not in V:
            self.logger.warning("Cannot find the to node when adding edge: "+
                    "%s - %s" % (from_id, to_id))
            return
        
        if (from_id, to_id) not in E:
            E[(from_id, to_id)] = edge_data
        else:
            self.logger.info("Duplicate edge: %s - %s" % (from_id, to_id))


    def select_query(self, sqlcmd):
        return self.cur.execute(sqlcmd).fetchall()
    
    def resolve_refid(self, lemma_id, ref_id, lemma):
        # if ref_id is None, lemma_id is in fact cwn_id        
        if ref_id is None:
            return lemma_id
        
        if lemma_id is None:
            self.logger.warning("Cannot find lemma %s" % (lemma,))
            return ""

        if len(ref_id) != 4:
            self.logger.warning("invalid ref_id format")
            return ""

        sense_part = ref_id[0:2]
        homo_part = ref_id[2]
        facet_part = ref_id[3]
        if facet_part == '0':
            return lemma_id + sense_part
        else:
            return lemma_id + sense_part + "0" + facet_part
