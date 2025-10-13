import logging
import re

from biocommons.seqrepo import SeqRepo
from connexion import NoContent, request

from ...threadglobals import get_seqrepo
from ...utils import get_sequence_id, problem, valid_content_types

_logger = logging.getLogger(__name__)

range_re = re.compile(r"^bytes=(\d+)-(\d+)$")


class HTTPError(Exception):
    """Custom Error"""

    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


def _validate_range_header(range_header, start: int | None = None, end: int | None = None):
    """
    Validate the range header against parameters

    Raises an HTTPError if:
    - A range header is provided along with `start` or `end` query parameters.
    - The range header format is invalid.
    - The parsed start is greater than the end.

    :param range_header: string representing the range
    :param start: optional start coordinate
    :param end: optional end coordinate
    :raises HTTPError: on invalid header or conflicting parameters
    """
    if range_header:
        _logger.debug("Received header `Range: %s`", range_header)
        if start is not None or end is not None:
            raise HTTPError(400, "May not send Range header with start and/or end query parameter")

        m = range_re.match(range_header)
        if not m:
            raise HTTPError(400, f"Could not parse range header {range_header}")

        start, end = int(m.group(1)), int(m.group(2)) + 1
        _logger.debug("Parsed `%s` as (%i, %i)", range_header, start, end)
        if start > end:
            raise HTTPError(416, "Range queries may specify start > end")


def _validate_start_and_end(
    sr: SeqRepo,
    seq_id: str,
    range_header,
    start: int | None = None,
    end: int | None = None,
):
    """
    Validate start and end query parameters against the sequence length

    Raises an HTTPError if:
    - `start` is greater than or equal to the sequence length.
    - `end` is greater than the sequence length and no range header is present.
    - `start` is greater than `end`.
    - Coordinates do not fall within valid bounds.

    :param sr: SeqRepo instance
    :param seq_id: sequence identifier
    :param range_header: string representing the range
    :param start: optional start coordinate
    :param end: optional end coordinate
    :raises HTTPError: on invalid coordinate logic
    """
    seqinfo = sr.sequences.fetch_seqinfo(seq_id)

    if start is not None and end is not None:
        if start >= seqinfo["len"]:
            raise HTTPError(416, "Invalid coordinates: start > sequence length")
        if end > seqinfo["len"] and not range_header:
            # NB Compliance tests imply that end may be > len if in range header
            raise HTTPError(416, "Invalid coordinates: end > sequence length")
        if start > end:
            raise HTTPError(501, "Invalid coordinates: start > end")
        if not (0 <= start <= end <= seqinfo["len"]) and not range_header:
            raise HTTPError(
                416, "Invalid coordinates: must obey 0 <= start <= end <= sequence_length"
            )


def get(query: str, start=None, end=None):
    """
    Retrieve a sequence or a subsequence

    :param query: string identifying the sequence
    :param start: optional start coordinate
    :param end: optional end coordinate
    return: tuple of (sequence bytes or NoContent, HTTP status code)
    """
    accept_header = request.headers.get("Accept", None)
    if accept_header and accept_header not in valid_content_types:
        return problem(406, "Invalid Accept header")

    range_header = request.headers.get("Range", None)
    try:
        _validate_range_header(range_header, start, end)
    except HTTPError as http_error:
        return problem(http_error.status_code, http_error.message)

    sr = get_seqrepo()
    seq_id = get_sequence_id(sr, query)
    if not seq_id:
        return NoContent, 404
    try:
        _validate_start_and_end(sr, seq_id, range_header, start, end)
    except HTTPError as http_error:
        return problem(http_error.status_code, http_error.message)

    try:
        status = 206 if ((start or end) and range_header) else 200
        return sr.sequences.fetch(seq_id, start, end), status
    except KeyError:
        return NoContent, 404
