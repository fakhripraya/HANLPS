# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from .action import Action


def test_action_creation(fixture_action_data):
    action = Action(action=fixture_action_data["action"])
    assert action.action == fixture_action_data["action"]


def test_action_from_dict(fixture_action_data):
    action = Action.from_dict(fixture_action_data)
    assert action.action == fixture_action_data["action"]


def test_action_to_dict(fixture_action_data):
    action = Action.from_dict(fixture_action_data)
    assert action.to_dict() == fixture_action_data


def test_action_comparison(fixture_action_data):
    action_1 = Action.from_dict(fixture_action_data)
    action_2 = Action.from_dict(fixture_action_data)
    assert action_1 == action_2
