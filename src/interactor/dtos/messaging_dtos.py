""" Module for Messaging Dtos
"""

from dataclasses import dataclass, asdict
from src.domain.entities.message import Message

@dataclass
class MessagingInputDto:
    """ Input Dto for messaging """
    content: str

    def to_dict(self):
        """ Convert data into dictionary
        """
        return asdict(self)
    
@dataclass
class MessagingOutputDto:
    """ Output Dto for messaging """
    message: Message
