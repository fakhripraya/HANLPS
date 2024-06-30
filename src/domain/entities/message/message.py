""" This module has definition of the Building entity
"""


from dataclasses import dataclass, asdict
from src.domain.value_objects import MessageId

@dataclass
class Message:
    """ Definition of the Message entity
    """
    message_id: MessageId
    content: str

    @classmethod
    def from_dict(cls, data):
        """ Convert data from a dictionary
        """
        return cls(**data)

    def to_dict(self):
        """ Convert data into dictionary
        """
        return asdict(self)
