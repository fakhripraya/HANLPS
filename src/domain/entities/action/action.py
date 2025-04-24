""" This module has definition of the Action entity
"""

from dataclasses import dataclass, asdict


@dataclass
class Action:
    """Definition of the Action entity"""

    action: str

    @classmethod
    def from_dict(cls, data):
        """Convert data from a dictionary"""
        return cls(**data)

    def to_dict(self):
        """Convert data into dictionary"""
        return asdict(self)
