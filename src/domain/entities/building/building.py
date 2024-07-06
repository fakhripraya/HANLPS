"""
This module defines the Building entity.
"""

from dataclasses import dataclass, asdict, field
from typing import Union, Optional

@dataclass
class Building:
    """ Definition of the Building entity """
    building_title: Optional[str] = None
    building_address: Optional[str] = None
    building_description: Optional[str] = None
    housing_price: Optional[Union[str, float]] = None
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_whatsapp: Optional[str] = None
    owner_phone_number: Optional[str] = None
    image_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        """ Convert data from a dictionary """
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary")

        return cls(**data)

    def to_dict(self):
        """ Convert data into dictionary """
        return asdict(self)

    def __str__(self):
        """ String representation of the Building instance """
        return f"Building(title={self.building_title}, address={self.building_address}, price={self.housing_price})"
