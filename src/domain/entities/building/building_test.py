# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from .building import Building

def test_building_creation(fixture_building_developer):
    building = Building(
        building_title=fixture_building_developer["building_title"],
        building_address=fixture_building_developer["building_address"],
    )
    assert building.building_address == fixture_building_developer["building_address"]

def test_building_from_dict(fixture_building_developer):
    building = Building.from_dict(fixture_building_developer)
    assert building.building_address == fixture_building_developer["building_address"]

def test_building_to_dict(fixture_building_developer):
    building = Building.from_dict(fixture_building_developer)
    assert building.to_dict() == fixture_building_developer

def test_building_comparison(fixture_building_developer):
    building_1 = Building.from_dict(fixture_building_developer)
    building_2 = Building.from_dict(fixture_building_developer)
    assert building_1 == building_2
