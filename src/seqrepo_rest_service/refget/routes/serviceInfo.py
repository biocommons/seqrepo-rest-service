import biocommons.seqrepo
import bioutils

from ... import __version__
from ...threadglobals import get_seqrepo


def get():
    sr = get_seqrepo()

    return {
        "service": {
            "algorithms": ["md5", "trunc512"],
            "circular_supported": False,
            "subsequence_limit": None,
            "supported_api_versions": ["1.0"],
        },
        "x-config": {
            "seqrepo-rest-service": {
                "version": __version__,
                "url": "https://github.com/biocommons/seqrepo-rest-service/",
            },
            "seqrepo": {
                "version": biocommons.seqrepo.__version__,
                "root": sr._root_dir,
                "url": "https://github.com/biocommons/biocommons.seqrepo/",
            },
            "bioutils": {
                "version": bioutils.__version__,
                "url": "https://github.com/biocommons/bioutils/",
            },
        },
    }
