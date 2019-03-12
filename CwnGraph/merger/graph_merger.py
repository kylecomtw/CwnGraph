from ..cwn_types import GraphStructure

class GraphMerger():
    def __init__(self, Gx:GraphStructure, Gy:GraphStructure):
        self.Gx = Gx
        self.Gy = Gy
        self.Gm = GraphStructure()
        super(GraphMerger, self).__init__(Gx, Gy)
    
    def merge(self, resolve_strategy: "ResolveStrategy"):
        self.merge_elements(self.Gx.V, self.Gy.V, self.Gm.V)
        self.merge_elements(self.Gx.E, self.Gy.E, self.Gm.E)

    def merge_elements(self, xdict, ydict, merged):
        xkeys = list(xdict.keys()).copy()
        for ykey, yvalue in ydict.items():
            if ykey in xdict:
                merged[ykey] = xdict[ykey]
                
            else:
                merged[ykey] = ydict[ykey]
        
        for xkey in xkeys:
            merged[xkey] = xdict[xkey]
        
class ResolveStrategy:
    @classmethod
    def resolve(cls):
        raise NotImplementedError()

class DefaultResolveStrategy:
    @classmethod
    def resolve(cls, elem_x, elem_y):
        return elem_x