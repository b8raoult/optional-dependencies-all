import argparse
import re
import sys

import toml


def fix(path, inplace=False, all_key="all", exclude_keys=None, indent=2):
    with open(path) as file:
        text = file.read()

    toml_dict = toml.loads(text)

    project = toml_dict.get("project", {})
    dependencies = project.get("dependencies", [])
    optional_dependencies = project.get("optional-dependencies", {})

    all_key = "all"
    exclude_keys = ["dev", "docs"]
    all_dependencies = set(dependencies)

    if all_key not in optional_dependencies:
        return

    for key in optional_dependencies:
        if key == all_key:
            continue
        if key in exclude_keys:
            continue
        all_dependencies.update(optional_dependencies[key])

    if all_key in optional_dependencies:
        optional_dependencies[all_key] = sorted(all_dependencies)

    if inplace:
        out = open(path, "w")
    else:
        out = sys.stdout

    indent = " " * indent

    lines = iter(text.splitlines())
    for line in lines:
        m = re.match(rf"^optional-dependencies.{all_key}\s*=\s*\[", line)
        if m:
            print(f"optional-dependencies.{all_key} = [", file=out)
            for p in optional_dependencies.get(all_key, []):
                print(f'{indent}"{p}",', file=out)
            print("]", file=out)
            while not line.strip().endswith("]"):
                line = next(lines)
        else:
            print(line, file=out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inplace", action="store_true", help="Modify the files in place."
    )
    parser.add_argument(
        "--all-key", default="all", help="The key to use for the `all` dependencies."
    )
    parser.add_argument("--exclude-keys", help="The keys to exclude.")
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="The number of spaces to use for indentation.",
    )
    parser.add_argument("files", nargs="+", help="The files to convert.")
    args = parser.parse_args()

    for path in args.files:
        fix(
            path,
            inplace=args.inplace,
            all_key=args.all_key,
            exclude_keys=args.exclude_keys,
            indent=args.indent,
        )


if __name__ == "__main__":
    main()
