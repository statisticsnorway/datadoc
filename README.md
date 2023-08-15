# Datadoc

![Datadoc Unit tests](https://github.com/statisticsnorway/datadoc/actions/workflows/unit-tests.yml/badge.svg) ![Code coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/mmwinther/0c0c5bdfc360b59254f2c32d65914025/raw/pytest-coverage-badge-datadoc.json) [![PyPI version](https://img.shields.io/pypi/v/ssb-datadoc)](https://pypi.org/project/ssb-datadoc/) ![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

Document datasets in Statistics Norway

## Usage

![DataDoc in use](./doc/change-language-example.gif)

### From Jupyter

1. Open <https://jupyter.dapla-staging.ssb.no> or another Jupyter Lab environment
1. Datadoc comes preinstalled in Statistics Norway environments. Elsewhere, run Run `pip install ssb-datadoc` to install
1. Upload a dataset to your Jupyter server (e.g. <https://github.com/statisticsnorway/datadoc/blob/master/klargjorte_data/befolkning/person_testdata_p2021-12-31_p2021-12-31_v1.parquet>)
1. Run the [demo.ipynb](./demo.ipynb) Notebook
1. Datadoc will open in the notebook

## Contributing

### Prerequisites

- Python >=3.10
- Poetry, install via `curl -sSL https://install.python-poetry.org | python3 -`

### Dependency Management

Poetry is used for dependency management. [Poe the Poet](https://github.com/nat-n/poethepoet) is used for running poe tasks within poetry's virtualenv. Upon cloning this project first install necessary dependencies, then run the tests to verify everything is working.

#### Install all dependencies

```shell
poetry install --all-extras
```

### Add dependencies

#### Main

```shell
poetry add <python package name>
```

#### Dev

```shell
poetry add --group dev <python package name>
```

### Run tests

```shell
poetry run poe test
```

### Run project locally

To run the project locally:

```shell
poetry run poe datadoc
```

### Run project locally in Jupyter

To run the project locally in Jupyter run:

```shell
poetry run poe jupyter
```

A Jupyter instance should open in your browser. Open and run the cells in the `.ipynb` file to demo datadoc.

## Running the Dockerized Application Locally

```bash
docker run -p 8050:8050 \
-v $HOME/.config/gcloud/application_default_credentials.json/:/application_default_credentials.json \
-e GOOGLE_APPLICATION_CREDENTIALS="/application_default_credentials.json" \
datadoc
```

### Bump version

```shell
poetry run poe bump-patch-version
```

> :warning: Run this on the default branch

This command will:

1. Increment version strings in files
1. Commit the changes
1. Tag the commit with the new version

Then just run `git push origin --tags` to push the changes and trigger the release process.
