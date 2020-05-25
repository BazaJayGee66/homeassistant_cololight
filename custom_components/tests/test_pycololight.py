import pytest

from cololight.light import (
    PyCololight,
    ColourException,
    ColourSchemeException,
    ModeExecption,
    CycleSpeedException,
)

from unittest.mock import patch, call


class TestPyCololight:
    @patch("cololight.light.PyCololight._send")
    def test_turn_on(self, mock_send):
        light = PyCololight("1.1.1.1")
        assert light.on == False

        light.on = 60

        mock_send.assert_called_with(
            b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xcf<"
        )

        assert light.on == True
        assert light.brightness == 60

    @patch("cololight.light.PyCololight._send")
    def test_setting_brightness(self, mock_send):
        light = PyCololight("1.1.1.1")

        light.brightness = 60

        mock_send.assert_called_with(
            b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xcf<"
        )

        assert light.brightness == 60

    @patch("cololight.light.PyCololight._send")
    def test_setting_colour(self, mock_send):
        light = PyCololight("1.1.1.1")
        assert light.colour == None

        light.colour = (255, 127, 255)

        mock_send.assert_called_with(
            b"SZ00\x00\x00\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x06\x02\xff\x00\xff\x7f\xff"
        )

        assert light.colour == (255, 127, 255)

    @patch("cololight.light.PyCololight._send")
    def test_setting_effect(self, mock_send):
        light = PyCololight("1.1.1.1")
        assert light.effect == None

        light.effect = "Sunrise"

        mock_send.assert_called_with(
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

    @patch("cololight.light.PyCololight._send")
    def test_turn_off(self, mock_send):
        light = PyCololight("1.1.1.1")
        light._on = True

        light.on = 0
        mock_send.assert_called_with(
            b"SZ00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x01\x03\x01\xce\x1e"
        )

        assert light.on == False

    def test_cycle_speed_hex_returns_hex_value(self):
        light = PyCololight("1.1.1.1")

        expected_responses = ["01", "20", "0d", "0b"]

        test_cycle_speeds = [(32, 1), (1, 1), (20, 1), (2, 2)]

        for index, test_speed in enumerate(test_cycle_speeds):
            cycle_speed = test_speed[0]
            mode = test_speed[1]
            cycle_speed_hex = light._cycle_speed_hex(cycle_speed, mode)
            assert cycle_speed_hex == expected_responses[index]

    def test_colour_hex_returns_hex_value(self):
        light = PyCololight("1.1.1.1")

        expected_responses = ["80", "06", "a6", "b4", "bf", "c1", "c3"]

        test_colours = [
            ["Breath", "Red, Green, Blue", 1],
            ["Breath", "Red", 13],
            ["Flicker", "Azure", 1],
            ["Mood", "Orange", 1],
            ["Selected", "Savasana", 1],
            ["Selected", "Sunrise", 1],
            ["Selected", "Unicorns", 1],
        ]

        for index, colour in enumerate(test_colours):
            colour_hex = light._colour_hex(colour[0], colour[1], colour[2])
            assert colour_hex == expected_responses[index]

    def test_mode_hex_returns_tuple_of_hex_values(self):
        light = PyCololight("1.1.1.1")

        expected_responses = [("05", "10"), ("05", "80"), ("06", "10"), ("06", "70")]

        test_modes = [3, 8, 17, 26]

        for index, mode in enumerate(test_modes):
            mode_hex = light._mode_hex(mode)
            assert mode_hex == expected_responses[index]

    def test_add_custom_effect_adds_effect(self):
        light = PyCololight("1.1.1.1")

        effect_name = "test_effect"
        effect_colour_schema = "Mood"
        effect_colour = "Orange"
        effect_cycle_speed = 11
        effect_mood = 1

        light.add_custom_effect(
            effect_name,
            effect_colour_schema,
            effect_colour,
            effect_cycle_speed,
            effect_mood,
        )

        assert effect_name in light.effects
        assert light._effects[effect_name] == "01b41600"

    def test_add_custom_effect_adds_effect_when_mode_is_2(self):
        light = PyCololight("1.1.1.1")

        effect_name = "test_effect"
        effect_colour_schema = "Mood"
        effect_colour = "Orange"
        effect_cycle_speed = 3
        effect_mood = 2

        light.add_custom_effect(
            effect_name,
            effect_colour_schema,
            effect_colour,
            effect_cycle_speed,
            effect_mood,
        )

        assert effect_name in light.effects
        assert light._effects[effect_name] == "0213b400"

    def test_custom_effect_colour_schemes_returns_supported_colour_schemes(self):
        light = PyCololight("1.1.1.1")

        supported_colour_schemes = [
            "Breath",
            "Shadow",
            "Flash",
            "Flicker",
            "Scene",
            "Mood",
            "Selected",
        ]

        assert light.custom_effect_colour_schemes() == supported_colour_schemes

    def test_custom_effect_colour_scheme_colours_returns_colour_scheme_colours(self):
        light = PyCololight("1.1.1.1")

        expected_colours = [
            "Red, Green, Blue",
            "Rainbow",
            "Green",
            "Azure",
            "Blue",
            "Purple",
            "Red",
            "Orange",
            "Yellow",
            "White",
        ]

        assert light.custom_effect_colour_scheme_colours("Flicker") == expected_colours

    def test_colour_hex_raises_exeception_when_bad_scheme(self):
        light = PyCololight("1.1.1.1")

        with pytest.raises(ColourSchemeException):
            light._colour_hex("bad_scheme", "colour", 1)

    def test_colour_hex_raises_exeception_when_bad_colour(self):
        light = PyCololight("1.1.1.1")

        with pytest.raises(ColourException):
            light._colour_hex("Mood", "bad_colour", 1)

    def test_cycle_speed_hex_raises_exeception_when_bad_speed(self):
        light = PyCololight("1.1.1.1")

        with pytest.raises(CycleSpeedException):
            light._cycle_speed_hex(35, 1)

    def test_mode_hex_raises_exeception_when_bad_mode(self):
        light = PyCololight("1.1.1.1")

        with pytest.raises(ModeExecption):
            light._mode_hex(0)
