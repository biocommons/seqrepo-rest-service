"""per-thread globals for seqrepo REST APIs

"""


import logging
import os

from biocommons.seqrepo import SeqRepo
from flask import g


_logger = logging.getLogger(__name__)


try:
    seqrepo_dir = os.environ["SEQREPO_DIR"]
    _logger.info(f"Using seqrepo directory from SEQREPO_DIR ({seqrepo_dir})")
except KeyError:
    test_dir = os.path.join(os.path.dirname(__file__), '', '../..', 'tests', 'data', 'seqrepo', 'master')
    if os.path.exists(test_dir):
        seqrepo_dir = os.path.abspath(test_dir)
        _logger.warning(f"Using seqrepo test directory ({seqrepo_dir})")
    else:
        seqrepo_dir = "/usr/local/share/seqrepo/latest"
        _logger.info(f"Using default seqrepo directory ({seqrepo_dir})")


def get_seqrepo():
    return _get_or_create(
        "seqrepo",
        lambda: SeqRepo(root_dir=seqrepo_dir))


def _get_or_create(k, f):
    k = '_' + k
    o = getattr(g, k, None)
    if o is None:
        o = f()
        setattr(g, k, o)
    return o
