"""
This module defines the Building entity.
"""

from dataclasses import dataclass, asdict, field
from typing import Union, Optional

@dataclass
class Building:
    """ Definition of the Building entity """
    buildingTitle: Optional[str] = None
    buildingAddress: Optional[str] = None
    buildingProximity: Optional[str] = None
    buildingFacility: Optional[str] = None
    buildingDescription: Optional[str] = None
    housingPrice: Optional[Union[str, float]] = None
    ownerName: Optional[str] = None
    ownerEmail: Optional[str] = None
    ownerWhatsapp: Optional[str] = None
    ownerPhoneNumber: Optional[str] = None
    imageURL: Optional[str] = None

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
        return (f"Building("
                f"buildingTitle={self.buildingTitle}, "
                f"buildingAddress={self.buildingAddress}, "
                f"buildingProximity={self.buildingProximity}, "
                f"buildingFacility={self.buildingFacility}, "
                f"buildingDescription={self.buildingDescription}, "
                f"housingPrice={self.housingPrice}, "
                f"ownerName={self.ownerName}, "
                f"ownerEmail={self.ownerEmail}, "
                f"ownerWhatsapp={self.ownerWhatsapp}, "
                f"ownerPhoneNumber={self.ownerPhoneNumber}, "
                f"imageURL={self.imageURL})")
