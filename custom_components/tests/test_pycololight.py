import pytest

from cololight.light import PyCololight

from unittest.mock import patch, call


class TestPyCololight:
    @patch("cololight.light.PyCololight._send")
    def test_setting_brightness(self, mock_sending):
        light = PyCololight("1.1.1.1")
        assert light.brightness == None

        light.brightness = 60

        mock_sending.assert_called_with(
            b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xcf<"
        )

        assert light.brightness == 60

    @patch("cololight.light.PyCololight._send")
    def test_setting_colour(self, mock_sending):
        light = PyCololight("1.1.1.1")
        assert light.colour == None

        light.colour = (255, 127, 255)

        mock_sending.assert_called_with(
            b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x00\xff\x7f\xff"
        )

        assert light.colour == (255, 127, 255)

    @patch("cololight.light.PyCololight._send")
    def test_setting_effect(self, mock_sending):
        light = PyCololight("1.1.1.1")
        assert light.effect == None

        light.effect = "Sunrise"

        mock_sending.assert_called_with(
            b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x01\xc1\n\x00"
        )
        assert light.effect == "Sunrise"

    def test_effects_returns_list_of_effects(self):
        light = PyCololight("1.1.1.1")
        supported_efects = [
            "80s Club",
            "Cherry Blossom",
            "Cocktail Parade",
            "Instagrammer",
            "Pensieve",
            "Savasana",
            "Sunrise",
            "The Circus",
            "Unicorns",
            "Christmas",
            "Rainbow Flow",
            "Music Mode",
        ]

        assert light.effects == supported_efects
