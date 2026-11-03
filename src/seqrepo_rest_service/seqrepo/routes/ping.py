from importlib import metadata

import biocommons.seqrepo
import bioutils
from flask import current_app

from ...threadglobals import get_seqrepo


def get():
    get_seqrepo()  # ensure seqrepo opens

    return {
        "version": metadata.version("seqrepo-rest-service"),
        "url": "https://github.com/biocommons/seqrepo-rest-service/",
        "dependencies": {
            "seqrepo": {
                "version": biocommons.seqrepo.__version__,
                "root": str(current_app.config["seqrepo_dir"]),
                "url": "https://github.com/biocommons/biocommons.seqrepo/",
            },
            "bioutils": {
                "version": bioutils.__version__,
                "url": "https://github.com/biocommons/bioutils/",
            },
        },
    }
