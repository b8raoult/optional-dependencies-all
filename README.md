# optional-dependencies-all pre-commit hook

A pre-commit hook to updates the `project.optional-dependencies.all` in a `pyproject.toml` file.

The following code is inconsistent because `pip install mypackage[all]` will not install `requests`.
This pre-commit hook will make sure that `all` list all the dependencies listed in other entries.
You can also exclude some entries (typically `docs` or `dev`) with the `--exclude-keys` option.

You can defines also define groups like `--group dev=docs,tests` that will combine the dependencies of `docs` and `tests` into `dev`. You can provide several groups.

```toml

[project]

dependencies = [
  "tqdm"
]

optional-dependencies.web = [
  "requests",
]

optional-dependencies.database = [
  "sqlalchemy",
]

optional-dependencies.all = [
]
```

becomes:

```toml

[project]

dependencies = [
  "tqdm"
]

optional-dependencies.database = [
  "sqlalchemy",
]

optional-dependencies.all = [
  "requests",
  "sqlalchemy",
]
```

Usage:

```yaml
- repo: https://github.com/b8raoult/optional-dependencies-all
  rev: "0.0.4"
  hooks:
  - id: optional-dependencies-all
    args: ["--inplace", "--exclude-keys=dev,docs,tests", "--group=dev=docs,tests"]
```
