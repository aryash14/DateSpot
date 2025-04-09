from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class DetailExtractionOutputSchema(BaseModel):
    preferred_atmosphere: Optional[str] = Field(..., description="The preferred atmoshphere")
    cuisine_preferences: Optional[List[str]] = Field(..., description="The type of desired cuisine(s)")
    budget_range: Optional[str] = Field(..., description="The price range.")
    desired_activities: Optional[List[str]] = Field(..., description="A desired activity such as live music, trivia.")
    location_preferences: Optional[str] = Field(..., description="The desired location by the user.")
    other_requirements: Optional[str] = Field(..., description="Any other requirement.")


class DateSpotSchema(BaseModel):
    name: str = Field(..., description="The name of the given place.")
    description: str = Field(..., description="A brief description about the place.")
    category: List[str] = Field(..., description="The types of food or restaurant styles. (e.g. ['Indian Restaurant', 'Bar'])")
    price: str = Field(..., description="The price tag.")
    address: str = Field(..., description="The address of the location.")
    contact_information: str  = Field(..., description="Phone number for the place of interest.")
    reviews: float = Field(..., description="The given rating.")
    website: str = Field(..., description="The website for the given location.")
    image_url: str = Field(..., description="A thumbnail image url.")
    rating: int = Field(..., description="A score between 1 - 5 indicating how well the location aligns with user's requirements.")
    reasoning: str = Field(..., description="A logical reasoning behind the rating.")

class DateSpotListSchema(BaseModel):
    date_spots: List[DateSpotSchema] = Field(..., description="List of date spots found")



class DateSpotReviewSchema(BaseModel):
    # name: str = Field(..., description="The name of the given place.")
    agent_rating: int = Field(..., description="A score between 1 - 5 indicating how well the location aligns with user's requirements.")
    reasoning: str = Field(..., description="A logical reasoning behind the rating.")

class DateSpotReviewSchema(BaseModel):
    date_spots: Dict[str, DateSpotReviewSchema] = Field(..., description="Dictionary of place names mapped to their rating and reasoning.")

