""" This module has definition of the Building entity
"""


from dataclasses import dataclass, asdict

@dataclass
class Building:
    """ Definition of the Building entity
    """
    building_title: str | None
    building_address: str | None

    @classmethod
    def from_dict(cls, data):
        """ Convert data from a dictionary
        """
        return cls(**data)

    def to_dict(self):
        """ Convert data into dictionary
        """
        return asdict(self)
