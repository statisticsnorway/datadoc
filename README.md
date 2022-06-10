# datadoc-prototype

## Usage example

Data Documentation (DataDoc) Prototyp for Jupyter
![DataDoc](./doc/DataDoc_prototype_001.png)

## Contributing

### Dependency Management

Poetry is used for dependency management.

To install all required dependencies in a virtual environment run `poetry install`. To add a new dependency to the project run `poetry add <package name>`.

### Run project locally in Jupyter

To run the project locally in Jupyter run:

```bash
poetry shell
ipython kernel install --user --name="datadoc"
jupyter notebook
```

A Jupyter instance should open in your browser. Once there, open the `*.ipynb` file. Before running it, select the correct interpreter via `Kernel > Change Kernel > datadoc`.

### Run tests

1. Install dev dependencies (see [Dependency Management](#dependency-management))
1. Run `poetry shell` to open a shell in the Virtual Environment for the project
1. Run `pytest` in the root of the project
