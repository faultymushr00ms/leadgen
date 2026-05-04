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
    # Cross-reference tracking — populated by the scraper orchestrator
    source_count: int = 1
    confirmed_by: List[str] = field(default_factory=list)

    def dedup_key(self) -> str:
        """Unique key for deduplication across sources."""
        name = self.company_name.lower().strip()
        # Fall back to city when zip is missing so cross-source matches still work
        location = self.zip_code.strip() or self.city.lower().strip()
        return f"{name}|{location}"

    def merge(self, other: "RawLead"):
        """
        Absorb data from another source's record of the same business.
        Fills any gaps in our data and increments the confidence count.
        """
        if other.source not in self.confirmed_by:
            self.confirmed_by.append(other.source)
            self.source_count += 1
        # Fill empty fields with whatever the other source has
        if not self.phone and other.phone:
            self.phone = other.phone
        if not self.zip_code and other.zip_code:
            self.zip_code = other.zip_code
        if not self.address and other.address:
            self.address = other.address
        if not self.city and other.city:
            self.city = other.city
        if not self.latitude and other.latitude:
            self.latitude = other.latitude
            self.longitude = other.longitude
        # Prefer the more specific industry label (longer = more specific)
        if len(other.industry) > len(self.industry):
            self.industry = other.industry
        if other.notes:
            self.notes = f"{self.notes} | {other.notes}".strip(" |")

    @property
    def confidence(self) -> str:
        """Human-readable confidence label based on how many sources confirmed this."""
        if self.source_count >= 3:
            return "HIGH"
        if self.source_count == 2:
            return "MEDIUM"
        return "LOW"

    def to_prospect_data(self) -> dict:
        """Convert to the format Agent 2 (qualifier) expects."""
        location = f"{self.city}, OH {self.zip_code}".strip(", ")
        known_info = (
            f"Sources: {self.source_count} ({', '.join(self.confirmed_by or [self.source])}) "
            f"| Confidence: {self.confidence}"
        )
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
            "source_count": self.source_count,
            "confidence": self.confidence,
        }


class BaseSource(ABC):
    """All scraper sources implement this interface."""

    name: str = "base"

    @abstractmethod
    def fetch(self) -> List[RawLead]:
        """Pull leads from this source and return them."""
        pass
