""" This module has definition of the Message entity
"""

from typing import List, Optional
from dataclasses import dataclass, asdict
from src.domain.entities.building.building import Building


@dataclass
class Message:
    """Definition of the Message entity"""

    input: str
    output: str
    output_content: Optional[List[Building]] = None
    action: Optional[dict] = None

    @classmethod
    def from_dict(cls, data):
        """Convert data from a dictionary"""
        return cls(**data)

    def to_dict(self):
        """Convert data into dictionary"""
        return asdict(self)
