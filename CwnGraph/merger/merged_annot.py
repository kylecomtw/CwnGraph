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
    
    def get_hash(self):
        byteStr = pickle.dumps((self.V, self.E))
        hashStr = ("{0:x}".format(hash(byteStr)))[:6]
        return hashStr
    
    def resolve(self):
        raise NotImplementedError()

    def report(self):
        raise NotImplementedError()
    


