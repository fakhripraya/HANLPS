"""
This module defines the Building entity.
"""

from dataclasses import dataclass, asdict
from typing import Union, Optional


@dataclass
class Building:
    """Definition of the Building entity"""

    building_title: Optional[str] = None
    building_address: Optional[str] = None
    building_proximity: Optional[str] = None
    building_facility: Optional[str] = None
    building_note: Optional[str] = None
    building_description: Optional[str] = None
    housing_price: Optional[Union[str, float]] = None
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_whatsapp: Optional[str] = None
    owner_phone_number: Optional[str] = None
    image_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        """Convert data from a dictionary"""
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary")

        return cls(**data)

    def to_dict(self):
        """Convert data into dictionary"""
        return asdict(self)

    def __str__(self):
        """String representation of the Building instance"""
        return (
            f"Building("
            f"building_title={self.building_title}, "
            f"building_address={self.building_address}, "
            f"building_proximity={self.building_proximity}, "
            f"building_facility={self.building_facility}, "
            f"building_note={self.building_note}, "
            f"building_description={self.building_description}, "
            f"housing_price={self.housing_price}, "
            f"owner_name={self.owner_name}, "
            f"owner_email={self.owner_email}, "
            f"owner_whatsapp={self.owner_whatsapp}, "
            f"owner_phone_number={self.owner_phone_number}, "
            f"image_url={self.image_url})"
        )
