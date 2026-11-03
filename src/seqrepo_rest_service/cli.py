"""start seqrepo rest service"""

import argparse
import importlib.resources
import logging
import os
import pathlib
import time

import coloredlogs
import connexion
from biocommons.seqrepo import SeqRepo
from flask import redirect

WAIT_POLL_PERIOD = 15  # seconds between polling for SEQREPO PATH

# Same defaults as biocommons.seqrepo: $SEQREPO_ROOT_DIR (or /usr/local/share/seqrepo)/latest
DEFAULT_SEQREPO_INSTANCE_DIR = (
    pathlib.Path(os.environ.get("SEQREPO_ROOT_DIR", "/usr/local/share/seqrepo")) / "latest"
)


_logger = logging.getLogger(__name__)
resources = importlib.resources.files(__package__)


def _parse_opts():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "SEQREPO_INSTANCE_DIR",
        type=pathlib.Path,
        nargs="?",
        default=DEFAULT_SEQREPO_INSTANCE_DIR,
        help="SeqRepo instance directory (default: %(default)s)",
    )
    ap.add_argument(
        "--wait-for-path",
        "-w",
        action="store_true",
        default=False,
        help="Wait for path to exist before starting (useful for docker-compose)",
    )
    return ap.parse_args()


def main():
    coloredlogs.install(level="INFO")

    if "SEQREPO_DIR" in os.environ:
        _logger.warning("SEQREPO_DIR environment variable is now ignored")

    opts = _parse_opts()

    seqrepo_dir = opts.SEQREPO_INSTANCE_DIR
    if opts.wait_for_path:
        while not seqrepo_dir.exists():
            _logger.info("%s: waiting for existence", seqrepo_dir)
            time.sleep(WAIT_POLL_PERIOD)
        _logger.info("%s: path found", seqrepo_dir)
    _ = SeqRepo(seqrepo_dir.as_posix())  # test opening

    cxapp = create_app(seqrepo_dir)
    cxapp.run(host="0.0.0.0", port=5000)  # noqa: S104


def create_app(seqrepo_dir: pathlib.Path) -> connexion.App:
    """Build the connexion app serving the seqrepo and refget APIs for seqrepo_dir"""
    cxapp = connexion.App(__name__)
    cxapp.app.url_map.strict_slashes = False
    cxapp.app.config["seqrepo_dir"] = seqrepo_dir

    # seqrepo interface
    spec_fn = resources / "seqrepo" / "openapi.yaml"
    cxapp.add_api(str(spec_fn), validate_responses=True, strict_validation=True)

    @cxapp.route("/")
    @cxapp.route("/seqrepo")
    def seqrepo_ui():
        return redirect("/seqrepo/1/ui/")

    # refget interface
    spec_fn = resources / "refget" / "refget-openapi.yaml"
    # pythonic_params maps spec param `id` to handler arg `id_` (avoids shadowing builtin)
    cxapp.add_api(
        str(spec_fn), validate_responses=True, strict_validation=True, pythonic_params=True
    )

    @cxapp.route("/refget")
    def refget_ui():
        return redirect("/refget/1/ui/")

    return cxapp


if __name__ == "__main__":
    main()
