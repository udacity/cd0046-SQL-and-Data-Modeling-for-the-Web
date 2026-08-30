from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ArtistDTO:
    id: Optional[int]
    name: str
    city: str
    state: str
    phone: str
    image_link: str
    facebook_link: str
    website: str
    genres: List[str]
    seeking_venue: bool
    seeking_description: str
