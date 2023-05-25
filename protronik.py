#!/usr/bin/env python3
"""Decode SBUS frames from a Pro-Tronik PTR-6A v2 remote controller.

Don't forget to invert its electrical signal, eg. with a NAND gate !
"""

from logging import getLogger
from os import environ
from time import sleep

import serial

LOGGER = getLogger("protronik")


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


class SbusError(Exception):
    """Exception class for SbusDecoder."""

    pass


class SbusDecoder:
    """Decode SBUS frames."""

    def __init__(self, frame, n_chans=16):
        """Parse a frame with `n_chans` used channels."""
        LOGGER.info("parsing frame")
        self.frame = frame
        self.val = int.from_bytes(frame, byteorder="little")
        if not (0 <= n_chans <= 16):
            err = "Wrong number of channels. "
            err += f"Expected 0 <= n_chans <= 16, got {n_chans}."
            raise ValueError(err)
        self.n_chans = n_chans
        self.chans = [None] * n_chans
        self.failsafe = None
        self.frame_lost = None
        self.ch17 = None
        self.ch18 = None

        self.check()
        LOGGER.debug(f"0x{self.val:025x}")
        self.parse()
        LOGGER.debug("chans: %s" % self.chans)
        LOGGER.debug("failsafe: %s" % self.failsafe)
        LOGGER.debug("frame lost: %s" % self.frame_lost)
        LOGGER.debug("ch 18: %s" % self.ch18)
        LOGGER.debug("ch 17: %s" % self.ch17)

    def check(self):
        """Check if the frame is in correct format."""
        if len(self.frame) != 25:
            err = f"Wrong frame length. Expected 25, got {len(self.frame)}."
            raise SbusError(err)
        if self.frame[0] != 0x0F:
            err = f"Wrong header. Expected 0x0F, got {self.frame[0]}."
            raise SbusError(err)
        if self.frame[24] != 0x00:
            err = f"Wrong end byte. Expected 0x00, got {self.frame[24]}."
            raise SbusError(err)

    def parse(self):
        """Decode `n_chans` channels and 4 bits in Byte 23."""
        data = self.val >> 8  # ignore header
        for chan in range(self.n_chans):
            self.chans[chan] = data & 0b11111111111
            data >>= 11

        self.failsafe = self.frame[23] & 0x10
        self.frame_lost = self.frame[23] & 0x20
        self.ch18 = self.frame[23] & 0x40
        self.ch17 = self.frame[23] & 0x80


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


class ProTronik:
    """Bind to a serial port, read SBUS frames and process them."""

    def __init__(self, port="/dev/ttyS0", retry=True, timeout=1):
        """Configure the serial port parameters."""
        self.port = port
        self.retry = retry
        self.timeout = timeout

    def run(self):
        """Run main loop."""
        while self.retry:
            with serial.Serial(
                port=self.port,
                baudrate=100_000,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_TWO,
                timeout=self.timeout,
            ) as ser:
                while True:
                    try:
                        data = ser.read(25)
                        if len(data) == 0:
                            err = f"no data on {self.port} "
                            err += f"in the last {self.timeout} seconds."
                            LOGGER.warning(err)
                        else:
                            frame = ProTronikDecoder(data)
                            self.process(frame)
                    except SbusError as e:
                        LOGGER.error(f"SBUS error: {e}")
                        break
            LOGGER.warning("sleeping a bit.")
            sleep(1)

    def process(self, frame):
        """Override this for your application."""
        print(frame, frame.chans)


if __name__ == "__main__":
    ProTronik().run()
