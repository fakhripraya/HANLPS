""" This module has definition of the Building entity
"""


from dataclasses import dataclass, asdict
from typing import List
from src.domain.entities.building.building import Building

@dataclass
class Message:
    """ Definition of the Message entity
    """
    input: str
    output: str
    output_content: List[Building] | None

    @classmethod
    def from_dict(cls, data):
        """ Convert data from a dictionary
        """
        return cls(**data)

    def to_dict(self):
        """ Convert data into dictionary
        """
        return asdict(self)
