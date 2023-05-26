"""Test sbus decoder."""
from unittest import TestCase

from rfrx.sbus import SbusDecoder


class TestSbus(TestCase):
    """Test sbus decoder."""

    def test_frame(self):
        """Test sbus decoder."""
        frame = (
            b'\x0f\xe0c"\xf1\xc0\x07>\x7f\x83\x0f|\x00\x00'
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        )
        sbus = SbusDecoder(frame)
        self.assertFalse(sbus.ch17)
        self.assertFalse(sbus.ch18)
        self.assertFalse(sbus.ch18)
        self.assertEqual(sbus.chans[0], 992)

        frame = (
            b"\x0fCb\xe2\xf0\xc0\x07\x0c\x80\x83\x0f|\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        )

        sbus = SbusDecoder(frame)
        self.assertFalse(sbus.ch17)
        self.assertFalse(sbus.ch18)
        self.assertFalse(sbus.ch18)
        self.assertEqual(sbus.chans[0], 579)
