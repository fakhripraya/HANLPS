# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import pytest
from src.interactor.errors.error_classes \
    import FieldValueNotPermittedException
from src.interactor.errors.error_classes import ItemNotCreatedException

def test_empty_field_exception():
    with pytest.raises(FieldValueNotPermittedException) as exception_info:
        raise FieldValueNotPermittedException("Error", "Content")
    assert str(exception_info.value) == "Error: Content is not permitted"

def test_item_not_created_exception():
    with pytest.raises(ItemNotCreatedException) as exception_info:
        raise ItemNotCreatedException("message content", "message")
    assert str(exception_info.value) == \
        "Message 'message content' was not created correctly"
