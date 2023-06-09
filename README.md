# rfrx

[![Test](https://github.com/nim65s/rfrx/actions/workflows/test.yml/badge.svg)](https://github.com/nim65s/rfrx/actions/workflows/test.yml)
[![Release](https://github.com/nim65s/rfrx/actions/workflows/release.yml/badge.svg)](https://github.com/nim65s/rfrx/actions/workflows/release.yml)
[![PyPI version](https://badge.fury.io/py/rfrx.svg)](https://pypi.org/project/rfrx)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/nim65s/rfrx/main.svg)](https://results.pre-commit.ci/latest/github/nim65s/rfrx/main)
[![codecov](https://codecov.io/gh/nim65s/rfrx/branch/main/graph/badge.svg?token=BLGISGCYKG)](https://codecov.io/gh/nim65s/rfrx)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)

Receive RF frames from some remote controllers.

Available Decoder / Readers:
- SBUS
- Pro-Tronik PTR-6A v2

:warning: Don't forget to invert its electrical signal, eg. with a NAND gate ! :warning:

## Configuration

Could be done in python calls, or by setting the following environment variables:

### SBUS

- `RFRX_PORT`: default to `/dev/ttyS0`
- `RFRX_TIMEOUT`: default to 1
- `RFRX_N_CHANS`: default to 16, number of useful channels for your case
- `RFRX_RUNNING`: default to `ON`, to keep reading and procesing data
- `RFRX_RETRY`: default to `ON`, to close and reopen the port again when something went wrong
- `RFRX_LOG_LEVEL`: default to `WARNING`

### ProTronik

Minimum, Middle and Maximum values read on your Right and Left Horizontal and Vertical joysticks

- `RFRX_RX_MIN`: default to 192
- `RFRX_RX_MID`: default to 992
- `RFRX_RX_MAX`: default to 1796
- `RFRX_RY_MIN`: default to 302
- `RFRX_RY_MID`: default to 1100
- `RFRX_RY_MAX`: default to 1900
- `RFRX_LY_MIN`: default to 180
- `RFRX_LY_MID`: default to 980
- `RFRX_LY_MAX`: default to 1779
- `RFRX_LX_MIN`: default to 192
- `RFRX_LX_MID`: default to 992
- `RFRX_LX_MAX`: default to 1790
