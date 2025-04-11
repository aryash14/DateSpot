import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
from PIL import Image
import json
import time
import os
from datetime import datetime
from datespot.crew import Datespot
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import requests
from io import BytesIO
import html
from datespot_v2.crew import get_deduplication_crew, get_extarcter_crew, get_finder_crew, calculate_cost
import asyncio

# Set page config
st.set_page_config(
    page_title="DateSpot Recommender",
    page_icon="💑",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

if 'image_cache' not in st.session_state:
    st.session_state.image_cache = {}

def get_coordinates(address):
        geolocator = Nominatim(user_agent="geocoding_app")
        location = geolocator.geocode(address)
        # if location != "San Francisco, CA":
        return location.latitude, location.longitude
        # else: # default would be SF coordinates
        #     return 37.7792588, -122.4193286

def create_map(place, coordinate_convertion):
    """Create a Folium map with a single marker for the selected place"""
    # Get coordinates from address
    if coordinate_convertion:
        coordinates = get_coordinates(place.get('address'))
    else:
        coordinates = (place.get("latitude", None), place.get("longitude", None))
    
    if coordinates == (None, None):
        # Default to San Francisco coordinates if geocoding fails
        coordinates = (37.7792588, -122.4193286)
        st.warning("Could not geocode the address. Showing default location.")
    
    # Create map centered on the location
    m = folium.Map(location=coordinates, zoom_start=15)
    
    # Add marker for the place
    folium.Marker(
        location=coordinates,
        popup=f"""
            <b>{place['title']}</b><br>
            {place.get('address', 'N/A')}<br>
            Rating: {place.get('rating', 'N/A')}<br>
            Price: {place.get('price', 'N/A')}
        """,
        tooltip=place['title']
    ).add_to(m)
    
    return m

def run_crew(user_input):
    """Run the Datespot crew with user input and return the results"""
    try:
        inputs = {
            'user_input': user_input
        }
        
        start_time = time.time()
        # Create and run the crew
        crew = Datespot().crew()
        
        results = crew.kickoff(inputs=inputs)
        
        end_time = time.time()
        # Calculate costs and runtime
        costs = 1.93 * (crew.usage_metrics.prompt_tokens + crew.usage_metrics.completion_tokens) / 1_000_000
        st.metric(label="💰 Total Cost", value=f"${costs:.4f}")
        st.metric(label="⏱️ Total Runtime", value=f"{end_time - start_time:.2f} seconds")
    
    
        return results
    except Exception as e:
        st.error(f"An error occurred while running the crew: {e}")
        return None



async def async_multiple_crews(user_input):
    start_time = time.time()

    st.info("🔍 Starting extracter crew...")
    extracter_crew = get_extarcter_crew()
    extracter_res = extracter_crew.kickoff(inputs={'user_input': user_input}).pydantic.model_dump()
    st.success("✅ Extracter crew completed.")

    search_queries = extracter_res["search_queries"]
    location = extracter_res["location"]
    user_requirements = extracter_res["user_requirements"]

    st.info("🔎 Starting finder crew for each search query...")
    finder_crew = get_finder_crew()
    results = []
    for idx, search_query in enumerate(search_queries):
        st.write(f"📌 Finder agent #{idx + 1} starting with query: '{search_query}'")
        results.append(
            finder_crew.kickoff_async(inputs={
                "search_query": search_query,
                "location": location,
                "user_requirements": user_requirements
            })
        )

    completed_results = await asyncio.gather(*results)
    st.success("✅ Finder crew completed all searches.")

    overall = []
    for results in completed_results:
        overall.extend(results.pydantic.model_dump()["date_spots"])

    st.info("🧹 Starting deduplication crew...")
    deduplication_crew = get_deduplication_crew()
    modified_overall = deduplication_crew.kickoff(inputs={'overall_finds': overall}).pydantic.model_dump()
    st.success("✅ Deduplication completed.")

    costs = calculate_cost([extracter_crew, finder_crew, deduplication_crew])
    end_time = time.time()

    st.metric(label="💰 Total Cost", value=f"${costs:.4f}")
    st.metric(label="⏱️ Total Runtime", value=f"{end_time - start_time:.2f} seconds")
    return modified_overall

def load_image_with_cache(url, timeout=5):
    """Load image with caching and proper error handling"""
    if url in st.session_state.image_cache:
        return st.session_state.image_cache[url]
    
    try:
        # Add a User-Agent header to avoid some websites blocking requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        # Try to open and verify the image
        img = Image.open(BytesIO(response.content))
        img.verify()  # Verify it's actually an image
        
        # Store in cache and return the image bytes
        st.session_state.image_cache[url] = response.content
        return response.content
    except Exception as e:
        # Return None on any error
        return None

def create_styled_card(place):
    # Create a clean card layout using Streamlit's native components
    with st.container():
        # Create a bordered container with custom CSS
        st.markdown("""
        <style>
        .card-container {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 0;
            margin-bottom: 20px;
            background-color: white;
        }
        .info-header {
            font-weight: bold;
            color: #555;
            text-transform: uppercase;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Title and heading (outside the card border)
        st.markdown(f"### {place['title']}")
        if place.get('description'):
            st.markdown(f"**{place.get('description')}**")
        
        # Start the card container
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        
        # Types and Price Level in a row
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown('<div class="info-header">Types</div>', unsafe_allow_html=True)
            categories = ', '.join(place.get('types', ['N/A']))
            st.markdown(f"<div style='padding: 0 10px 10px;'>{categories}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="info-header">Price Level</div>', unsafe_allow_html=True)
            price_level = place.get('priceLevel', 'N/A')
            if isinstance(price_level, (int, float)):
                price_symbols = "$" * int(price_level)
            else:
                price_symbols = price_level
            st.markdown(f"<div style='padding: 0 10px 10px;'>{price_symbols}</div>", unsafe_allow_html=True)
        
        # Rating and Agent Rating
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="info-header">Rating</div>', unsafe_allow_html=True)
            rating = place.get('rating', 'N/A')
            st.markdown(f"<div style='padding: 0 10px 10px;'>⭐ {rating}</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="info-header">Agent Rating</div>', unsafe_allow_html=True)
            agent_rating = place.get('agent_rating', 'N/A')
            st.markdown(f"<div style='padding: 0 10px 10px;'>⭐ {agent_rating}/5</div>", unsafe_allow_html=True)
        
        # Agent Reasoning
        st.markdown('<div class="info-header">Why We Recommend This</div>', unsafe_allow_html=True)
        st.markdown(f"<div style='padding: 0 10px 10px;'>{place.get('reasoning', 'N/A')}</div>", unsafe_allow_html=True)
        
        # Address and Website in a table-like format
        st.markdown("""
        <div style='display: flex; border-top: 1px solid #ddd;'>
            <div style='padding: 10px; font-weight: bold; width: 30%; border-right: 1px solid #ddd;'>Address</div>
            <div style='padding: 10px; flex-grow: 1;'>""" + place.get('address', 'N/A') + """</div>
        </div>
        """, unsafe_allow_html=True)
        
        website = place.get('website', 'N/A')
        website_display = f"<a href='{website}' target='_blank'>{website}</a>" if website != 'N/A' else 'N/A'
        st.markdown(f"""
        <div style='display: flex; border-top: 1px solid #ddd;'>
            <div style='padding: 10px; font-weight: bold; width: 30%; border-right: 1px solid #ddd;'>Website</div>
            <div style='padding: 10px; flex-grow: 1;'>{website_display}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Close the card container
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Opening Hours (if available) as an expander
        opening_hours = place.get('openingHours')
        if opening_hours and isinstance(opening_hours, dict):
            with st.expander("Opening Hours"):
                hours_df = pd.DataFrame(list(opening_hours.items()), columns=['Day', 'Hours'])
                st.table(hours_df.set_index('Day'))


def main():
    st.title("DateSpot Finder")
    st.markdown("""
    Describe your ideal date, and we'll recommend the perfect spots for you!
    """)
    
    # Initialize session state for current index if it doesn't exist
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    
    # User input
    user_input = st.text_area(
        "Describe your ideal date (e.g., 'A romantic evening with great food and live music'):",
        height=150
    )
    
    col1, col2, _ = st.columns([1, 1, 6])  # two equal columns, third empty to push spacing

    with col1:
        quick_search = st.button("Quick Search")

    with col2:
        deep_search = st.button("Deep Search")

    if quick_search:
        if not user_input:
            st.warning("Please describe your ideal date first!")
        else:
            with st.spinner("Finding the perfect spots for your date..."):
                agentRankings = run_crew(user_input).pydantic.model_dump()["date_spots"]
                with open('./places_found.json', 'r') as f:
                    places = json.load(f)["places"]

                places_mod = []
                for place in places:
                    name = place["title"]
                    ranking_data = agentRankings.get(name, {})  # fallback to empty dict if name not found
                    combined_entry = {**place, **ranking_data}
                    places_mod.append(combined_entry)
                
                if not places_mod:  # Check if the list is empty
                   st.image("src/placeholders/NoResults.png", caption="No results found", width=300)

                else:
                    st.session_state.places = sorted(places_mod, key=lambda x: x["agent_rating"], reverse=True)
                    st.session_state.current_index = 0
                    st.session_state.coordinate_convertion = False


    elif deep_search:
        if not user_input:
            st.warning("Please describe your ideal date first!")
        else:
            with st.spinner("Finding the perfect spots for your date. Hang tight this takes a bit more work..."):
                places= asyncio.run(async_multiple_crews(user_input))
                places_mod = places["date_spots"]
                if not places_mod:  # Check if the list is empty
                   st.image("src/placeholders/NoResults.png", caption="No results found", width=300)
                else:
                    st.session_state.places = sorted(places_mod, key=lambda x: x["agent_rating"], reverse=True)
                    st.session_state.current_index = 0
                    st.session_state.coordinate_convertion = False
        

    # Display results if we have places in session state
    if 'places' in st.session_state and st.session_state.places:
        places = st.session_state.places
        coordinate_convertion = st.session_state.coordinate_convertion
        current_index = st.session_state.current_index
        
        # Display current place
        place = places[current_index]
        # agentRanking = agentRankings.get(place["title"], {"rating": "NA", "reasoning": "N/A"})
        col1, col2 = st.columns([1, 2])
        
        with col1:
            thumbnail_url = place.get('thumbnailUrl')
            if thumbnail_url:
                with st.spinner('Loading image...'):
                    img_data = load_image_with_cache(thumbnail_url)
                    if img_data:
                        st.image(
                            img_data, 
                            use_container_width=True,
                            caption=place['title']
                        )
                    else:
                        st.image(
                            "https://via.placeholder.com/300x200?text=Image+Error", 
                            use_container_width=True,
                            caption="Image failed to load"
                        )
                        st.warning(f"Could not load image for {place['title']}")
            else:
                st.image( 
                    "src/placeholders/NoImageAvailable.png", 
                    use_container_width=True,
                    caption="No image available"
                )
                st.info("No image available for this location")
            
            # Display map underneath the image
            st.markdown("### Location")
            m = create_map(place, coordinate_convertion)
            folium_static(m, width=400)
        
        with col2:
            create_styled_card(place)
        # Navigation buttons
        col1, col2, _ = st.columns([1, 2, 1])
        with col2:
            nav_col1, nav_col2, nav_col3 = st.columns([1, 0.5, 1])
            with nav_col1:
                st.button(
                    "Previous", 
                    disabled=current_index == 0, 
                    use_container_width=True, 
                    on_click=lambda: st.session_state.update(current_index=current_index - 1)
                )

            with nav_col2:
                st.markdown(
                f"""
                <div style='text-align: center; font-size: 20px; line-height: 2;'>
                    <strong>{current_index + 1}</strong> / {len(places)}
                </div>
                """,
                unsafe_allow_html=True
                )

            with nav_col3:
                st.button(
                    "Next", 
                    disabled=current_index == len(places) - 1,
                    use_container_width=True,
                    on_click=lambda: st.session_state.update(current_index=current_index + 1)
                )

if __name__ == "__main__":
    main() 