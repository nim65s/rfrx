"""Test pro-tronik decoder."""
from unittest import TestCase

from rfrx.protronik import ProTronikDecoder


class TestProTronik(TestCase):
    """Test pro-tronik decoder."""

    def test_frame(self):
        """Test pro-tronik decoder."""
        frame = (
            b'\x0f\xe0c"\xf1\xc0\x07>\x7f\x83\x0f|\x00\x00'
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        )
        sbus = ProTronikDecoder(frame)
        self.assertEqual(sbus.rx, 0.0)
        self.assertEqual(sbus.ch5, 1)

        frame = (
            b"\x0fCb\xe2\xf0\xc0\x07\x0c\x80\x83\x0f|\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        )

        sbus = ProTronikDecoder(frame)
        self.assertEqual(sbus.rx, -0.51625)
        self.assertEqual(sbus.ch5, 2)
