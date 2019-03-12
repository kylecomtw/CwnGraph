import logging
from CwnGraph.cwn_types import GraphStructure

logger = logging.getLogger()
logging.basicConfig(level="DEBUG", format="[%(levelname)s] %(message)s")

def test_graph_merge():
    Gx = GraphStructure()
    Gy = GraphStructure()
    Gx.V = {
        "123": {"123"},
        "323": {"333"}
    }
    Gx.E = {
        "123-323": {}
    }


    logger.debug("debug info")
    return True
