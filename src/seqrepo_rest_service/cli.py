"""start refget webservice

"""

from genericpath import isdir
import logging
import os
import sys

from pkg_resources import get_distribution, resource_filename

from biocommons.seqrepo import SeqRepo
import coloredlogs
import connexion
from flask import Flask, redirect


_logger = logging.getLogger(__name__)
__version__ = get_distribution("seqrepo-rest-service").version


def main():
    coloredlogs.install(level="INFO")

    if "SEQREPO_DIR" in os.environ:
        _logger.warn("SEQREPO_DIR environment variable is now ignored")
        
    # TODO: use argparse
    if len(sys.argv) != 2:
        raise RuntimeError("Usage: seqrepo-rest-service <dir>")

    seqrepo_dir = sys.argv[1]
    _logger.info(f"Using {seqrepo_dir=} from command line")
    _ = SeqRepo(seqrepo_dir)   # test opening

    cxapp = connexion.App(__name__, debug=True)
    cxapp.app.url_map.strict_slashes = False
    cxapp.app.config["seqrepo_dir"] = seqrepo_dir

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
