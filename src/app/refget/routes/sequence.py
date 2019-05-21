import logging
import re

from connexion import NoContent, request

from ...threadglobals import get_seqrepo
from ..utils import get_sequence_id, problem


_logger = logging.getLogger(__name__)

range_re = re.compile("^bytes=(\d+)-(\d+)$")


def get(id, start=None, end=None):
    range_header = request.headers.get("Range", None)
    if range_header:
        _logger.debug(f"Received header `Range: {range_header}`")
        if start is not None or end is not None:
            return problem(400, "May not send Range header with start and/or end query parameter")
        m = range_re.match(range_header)
        if not m:
            return problem(400, f"Could not parse range header {range_header}")
        start, end = int(m.group(1)), int(m.group(2)) + 1
        _logger.debug(f"Parsed `{range_header}` as ({start}, {end})")
        if start > end:
            return problem(416, f"Range queries may specify start > end")
        
    sr = get_seqrepo()
    seq_id = get_sequence_id(sr, id)
    if not seq_id:
        return NoContent, 404
    seqinfo = sr.sequences.fetch_seqinfo(seq_id)
   
    if start is not None and end is not None:
        if start >= seqinfo["len"]:
            return problem(416, "Invalid coordinates: start > sequence length")
        if end > seqinfo["len"] and not range_header:
            # NB Compliance tests imply that end may be > len if in range header
            return problem(416, "Invalid coordinates: end > sequence length")
        if start > end:
            return problem(501, "Invalid coordinates: start > end")
        if not (0 <= start <= end <= seqinfo["len"]) and not range_header:
            return problem(416, "Invalid coordinates: must obey 0 <= start <= end <= sequence_length")

    try:
        status = 206 if ((start or end) and range_header) else 200
        return sr.sequences.fetch(seq_id, start, end), status
    except KeyError:
        return NoContent, 404
    
