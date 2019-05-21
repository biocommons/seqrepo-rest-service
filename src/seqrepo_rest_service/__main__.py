"""start refget webservice

"""

import logging

from pkg_resources import get_distribution, resource_filename

import coloredlogs
import connexion
from flask import Flask, redirect


_logger = logging.getLogger(__name__)
__version__ = get_distribution("seqrepo-rest-service").version


def main():
    coloredlogs.install(level="INFO")

    cxapp = connexion.App(__name__, debug=True)
    cxapp.app.url_map.strict_slashes = False

    spec_fn = resource_filename(__name__, "refget/refget-openapi.yaml")
    cxapp.add_api(spec_fn,
                  validate_responses=True,
                  strict_validation=True)

    @cxapp.route('/')
    def index():
        return redirect("/refget/1/ui")

    cxapp.run(host="0.0.0.0",
              extra_files=[spec_fn],
              processes=1)



if __name__ == "__main__":
    main()
