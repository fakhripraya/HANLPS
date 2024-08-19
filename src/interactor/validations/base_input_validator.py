""" This module provides the base class BaseInputValidator for input validation
"""

from cerberus import Validator

class BaseInputValidator:
    """ This class provides the base class for input validation
    """
    def __init__(self, data: dict[str, str]):
        self.data = data
        self.errors: dict = {}

    def verify(self, schema: dict) -> None:
        """ Validates the input data against the provided schema
        :param schema: The schema to validate against
        :return: None
        :raises ValueError: If the input data is invalid.
        """
        validator = Validator(schema)
        if not validator.validate(self.data):
            self.errors = validator.errors
            self._raise_validation_error()

    def _raise_validation_error(self):
        error_messages = []
        for field, messages in self.errors.items():
            for message in messages:
                error_messages.append(f"{field.capitalize()}: {message}")
        raise ValueError("\n".join(error_messages))
