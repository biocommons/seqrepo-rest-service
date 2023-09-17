"""per-thread globals for seqrepo REST APIs

"""

import logging
import os

from biocommons.seqrepo import SeqRepo
from flask import current_app, g

_logger = logging.getLogger(__name__)


def get_seqrepo():
    seqrepo_dir = current_app.config["seqrepo_dir"]
    _logger.info(f"Opening {seqrepo_dir=}")
    return _get_or_create("seqrepo", lambda: SeqRepo(root_dir=seqrepo_dir))


def _get_or_create(k, f):
    k = "_" + k
    o = getattr(g, k, None)
    if o is None:
        o = f()
        setattr(g, k, o)
    return o
