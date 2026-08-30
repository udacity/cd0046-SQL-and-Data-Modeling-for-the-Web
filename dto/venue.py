from dataclasses import dataclass
from typing import Optional, List

@dataclass
class VenueDTO:
    id: Optional[int]
    name: str
    city: str
    state: str
    address: str
    phone: str
    image_link: str
    facebook_link: str
    website: str
    seeking_talent: bool = False
    seeking_description: Optional[str] = None
    genres: List[str] = None