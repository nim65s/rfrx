"""Process protronik data."""

from logging import getLogger
from os import environ

from .sbus import SbusDecoder, SbusReader

LOGGER = getLogger("protronik.protronik")

RH_MIN, RH_MID, RH_MAX = (
    int(environ.get("RH_MIN", 192)),
    int(environ.get("RH_MID", 992)),
    int(environ.get("RH_MAX", 1796)),
)
RV_MIN, RV_MID, RV_MAX = (
    int(environ.get("RV_MIN", 302)),
    int(environ.get("RV_MID", 1100)),
    int(environ.get("RV_MAX", 1900)),
)
LV_MIN, LV_MID, LV_MAX = (
    int(environ.get("LV_MIN", 180)),
    int(environ.get("LV_MID", 980)),
    int(environ.get("LV_MAX", 1779)),
)
LH_MIN, LH_MID, LH_MAX = (
    int(environ.get("LH_MIN", 192)),
    int(environ.get("LH_MID", 992)),
    int(environ.get("LH_MAX", 1790)),
)


class ProTronikDecoder(SbusDecoder):
    """Decode S-BUS frames from Pro-Tronik PTR-6A v2."""

    def __init__(self, frame):
        """Decode SBUS, then parse it according to Pro-Tronik use."""
        super().__init__(frame, n_chans=6)

        # calibration: position, mini, middle, maxi
        rh = RH_MIN, RH_MID, RH_MAX, "right horizontal"
        rv = RV_MIN, RV_MID, RV_MAX, "right vertical"
        lv = LV_MIN, LV_MID, LV_MAX, "left vertical"
        lh = LH_MIN, LH_MID, LH_MAX, "left horizontal"

        def scale(val, mini, middle, maxi, pos):
            """Convert read value to -1.0 -> 1.0."""
            if val < mini:
                LOGGER.debug(f"{pos} value lower than min: {val} < {mini}")
                return -1.0
            if val > maxi:
                LOGGER.debug(f"{pos} value higher than max: {val} > {maxi}")
                return 1.0
            if val < middle:
                return (val - mini) / (middle - mini) - 1.0
            return (val - middle) / (maxi - middle)

        self.rh = +scale(self.chans[0], *rh)
        self.rv = -scale(self.chans[1], *rv)
        self.lv = -scale(self.chans[2], *lv)
        self.lh = +scale(self.chans[3], *lh)

        self.ch5 = 2 if self.chans[4] < 500 else 1 if self.chans[4] < 1500 else 0
        self.ch6 = 0 if self.chans[5] < 1000 else 1

    def __str__(self):
        """Show decoded data."""
        return (
            f"{self.rh:+.3f} {self.rv:+.3f} {self.lv:+.3f} {self.lh:+.3f} "
            f"{self.ch5} {self.ch6}"
        )


class ProTronikReader(SbusReader):
    """Bind to a serial port, read SBUS frames and process them."""

    decoder_class = ProTronikDecoder
