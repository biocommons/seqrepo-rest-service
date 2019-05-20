import logging

from connexion import NoContent, problem
import connexion

from ...threadglobals import get_seqrepo
from ..utils import get_sequence_id


_logger = logging.getLogger(__name__)


def get(id, start=None, end=None):
    sr = get_seqrepo()
    seq_id = get_sequence_id(sr, id)
    seqinfo = sr.sequences.fetch_seqinfo(seq_id)
    
    if start is not None and end is not None:
        if start > end:
            return problem(501, "Bad Request", "Invalid coordinates: start > end")
        if not (0 <= start <= end <= seqinfo["len"]):
            return problem(416, "Bad Request", "Invalid coordinates: must obey 0 <= start <= end <= sequence_length")

    try:
        return sr.sequences.fetch(seq_id, start, end)
    except KeyError:
        return NoContent, 404
    
