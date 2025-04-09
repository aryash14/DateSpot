from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import requests
import json
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

load_dotenv()

class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    search_query: str = Field(..., description="A generated search query to be used by Serper API excluding location mentions")
    location: Optional[str] = Field(..., description="The geological location to search for places.")

class CustomSerperPlaceTool(BaseTool):
    name: str = "Custom Serper Place Tool"
    description: str = (
        "Search the internet for locations."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput
    
    def _get_lat_long(self, location):
        geolocator = Nominatim(user_agent="geocoding_app")
        location = geolocator.geocode(location)
        if location != "San Francisco, CA":
            return location.latitude, location.longitude, "16z"
        else: # default would be SF coordinates
            return 37.7792588, -122.4193286, "13z"

    def _extract_place_info(self, place):
        return {
            "Name": place.get("title"),
            "Category": place.get("types", []),
            "Price": place.get("priceLevel"),
            "Description": place.get("description"),
            "Address": place.get("address"),
            "Rating": place.get("rating"),
            # "openingHours": place.get("openingHours")
        }
    def _convert_price_level(self, price_level):
        """Convert price level symbols to their corresponding price ranges"""
        if price_level == '$':
            return '$0-10'
        elif price_level == '$$':
            return '$10-25'
        elif price_level == '$$$':
            return '$25-50'
        elif price_level == '$$$$':
            return '$50>'
        else:
            return price_level
        
    def _normalize_prices_in_response(self, response_data):
        """Normalize price levels in the entire response data structure"""
        if 'places' in response_data:
            for place in response_data['places']:
                if 'priceLevel' in place:
                    place['priceLevel'] = self._convert_price_level(place['priceLevel'])
        return response_data

    def _run(self, search_query: str, location: str ) -> str:
        """
        Search the internet for news.
        """

        url = "https://google.serper.dev/maps"
        if not location:
            location = "San Francisco, CA"
        
        latitude, longitude, zoom_value = self._get_lat_long(location)

        payload = json.dumps({
            "q": search_query,
            "ll": f"@{latitude},{longitude},{zoom_value}"
        })

        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        # Parse the JSON response
        if response.status_code == 200:
            response_data = response.json()
            # Normalize prices in the entire response
            normalized_data = self._normalize_prices_in_response(response_data)
            # Write normalized response data to JSON file
            with open('places_found.json', 'w') as f:
                json.dump(normalized_data, f, indent=2)
            # Extract only the 'news' property
            raw_places = normalized_data.get('places', [])
            filtered_data = [self._extract_place_info(place) for place in raw_places]
            # Convert the news data back to a JSON string
            return json.dumps(filtered_data, indent=2)

        else:
            # Fallback in case of timeouts or other issues
            return json.dumps({"error": "Failed to fetch any locations."})


    
    # def _run(self, search_query: str, location: str ) -> str:
    #     """
    #     Search the internet for news.
    #     """

    #     url = "https://google.serper.dev/places"
    #     if not location:
    #         location = "San Francisco, CA"
        
    #     payload = json.dumps({
    #         "q": search_query,
    #         # "num": 20,
    #         "location": location
    #     })

    #     headers = {
    #         'X-API-KEY': os.getenv('SERPER_API_KEY'),
    #         'Content-Type': 'application/json'
    #     }

    #     response = requests.request("POST", url, headers=headers, data=payload)

    #     # Parse the JSON response
    #     if response.status_code == 200:
    #         response_data = response.json()
    #         # Extract only the 'news' property
    #         news_data = response_data.get('places', [])
    #         # Convert the news data back to a JSON string
    #         return json.dumps(news_data, indent=2)

    #     else:
    #         # Fallback in case of timeouts or other issues
    #         return json.dumps({"error": "Failed to fetch any locations."})