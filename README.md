# rfrx

[![Release](https://github.com/nim65s/rfrx/actions/workflows/release.yml/badge.svg)](https://github.com/nim65s/rfrx/actions/workflows/release.yml)
[![PyPI version](https://badge.fury.io/py/rfrx.svg)](https://pypi.org/project/rfrx)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/nim65s/rfrx/master.svg)](https://results.pre-commit.ci/latest/github/nim65s/rfrx/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

Receive RF frames from some remote controllers.

Available Decoder / Readers:
- SBUS
- Pro-Tronik PTR-6A v2

:warning: Don't forget to invert its electrical signal, eg. with a NAND gate ! :warning:
