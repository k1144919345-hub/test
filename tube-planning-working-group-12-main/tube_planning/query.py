def _VALID_SERVICES() -> tuple[str]:
    """Return a tuple of strings, corresponding to the web services that
    can be queried.

    We use a function, rather than a module-scoped variable, to avoid
    complications that may arise from unintentional edits to a module-
    scoped variable.

    THIS FUNCTION IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
    """
    return (
        "index/query",
        "line/query",
        "stations/query",
        "proposals/routes",
        "proposals/costs",
    )


def _WEB_SERVICE() -> str:
    """Return a string corresponding to the root address of the web
    service;

    https://rse-with-python.arc.ucl.ac.uk/tube-planning

    We use a function, rather than a module-scoped variable, to avoid
    complications that may arise from unintentional edits to a module-
    scoped variable.

    THIS FUNCTION IS PROVIDED TO YOU, AND DOES NOT NEED TO BE TESTED IN YOUR TEST SUITE.
    """
    return "https://rse-with-python.arc.ucl.ac.uk/tube-planning"


def send_query(service, **query_params):
    raise TubePlanningError("Network calls are not available in offline mode.")


def fetch_tfl_network():
    raise TubePlanningError("Fetching remote network is unsupported in this build.")


def fetch_fixed_costs(date):
    raise TubePlanningError("Fetching remote costs is unsupported in this build.")


def fetch_proposed_line(proposal_name):
    raise TubePlanningError("Fetching remote proposal is unsupported in this build.")
