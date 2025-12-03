from argparse import ArgumentParser
import sys


class CLIParser(ArgumentParser):
    """
    A custom subclass of ``argparse.ArgumentParser``,
    which changes the default behaviour on an error in CLI parsing to print the
    command-line help, as opposed to throwing an error to stderr.
    """

    def error(self, message):
        sys.stderr.write(
            f"ERROR parsing input arguments.\n{message}\nRefer to CLI usage below:\n\n"
        )
        self.print_help()
        sys.exit(2)


def read_fixed_costs(file):
    import json
    import csv
    from pathlib import Path

    path = Path(file)
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".json":
        with open(path, "r") as fh:
            data = json.load(fh)
            if not isinstance(data, dict):
                raise ValueError("Cost JSON must be an object mapping names to values.")
            return {k: float(v) for k, v in data.items()}

    costs: dict[str, float] = {}
    with open(path, newline="") as fh:
        reader = csv.reader(fh)
        for row in reader:
            if len(row) < 2:
                continue
            name, value = row[0], row[1]
            try:
                costs[name] = float(value)
            except ValueError:
                continue
    return costs
