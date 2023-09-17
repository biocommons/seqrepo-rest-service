import biocommons.seqrepo
import bioutils
from pkg_resources import get_distribution

from ...threadglobals import get_seqrepo


def get():
    sr = get_seqrepo()

    return {
        "version": get_distribution("seqrepo-rest-service").version,
        "url": "https://github.com/biocommons/seqrepo-rest-service/",
        "dependencies": {
            "seqrepo": {
                "version": biocommons.seqrepo.__version__,
                "root": str(sr._root_dir),
                "url": "https://github.com/biocommons/biocommons.seqrepo/",
            },
            "bioutils": {
                "version": bioutils.__version__,
                "url": "https://github.com/biocommons/bioutils/",
            },
        },
    }
