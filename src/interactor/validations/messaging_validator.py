""" Defines the validator for the messaging input data.
"""

from src.interactor.validations.base_input_validator import BaseInputValidator

class MessagingInputDtoValidator(BaseInputValidator):
    """ Validates the messaging input data.
    :param input_data: The input data to be validated.
    """

    def __init__(self, input_data: dict) -> None:
        super().__init__(input_data)
        self.input_data = input_data
        self.__schema = {
            "sessionId": {
                "type": "string",
                "required": True,
                "empty": False
            },
            "content": {
                "type": "string",
                "required": True,
                "empty": False
            },
        }

    def validate(self) -> None:
        """ Validates the input data
        """
        # Verify the input data using BaseInputValidator method
        super().verify(self.__schema)
