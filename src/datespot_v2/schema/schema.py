from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class UserRequirementSchema(BaseModel):
    preferred_atmosphere: Optional[str] = Field(..., description="The preferred atmoshphere")
    cuisine_preferences: Optional[List[str]] = Field(..., description="The type of desired cuisine(s)")
    budget_range: Optional[str] = Field(..., description="The price range.")
    desired_activities: Optional[List[str]] = Field(..., description="A desired activity such as live music, trivia.")
    location_preferences: Optional[str] = Field(..., description="The desired location by the user.")
    other_requirements: Optional[str] = Field(..., description="Any other requirement.")

class DetailExtractionOutputSchema(BaseModel):
    user_requirements: UserRequirementSchema = Field(..., description= "All of user requirements extraced from the user input.")
    search_queries: List[str] = Field(..., description="A list of search queries based on the extracted details.")
    location: str = Field(..., description="The specified location in the format 'Neighborhood (if given), City, State.'")


class DateSpotSchema(BaseModel):
    title: str = Field(..., description="The name of the given place.")
    description: str = Field(..., description="A brief description about the place.")
    types: Optional[List[str]] = Field(..., description="The types of food or restaurant styles. (e.g. ['Indian Restaurant', 'Bar'])")
    priceLevel: Optional[str] = Field(..., description="The price tag.")
    address: Optional[str] = Field(..., description="The address of the location.")
    phoneNumber: Optional[str]  = Field(..., description="Phone number for the place of interest.")
    rating: Optional[float] = Field(..., description="The given rating.")
    website: Optional[str] = Field(..., description="The website for the given location.")
    thumbnailUrl: Optional[str] = Field(..., description="A thumbnail image url.")
    

class DateSpotListSchema(BaseModel):
    date_spots: List[DateSpotSchema] = Field(..., description="List of date spots found")



class DateSpotReviewSchema(BaseModel):
    title: str = Field(..., description="The name of the given place.")
    description: str = Field(..., description="A brief description about the place.")
    types: Optional[List[str]] = Field(..., description="The types of food or restaurant styles. (e.g. ['Indian Restaurant', 'Bar'])")
    priceLevel: Optional[str] = Field(..., description="The price tag.")
    address: Optional[str] = Field(..., description="The address of the location.")
    phoneNumber: Optional[str]  = Field(..., description="Phone number for the place of interest.")
    rating: Optional[float] = Field(..., description="The given rating.")
    website: Optional[str] = Field(..., description="The website for the given location.")
    thumbnailUrl: Optional[str] = Field(..., description="A thumbnail image url.")
    agent_rating: int = Field(..., description="A score between 1 - 5 indicating how well the location aligns with user's requirements.")
    reasoning: str = Field(..., description="A logical reasoning behind the rating.")
    

class DateSpotReviewListSchema(BaseModel):
    date_spots: List[DateSpotReviewSchema] = Field(..., description="Final list of date spots found with their agent rating and reasoning.")
