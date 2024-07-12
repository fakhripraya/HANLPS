""" Module for Messaging Dtos
"""

from dataclasses import dataclass, asdict
from src.domain.entities.message.message import Message

@dataclass
class MessagingInputDto:
    """ Input Dto for messaging """
    sessionId: str
    content: str

    def to_dict(self):
        """ Convert data into dictionary
        """
        return asdict(self)
    
@dataclass
class MessagingOutputDto:
    """ Output Dto for messaging """
    input: str
    output: str
    output_content: str | None
