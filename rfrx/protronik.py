"""Process protronik data."""

from logging import getLogger
from os import environ

from .sbus import SbusDecoder, SbusReader

LOGGER = getLogger("rfrx.protronik")

RX_MIN, RX_MID, RX_MAX = (
    int(environ.get("RFRX_RX_MIN", 192)),
    int(environ.get("RFRX_RX_MID", 992)),
    int(environ.get("RFRX_RX_MAX", 1796)),
)
RY_MIN, RY_MID, RY_MAX = (
    int(environ.get("RFRX_RY_MIN", 302)),
    int(environ.get("RFRX_RY_MID", 1100)),
    int(environ.get("RFRX_RY_MAX", 1900)),
)
LY_MIN, LY_MID, LY_MAX = (
    int(environ.get("RFRX_LY_MIN", 180)),
    int(environ.get("RFRX_LY_MID", 980)),
    int(environ.get("RFRX_LY_MAX", 1779)),
)
LX_MIN, LX_MID, LX_MAX = (
    int(environ.get("RFRX_LX_MIN", 192)),
    int(environ.get("RFRX_LX_MID", 992)),
    int(environ.get("RFRX_LX_MAX", 1790)),
)


class ProTronikDecoder(SbusDecoder):
    """Decode S-BUS frames from Pro-Tronik PTR-6A v2."""

    def __init__(self, frame):
        """Decode SBUS, then parse it according to Pro-Tronik use."""
        super().__init__(frame, n_chans=6)

        # calibration: minimum, middle, maximum, name
        rx = RX_MIN, RX_MID, RX_MAX, "right horizontal"
        ry = RY_MIN, RY_MID, RY_MAX, "right vertical"
        ly = LY_MIN, LY_MID, LY_MAX, "left vertical"
        lx = LX_MIN, LX_MID, LX_MAX, "left horizontal"

        def scale(val, mini, middle, maxi, name):
            """Convert read value to -1.0 -> 1.0."""
            if val < mini:
                LOGGER.debug(f"{name} value lower than min: {val} < {mini}")
                return -1.0
            if val > maxi:
                LOGGER.debug(f"{name} value higher than max: {val} > {maxi}")
                return 1.0
            if val < middle:
                return (val - mini) / (middle - mini) - 1.0
            return (val - middle) / (maxi - middle)

        self.rx = +scale(self.chans[0], *rx)
        self.ry = -scale(self.chans[1], *ry)
        self.ly = -scale(self.chans[2], *ly)
        self.lx = +scale(self.chans[3], *lx)

        self.ch5 = 2 if self.chans[4] < 500 else 1 if self.chans[4] < 1500 else 0
        self.ch6 = 0 if self.chans[5] < 1000 else 1

    def __str__(self):
        """Show decoded data."""
        return (
            f"{self.rx:+.3f} {self.ry:+.3f} {self.ly:+.3f} {self.lx:+.3f} "
            f"{self.ch5} {self.ch6}"
        )


class ProTronikReader(SbusReader):
    """Bind to a serial port, read SBUS pro-tronik frames and process them."""

    decoder = ProTronikDecoder
