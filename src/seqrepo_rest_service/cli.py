"""start seqrepo rest service"""

import argparse
import importlib.resources
import logging
import os
import pathlib
import time

from biocommons.seqrepo import SeqRepo
import coloredlogs
import connexion
from flask import redirect
from waitress import serve

from . import __version__

WAIT_POLL_PERIOD = 15  # seconds between polling for SEQREPO PATH


_logger = logging.getLogger(__name__)
resources = importlib.resources.files(__package__)

def _parse_opts():
    ap = argparse.ArgumentParser(description=__doc__.split()[0])
    ap.add_argument(
        "SEQREPO_INSTANCE_DIR",
        type=pathlib.Path,
        help="SeqRepo instance directory (e.g., /usr/local/share/seqrepo/2021-01-29)",
    )
    ap.add_argument(
        "--wait-for-path",
        "-w",
        action="store_true",
        default=False,
        help="Wait for path to exist before starting (useful for docker-compose)",
    )
    opts = ap.parse_args()
    return opts


def main():
    coloredlogs.install(level="INFO")

    if "SEQREPO_DIR" in os.environ:
        _logger.warn("SEQREPO_DIR environment variable is now ignored")

    opts = _parse_opts()

    seqrepo_dir = opts.SEQREPO_INSTANCE_DIR
    if opts.wait_for_path:
        while not seqrepo_dir.exists():
            _logger.info(f"{seqrepo_dir}: waiting for existence")
            time.sleep(WAIT_POLL_PERIOD)
        _logger.info(f"{seqrepo_dir}: path found")
    _ = SeqRepo(seqrepo_dir.as_posix())  # test opening

    cxapp = connexion.App(__name__, debug=False)
    cxapp.app.url_map.strict_slashes = False
    cxapp.app.config["seqrepo_dir"] = seqrepo_dir
    cxapp.app.config["log_request_last_log_time"] = 0

    spec_files = []

    # seqrepo interface
    spec_fn = resources / "seqrepo" / "openapi.yaml"
    cxapp.add_api(str(spec_fn), validate_responses=True, strict_validation=True)
    spec_files += [spec_fn]

    @cxapp.route("/")
    @cxapp.route("/seqrepo")
    def seqrepo_ui():
        return redirect("/seqrepo/1/ui/")

    # refget interface
    spec_fn = resources / "refget" / "refget-openapi.yaml"
    cxapp.add_api(str(spec_fn), validate_responses=True, strict_validation=True)
    spec_files += [spec_fn]

    @cxapp.route("/refget")
    def refget_ui():
        return redirect("/refget/1/ui/")

    # Do not use Flask's builting development server. 
    # cxapp.run(host="0.0.0.0", extra_files=spec_files)
    
    # Use the Waitress production server 
    serve(cxapp, host='0.0.0.0', port=5000, threads = 10)

if __name__ == "__main__":
    main()