import sqlite3
import pickle
import CwnGraph
from CwnGraph import CWN_Graph, CwnGraphUtils
import sys
import os
import pdb

if __name__ == "__main__":
    if len(sys.argv) > 1:
        task = sys.argv[1]
    else:
        task = "out"

    if task == "encode":
        conn = sqlite3.connect("data/cwn-2016.sqlite")
        cg = CWN_Graph(conn)
        with open("data/cwn_graph.pyobj", "wb") as fout:
            pickle.dump((cg.V, cg.E), fout)
    elif task == "query":
        with open("data/cwn_graph.pyobj", "rb") as fin:
            V, E = pickle.load(fin)

        cgu = CwnGraphUtils(V, E)
        gid = cgu.find_glyph("田")
        print(gid)
        lemmas = [x[0] for x in cgu.find_edges(gid)]
        print(lemmas)
        senses = [x[0] for lid in lemmas for x in cgu.find_edges(lid)]
        print(senses)
        rel = cgu.find_edges("06014001")

        print(rel)
    elif task == "json":
        if not os.path.exists("data/cwn_graph.pyobj"):
            print("Cannot find cwn_graph.pyobj")
            exit()

        with open("data/cwn_graph.pyobj", "rb") as fin:
            V, E = pickle.load(fin)
            CwnGraph.io.dump_json(V, E, "data/cwn_graph")

    else:
        print("Not recognized task")
