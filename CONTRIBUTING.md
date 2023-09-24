## Setup

1. install [poetry](https://python-poetry.org/docs/)
2. run `poetry install`
3. run `poetry run pre-commit install`

Should be all that is needed to bootstrap a development setup. To save time, black and flake8 are the only things run from the pre-commit hook. It is recommended to NOT skip #3 above. A github action will reject any PRs that have lint or format fails. Black and flake8 are both set up to fix any errors they can before the code is committed to a PR branch and pushed.

## Running tests

Run automatically by Github action CI/CD

`poetry run pytest tests/`

## Running lint

Run automatically by commit-hook and CI/CD.

`poetry run flake8`

## Running formatters

Run automatically by commit-hook and CI/CD.

`poetry run black .`
