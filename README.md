# DateSpot Recommender

A web application that recommends perfect date spots based on user preferences using Streamlit and CrewAI.

## Features

- Natural language input for describing ideal date preferences
- Interactive map showing all recommended locations
- Detailed information for each recommended spot
- Beautiful and modern UI with responsive design

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DateSpot.git
cd DateSpot
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Running the App

To start the Streamlit app, run:
```bash
streamlit run src/app.py
```

The app will be available at `http://localhost:8501`

## Project Structure

- `src/app.py`: Main Streamlit application
- `places_found.json`: Database of date spots
- `pyproject.toml`: Project configuration and dependencies

## Requirements

- Python 3.10 or higher
- Streamlit
- Folium
- Pandas
- Pillow
- CrewAI

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
