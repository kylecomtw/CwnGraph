
import sys
sys.path.append("../CwnGraph")
import logging
from CwnGraph.cwn_types import GraphStructure
from CwnGraph import CwnAnnotator, CwnBase
from CwnGraph.merger import annot_merger


logger = logging.getLogger()
logging.basicConfig(level="DEBUG", format="[%(levelname)s] %(message)s")

def test_graph_merge():
    cwn = CwnBase("data/cwn_graph.pyobj")    
    annot1 = CwnAnnotator(cwn, "test_a")
    annot2 = CwnAnnotator(cwn, "test_b")
    
    am = annot_merger.AnnotationMerger(annot1, annot2)
    
    merged = am.merge()
    
    assert len(merged.V) > 0, "merged graph has non-empty vertices"
    assert len(merged.E) > 0, "merged graph has non-empty edges"

    merged.save()
