"""Dehumidifier humidity conversion and independent controls."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.ewpe_smart.number import EwpeTargetHumidityNumber
from custom_components.ewpe_smart.select import supported_select_descriptions
from custom_components.ewpe_smart.sensor import (
    EwpeExtraSensor,
    supported_extra_sensor_descriptions,
)
from custom_components.ewpe_smart.switch import supported_switch_descriptions


def coordinator(data):
    result = MagicMock()
    result.data = data
    result.device.mac = "AA:BB:CC:DD:EE:FF"
    result.device.info = {}
    result.device.set_state = AsyncMock()
    result.async_request_refresh = AsyncMock()
    return result


@pytest.mark.parametrize("code,humidity", [(3, 30), (4, 35), (13, 80), (0, None), (14, None)])
async def test_target_humidity_conversion(code, humidity):
    coord = coordinator({"Dwet": code, "DwatSen": 56})
    entity = EwpeTargetHumidityNumber(coord)
    assert entity.native_value == humidity
    if humidity is not None:
        await entity.async_set_native_value(humidity)
        coord.device.set_state.assert_awaited_once_with({"Dwet": code})
        coord.async_request_refresh.assert_awaited_once()


@pytest.mark.parametrize("value", [29, 81, 32])
async def test_invalid_target_does_not_write(value):
    coord = coordinator({})
    with pytest.raises(ValueError):
        await EwpeTargetHumidityNumber(coord).async_set_native_value(value)
    coord.device.set_state.assert_not_awaited()


def test_dehumidifier_sensor_and_controls():
    data = {"Dwet": 4, "DwatSen": 56, "Pow": 1, "WdSpd": 1}
    descriptions = supported_extra_sensor_descriptions(data)
    assert "Dwet" not in {d.param for d in descriptions}
    description = next(d for d in descriptions if d.param == "DwatSen")
    sensor = EwpeExtraSensor(coordinator(data), description)
    assert sensor.native_value == 56
    assert sensor.device_class == "humidity"
    assert sensor.native_unit_of_measurement == "%"
    assert sensor.entity_category is None
    assert sensor.entity_registry_enabled_default
    assert "Pow" in {d.param for d in supported_switch_descriptions(data)}
    assert "WdSpd" in {d.param for d in supported_select_descriptions(data)}


def test_ac_does_not_get_dehumidifier_controls():
    data = {"Pow": 1, "WdSpd": 1, "DwatSen": 0}
    assert "Pow" not in {d.param for d in supported_switch_descriptions(data)}
    assert "WdSpd" not in {d.param for d in supported_select_descriptions(data)}
    desc = next(d for d in supported_extra_sensor_descriptions(data) if d.param == "DwatSen")
    assert desc.entity_category == "diagnostic"
