# optional-dependencies-all pre-commit hook

A pre-commit hook to updates the `project.optional-dependencies.all` in a `pyproject.toml` file.

The following code is inconsistent because `pip install mypackage[all]` will not install `requests`.
This pre-commit hook will make sure that `all` list all the dependencies listed in other entries.
You can also exclude some entries (typically `docs` or `dev`) with the `--exclude-keys` option.

```toml

[project]

dependencies = [
  "tqdm"
]

optional-dependencies.web = [
  "requests",
]

optional-dependencies.all = [
  "tqdm",
]
```

becomes:

```toml

[project]

dependencies = [
  "tqdm"
]

optional-dependencies.web = [
  "requests",
]

optional-dependencies.all = [
  "tqdm",
  "requests",
]
```

Usage:

```yaml
- repo: https://github.com/b8raoult/optional-dependencies-all
  rev: "0.0.1"
  hooks:
  - id: optional-dependencies-all
    args: ["--inplace", "--all-key", "all", "--ignore-keys", "dev,docs"]
```
