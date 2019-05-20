import logging
import re

from connexion import NoContent, request

from ...threadglobals import get_seqrepo
from ..utils import get_sequence_id, problem


_logger = logging.getLogger(__name__)

range_re = re.compile("^bytes=(\d+)-(\d+)$")


def get(id, start=None, end=None):
    sr = get_seqrepo()
    seq_id = get_sequence_id(sr, id)
    if seq_id is None:
        return NoContent, 404

    header = request.headers.get("Range", None)
    if header:
        _logger.info(f"Received header `Range: {header}`")
        if start is not None or end is not None:
            return problem(400, "May not send Range header with start and/or end query parameter")
        m = range_re.match(header)
        if not m:
            return problem(400, f"Could not parse range header {header}")
        start, end = map(int, m.groups())
        _logger.info(f"Parsed `{header}` as ({start}, {end}")
        
    seqinfo = sr.sequences.fetch_seqinfo(seq_id)
    
    if start is not None and end is not None:
        if start > end:
            return problem(501, "Invalid coordinates: start > end")
        if not (0 <= start <= end <= seqinfo["len"]):
            return problem(416, "Invalid coordinates: must obey 0 <= start <= end <= sequence_length")

    try:
        return sr.sequences.fetch(seq_id, start, end)
    except KeyError:
        return NoContent, 404
    
