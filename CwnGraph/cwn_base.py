import pickle
from .cwn_graph_utils import CwnGraphUtils

class CwnBase(CwnGraphUtils):
    def __init__(self, fpath):
        with open(fpath, "rb") as fin:
            V, E = pickle.load(fin)
        super(CwnBase, self).__init__(V, E)