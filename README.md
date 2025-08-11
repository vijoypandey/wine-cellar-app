# Wine Cellar Tracker

A web application to track and manage your wine collection across multiple cellars.

## Features

- **Wine Entry**: Add wines with name, vintage, price, store, and storage location
- **Autocomplete**: Wine name and store suggestions based on existing entries
- **Automatic Data Lookup**: Web scraping to find wine characteristics including:
  - Drinking window
  - Wine color (Red/White)
  - Country and region
  - Grape varietal
  - Ratings from multiple sources
- **Collection Management**: View, sort, and filter your entire collection
- **Multi-Cellar Support**: Track wines across different cellars and racks

## Installation

1. Navigate to the project directory:
   ```bash
   cd wine-cellar-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and go to `http://localhost:5000`

## Usage

1. **Add a Wine**: Click "Add Wine" to enter a new wine with all details
2. **View Collection**: See all your wines with sorting and filtering options
3. **Search & Filter**: Find specific wines by color, cellar, store, or other criteria

## Database

The application uses SQLite database (`wine_cellar.db`) with the following tables:
- `wine`: Main wine entries with all details
- `store`: Store information
- `wine_rating`: Individual ratings from different sources

## Web Scraping

The app attempts to automatically gather wine information from web searches. If no data is found, it falls back to mock data for demonstration purposes.

## Technologies Used

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite
- **Frontend**: HTML, Bootstrap 5, JavaScript
- **Web Scraping**: Requests, BeautifulSoup