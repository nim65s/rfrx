"""Process SBUS data."""
from logging import basicConfig, getLogger, root
from os import environ
from time import sleep

import serial

LOGGER = getLogger("rfrx.sbus")

_FALSY = ("0", "NO", "OFF", "FALSE")
PORT = environ.get("RFRX_PORT", "/dev/ttyS0")
RUNNING = environ.get("RFRX_RUNNING", "ON") not in _FALSY
RETRY = environ.get("RFRX_RETRY", "ON") not in _FALSY
TIMEOUT = int(environ.get("RFRX_TIMEOUT", 1))
N_CHANS = int(environ.get("RFRX_N_CHANS", 16))
LOG_LEVEL = environ.get("RFRX_LOG_LEVEL", "WARNING").upper()


class SbusError(Exception):
    """Exception class for SbusDecoder."""

    pass


class SbusDecoder:
    """Decode SBUS frames."""

    def __init__(self, frame, n_chans=N_CHANS):
        """Parse a frame with `n_chans` used channels."""
        LOGGER.info("parsing frame")
        self.frame = frame
        self.val = int.from_bytes(frame, byteorder="little")
        if not (0 <= n_chans <= 16):
            err = (
                "Wrong number of channels. "
                f"Expected 0 <= n_chans <= 16, got {n_chans}."
            )
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

    def __str__(self):
        """Show decoded data."""
        data = [*self.chans, self.failsafe, self.frame_lost, self.ch18, self.ch17]
        return " ".join(f"{c:4}" for c in data)


class SbusReader:
    """Bind to a serial port, read SBUS frames and process them."""

    decoder = SbusDecoder

    def __init__(self, port=PORT, running=RUNNING, retry=RETRY, timeout=TIMEOUT):
        """Configure the serial port parameters."""
        if len(root.handlers) == 0:
            basicConfig(level=LOG_LEVEL)
        self.port = port
        self.running = running
        self.retry = retry
        self.timeout = timeout

        self.run()

    def run(self):
        """Run main loop."""
        while self.running and self.retry:
            with serial.Serial(
                port=self.port,
                baudrate=100_000,
                bytesize=serial.EIGHTBITS,
                # TODO: broken on raspbian buster & pyserial 3.5
                # works well on same setup but with pyserial 3.4…
                # parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_TWO,
                timeout=self.timeout,
            ) as ser:
                while self.running:
                    try:
                        data = ser.read(25)
                        if len(data) == 0:
                            err = (
                                f"no data on {self.port} "
                                f"in the last {self.timeout} seconds."
                            )
                            LOGGER.warning(err)
                        else:
                            frame = self.decoder(data)
                            self.process(frame)
                    except SbusError as e:
                        LOGGER.error(f"SBUS error: {e}")
                        break
            LOGGER.warning("sleeping a bit.")
            sleep(1)

    def process(self, frame):
        """Override this for your application."""
        print(frame, frame.chans)
