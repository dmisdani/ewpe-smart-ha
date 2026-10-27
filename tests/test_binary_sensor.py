"""Tests for the dehumidifier tank-full binary sensor."""

from unittest.mock import MagicMock

import pytest

from custom_components.ewpe_smart.binary_sensor import (
    EwpeBinarySensor,
    supported_binary_sensor_descriptions,
)
from custom_components.ewpe_smart.params_catalog import diagnostic_params
from custom_components.ewpe_smart.sensor import supported_extra_sensor_descriptions


@pytest.mark.parametrize("value,expected", [(0, False), (1, True), (None, None)])
def test_tank_full_state(value, expected):
    coordinator = MagicMock()
    coordinator.data = {"DwatFul": value}
    coordinator.device.mac = "AA:BB:CC:DD:EE:FF"
    coordinator.device.info = {}
    description = next(
        d for d in supported_binary_sensor_descriptions(coordinator.data)
        if d.param == "DwatFul"
    )
    sensor = EwpeBinarySensor(coordinator, description)
    assert sensor.is_on is expected
    assert sensor.device_class == "problem"
    assert sensor.entity_registry_enabled_default
    assert sensor.entity_category is None
    assert "DwatFul" not in {
        d.param for d in supported_extra_sensor_descriptions(coordinator.data)
    }
    assert "DwatFul" not in diagnostic_params(coordinator.data)


def test_tank_full_hidden_when_missing():
    assert "DwatFul" not in {
        d.param for d in supported_binary_sensor_descriptions({})
    }
