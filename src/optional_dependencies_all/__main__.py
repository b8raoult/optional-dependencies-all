import argparse
import json
import re
import sys
from logging import warning

import toml


def build_group(group, optional_dependencies, exclude_keys=None, include_keys=None):
    dependencies = set()

    for key, values in optional_dependencies.items():
        if exclude_keys is not None and key in exclude_keys:
            continue
        if include_keys is not None and key not in include_keys:
            continue
        dependencies.update(values)

    return sorted(dependencies)


def fix(path, inplace=False, all_key="all", exclude_keys=None, indent=2, groups=None):
    with open(path) as file:
        text = file.read()

    toml_dict = toml.loads(text)

    project = toml_dict.get("project", {})
    optional_dependencies = project.get("optional-dependencies", {})

    exclude_keys = [] if exclude_keys is None else exclude_keys.split(",")
    new_optional_dependencies = {}

    optional_dependencies.pop(all_key, None)
    for group in groups:
        optional_dependencies.pop(group.split("=")[0], None)

    previous_dependencies = optional_dependencies.copy()

    for _ in range(10):

        new_optional_dependencies = {}

        new_optional_dependencies[all_key] = build_group(
            all_key,
            optional_dependencies,
            exclude_keys=exclude_keys,
        )

        for group in groups:
            group_name, group_keys = group.split("=")
            group_dependencies = build_group(
                group_name, optional_dependencies, include_keys=group_keys.split(",")
            )
            new_optional_dependencies[group_name] = group_dependencies

        optional_dependencies.update(new_optional_dependencies)
        if previous_dependencies == optional_dependencies:
            break

        previous_dependencies = optional_dependencies.copy()

    if previous_dependencies != optional_dependencies:
        warning(f"Couln't converge on a solution for {path}")
        exit(1)

    if inplace:
        out = open(path, "w")
    else:
        out = sys.stdout

    indent = " " * indent

    lines = iter(text.splitlines())
    done = set()
    in_project = False

    def flush():
        for key, values in optional_dependencies.items():
            if key in done:
                continue
            print(f"optional-dependencies.{key} = [", file=out)
            for p in values:
                print(f'{indent}"{p}",', file=out)
            print("]", file=out)
            print("", file=out)
            done.add(key)

    for line in lines:

        if in_project and line.startswith("["):
            flush()
            in_project = False

        if line.startswith("[project]"):
            in_project = True

        found = False
        for key, values in optional_dependencies.items():
            m = re.match(rf"^optional-dependencies.{key}\s*=\s*\[", line)
            if m:
                print(f"optional-dependencies.{key} = [", file=out)
                for p in values:
                    print(f'{indent}"{p}",', file=out)
                print("]", file=out)
                while not line.strip().endswith("]"):
                    line = next(lines)
                found = True
                done.add(key)
                break

        if not found:
            print(line, file=out)

    if in_project and not done:
        flush()

    if not done:
        warning(f"Couldn't finalise optional-dependencies in {path}")
        exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inplace", action="store_true", help="Modify the files in place."
    )
    parser.add_argument(
        "--all-key", default="all", help="The key to use for the `all` dependencies."
    )
    parser.add_argument("--exclude-keys", help="The keys to exclude from `all`.")

    parser.add_argument(
        "--group",
        nargs="*",
        help="A group to build from other groups --group dev=tests/docs.",
    )

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
            groups=args.group,
        )


if __name__ == "__main__":
    main()
