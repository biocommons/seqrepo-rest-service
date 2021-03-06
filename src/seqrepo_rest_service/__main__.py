"""start refget webservice

"""

import logging
import os

from pkg_resources import get_distribution, resource_filename

import coloredlogs
import connexion
from flask import Flask, redirect


_logger = logging.getLogger(__name__)
__version__ = get_distribution("seqrepo-rest-service").version


def main():
    coloredlogs.install(level="INFO")

    if "SEQREPO_DIR" not in os.environ:
        _logger.warn("SEQREPO_DIR is undefined; rest service will use `latest`")

    cxapp = connexion.App(__name__, debug=True)
    cxapp.app.url_map.strict_slashes = False

    spec_files = []

    # seqrepo interface
    spec_fn = resource_filename(__name__, "seqrepo/openapi.yaml")
    cxapp.add_api(spec_fn,
                  validate_responses=True,
                  strict_validation=True)
    spec_files += [spec_fn]

    @cxapp.route('/')
    @cxapp.route('/seqrepo')
    def seqrepo_ui():
        return redirect("/seqrepo/1/ui/")


    # refget interface
    spec_fn = resource_filename(__name__, "refget/refget-openapi.yaml")
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
