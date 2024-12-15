""" This module has definition of the SearchResult entity for Agent Tool
"""

from dataclasses import dataclass, asdict
from src.domain.entities.building.building import Building


@dataclass
class SearchResult:
    """Definition of the SearchResult entity"""

    results: list[Building] | None

    @classmethod
    def from_dict(cls, data):
        """Convert data from a dictionary"""
        return cls(**data)

    def to_dict(self):
        """Convert data into dictionary"""
        return asdict(self)
