import logging
import re
import time

from connexion import NoContent, request

from ...threadglobals import get_seqrepo, log_request
from ...utils import get_sequence_ids, problem

_logger = logging.getLogger(__name__)


def get(alias, start=None, end=None):
    if start is not None and end is not None:
        if start > end:
            return problem(422, "Invalid coordinates: start > end")
    
    start_time_real = time.perf_counter()
    start_time_user = time.process_time()
    
    sr = get_seqrepo()
    
    seq_ids = get_sequence_ids(sr, alias)
    if not seq_ids:
        return NoContent, 404
    if len(seq_ids) > 1:
        return problem(422, f"Multiple sequences exist for alias '{alias}'")
    seq_id = seq_ids[0]
    f = sr.sequences.fetch(seq_id, start, end), 200

    stop_time_real = time.perf_counter()
    stop_time_user = time.process_time()

    log_request(alias, start, end, stop_time_real - start_time_real, stop_time_user - start_time_user)
        
    return f
