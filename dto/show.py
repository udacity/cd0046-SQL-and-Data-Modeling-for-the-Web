"""
Data transfer object for show data between service and controller layers.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ShowDTO:
    """Show data transfer object."""
    id: Optional[int]
    venue_id: int
    artist_id: int
    start_time: str
    end_time: Optional[str] = None
