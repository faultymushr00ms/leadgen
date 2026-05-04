from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import List


@dataclass
class RawLead:
    company_name: str
    address: str
    city: str
    zip_code: str = ""
    phone: str = ""
    industry: str = ""
    business_type: str = ""
    source: str = ""
    notes: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    state: str = "OH"

    def dedup_key(self) -> str:
        """Unique key for deduplication across sources."""
        name = self.company_name.lower().strip()
        zip_code = self.zip_code.strip()
        return f"{name}|{zip_code}"

    def to_prospect_data(self) -> dict:
        """Convert to the format Agent 2 (qualifier) expects."""
        location = f"{self.city}, OH {self.zip_code}".strip(", ")
        known_info = f"Source: {self.source}"
        if self.phone:
            known_info += f" | Phone: {self.phone}"
        if self.notes:
            known_info += f" | {self.notes}"
        return {
            "company_name": self.company_name,
            "industry": self.industry or self.business_type,
            "estimated_rce": 0,  # Agent 2 estimates this
            "location": location,
            "phone": self.phone,
            "known_info": known_info,
        }


class BaseSource(ABC):
    """All scraper sources implement this interface."""

    name: str = "base"

    @abstractmethod
    def fetch(self) -> List[RawLead]:
        """Pull leads from this source and return them."""
        pass
