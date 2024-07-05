"""per-thread globals for seqrepo REST APIs"""

import logging

from biocommons.seqrepo import SeqRepo
from flask import current_app

_logger = logging.getLogger(__name__)


def get_seqrepo():
    seqrepo_dir = current_app.config["seqrepo_dir"]
    if _get_or_create("seqrepo", None, False) is None:
        _logger.info("Opening seqrepo_dir=%s", seqrepo_dir)
    return _get_or_create("seqrepo", lambda: SeqRepo(root_dir=seqrepo_dir))


def _get_or_create(k, f, create=True):
    k = "_" + k
    o = getattr(_get_or_create, k, None)
    if o is None and create:
        o = f()
        setattr(_get_or_create, k, o)
    return o
