"""start refget webservice

"""

from pathlib import Path
import logging
import os

from pkg_resources import get_distribution, resource_filename

import coloredlogs
import connexion
from flask import Flask, redirect


_logger = logging.getLogger(__name__)
# __version__ = get_distribution("seqrepo-rest-service").version
__version__ = "1.0.0"
APP_ROOT = Path(__file__).resolve().parents[0]


def main():
    coloredlogs.install(level="INFO")

    if "SEQREPO_DIR" not in os.environ:
        _logger.warn("SEQREPO_DIR is undefined; rest service will use `latest`")

    cxapp = connexion.App(__name__, debug=True)
    cxapp.app.url_map.strict_slashes = False

    spec_files = []

    # seqrepo interface
    spec_fn = f"{APP_ROOT}/seqrepo_rest_service/seqrepo/openapi.yaml"
    cxapp.add_api(spec_fn,
                  validate_responses=True,
                  strict_validation=True)
    spec_files += [spec_fn]

    @cxapp.route('/')
    @cxapp.route('/seqrepo')
    def seqrepo_ui():
        return redirect("/seqrepo/1/ui/")


    # refget interface
    spec_fn = f"{APP_ROOT}/seqrepo_rest_service/refget/refget-openapi.yaml"
    cxapp.add_api(spec_fn,
                  validate_responses=True,
                  strict_validation=True)
    spec_files += [spec_fn]

    @cxapp.route('/refget')
    def refget_ui():
        return redirect("/refget/1/ui/")


    _logger.info("Also watching " + str(spec_files))
    cxapp.run(host="0.0.0.0",
              extra_files=spec_files)

if __name__ == "__main__":
    main()
