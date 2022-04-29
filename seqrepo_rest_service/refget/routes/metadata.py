import logging

from connexion import NoContent, request

from seqrepo_rest_service.threadglobals import get_seqrepo
from seqrepo_rest_service.utils import get_sequence_id, base64url_to_hex, problem, valid_content_types


_logger = logging.getLogger(__name__)


def get(id):
    accept_header = request.headers.get("Accept", None)
    if accept_header and accept_header not in valid_content_types:
        _logger.warn(f"{accept_header} not valid")
        return problem(406, "Invalid Accept header")
    
    sr = get_seqrepo()
    seq_id = get_sequence_id(sr, id)
    if not seq_id:
        return NoContent, 404
    seqinfo = sr.sequences.fetch_seqinfo(seq_id)
    aliases = sr.aliases.fetch_aliases(seq_id)

    md5_rec = [a for a in aliases if a["namespace"] == "MD5"]
    md5_id = md5_rec[0]["alias"] if md5_rec else None

    md = {
        "id": seq_id,
        "md5": md5_id,
        "trunc512": base64url_to_hex(seq_id),
        "length": seqinfo["len"],
        "aliases": [
            {"naming_authority": a["namespace"], "alias": a["alias"]}
            for a in aliases
            ]
        }

    return {"metadata": md}, 200
