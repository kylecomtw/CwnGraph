import pickle
from ..cwn_types import GraphStructure
from datetime import datetime
from .. import cwnio

class MergedAnnotation(GraphStructure):
    PREFIX = "annot/annot_merged"
    def __init__(self, meta, V, E):
        super(MergedAnnotation, self).__init__()
        self.V = V
        self.E = E
        self.meta = meta                                
    
    def load(self, name): 
        try:       
            self.meta, self.V, self.E = \
                cwnio.load_annot_json(f"{MergedAnnotation.PREFIX}_{name}.json")
            return True
        except FileNotFoundError:
            return False
        
    def save(self, with_timestamp=False):        
        hashstr = self.get_hash()
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        self.meta["snapshot"] = timestamp
        cwnio.ensure_dir("annot")
        if with_timestamp:
            cwnio.dump_annot_json(self.meta, self.V, self.E, 
                f"{MergedAnnotation.PREFIX}_{hashstr}_{timestamp}.json")
        else:
            cwnio.dump_annot_json(self.meta, self.V, self.E, 
                f"{MergedAnnotation.PREFIX}_{hashstr}.json")          
    
    def resolve(self):
        conflicts = self.meta.get("conflicts", {})
        new_conflicts = []
        for conf_x in conflicts:
            action = conf_x.get("action", "")
            if action == "USE_X":
                eid = conf_x["xid"]
                edata = conf_x["x"]
            elif action == "USE_Y":
                eid = conf_x["yid"]
                edata = conf_x["y"]
            elif action == "IGNORE":
                pass
            else:
                print("unrecognized action: ", action)
                new_conflicts.append(conf_x)
            self.E[eid] = edata
        self.meta["conflicts"] = new_conflicts
        if new_conflicts:
            print(f"{len(new_conflicts)} conflict(s) remained")

    


