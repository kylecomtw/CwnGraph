import json

def dump_json(V, E):    
    with open("cwn_graph_nodes.json", "w", encoding="UTF-8") as fout:
        json.dump(V, fout, indent=2, ensure_ascii=False)
    
    with open("cwn_graph_edges.json", "w", encoding="UTF-8") as fout:        
        strE = {str(k): v for k, v in E.items()}
        json.dump(strE, fout, indent=2, ensure_ascii=False)