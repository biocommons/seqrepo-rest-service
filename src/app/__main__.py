"""start refget webservice

"""

from pkg_resources import resource_filename

import coloredlogs
import connexion
from flask import Flask, redirect


def main():
    coloredlogs.install(level="INFO")

    cxapp = connexion.App(__name__, debug=True)

    spec_fn = "refget/refget-openapi.yaml"
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
