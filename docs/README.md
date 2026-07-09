## Editing, building, and publishing pymarble documentation


pymarble uses [Sphinx](https://www.sphinx-doc.org/en/master/index.html#) for documentation generation.

### Local testing

```
.venv/bin/python -m pip install -r requirements-devel.txt
```

Then build the documentation locally:

```
.venv/bin/make -C docs html
```

Navigate to `docs/build/` and open `index.html`.

### Remote building and testing

The documentation is built by the GitHub Action `.github/workflows/docbuild.yml` and published by that workflow.
