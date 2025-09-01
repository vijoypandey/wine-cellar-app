# API Reference - Drinking Window Service

## DrinkingWindowService

### Class Methods

#### `__init__(self)`
Initialize the service with session configuration and source priority list.

**Parameters:** None

**Returns:** DrinkingWindowService instance

**Example:**
```python
service = DrinkingWindowService()
```

---

#### `get_drinking_window(wine_name, vintage, grape_varietal=None, country=None, region=None, color=None)`
Main method to retrieve drinking window information for a wine.

**Parameters:**
- `wine_name` (str): Name of the wine
- `vintage` (int): Vintage year
- `grape_varietal` (str, optional): Primary grape variety
- `country` (str, optional): Country of origin
- `region` (str, optional): Wine region
- `color` (str, optional): Wine color ('Red' or 'White')

**Returns:** Dict with the following structure:
```python
{
    'drinking_window': 'YYYY-YYYY',    # String format date range
    'peak_year': YYYY,                 # Integer peak drinking year
    'confidence': 'high|medium|low',   # Confidence level
    'source': 'source_name',           # Data source
    'notes': 'description'             # Additional context
}
```

**Example:**
```python
result = service.get_drinking_window(
    wine_name="Chateau Margaux",
    vintage=2015,
    grape_varietal="Cabernet Sauvignon",
    country="France",
    region="Bordeaux",
    color="Red"
)
# Returns: {
#     'drinking_window': '2023-2055',
#     'peak_year': 2033,
#     'confidence': 'medium',
#     'source': 'Fallback Rules',
#     'notes': 'Bordeaux First Growth estimate'
# }
```

---

## Source Scrapers

Each source has a dedicated scraper method following the pattern `_scrape_[source_name]`.

### Common Pattern

All scraper methods follow this signature:

```python
def _scrape_source_name(self, wine_name: str, vintage: int, grape_varietal: str,
                        country: str, region: str, color: str) -> Optional[Dict]
```

**Parameters:**
- Same as `get_drinking_window()` method

**Returns:**
- `Dict`: Drinking window data if found
- `None`: If no data found or error occurred

### Individual Source Methods

#### `_scrape_cellartracker()`
Scrapes CellarTracker.com for crowd-sourced drinking windows.

**URL Pattern:** `https://www.cellartracker.com/list.asp?Table=List&iUserOverride=0&szSearch={query}`

**Confidence:** High (when data found)

**Pattern Examples:**
- "drink: 2025-2035"
- "drinking window: 2024-2030" 
- "cellar until: 2028"

#### `_scrape_wine_searcher()`
Scrapes Wine-Searcher.com for aggregated professional data.

**URL Pattern:** `https://www.wine-searcher.com/find/{query}`

**Confidence:** High (when data found)

#### `_scrape_erobertparker()`
Searches for Robert Parker Wine Advocate reviews via Google.

**Search Pattern:** `"wine_name" vintage site:erobertparker.com`

**Confidence:** High (professional critic)

**Special Patterns:**
- "anticipated maturity: 2025-2035"
- "cellar for: 8 years" (converted to date range)

#### `_scrape_vinous()`
Searches Vinous.com professional reviews.

**Search Pattern:** `"wine_name" vintage site:vinous.com`

**Confidence:** High (professional critics)

#### `_scrape_jancisrobinson()`
Searches Jancis Robinson MW tasting notes.

**Search Pattern:** `"wine_name" vintage site:jancisrobinson.com`

**Confidence:** High (Master of Wine)

#### `_scrape_vivino()`
Scrapes Vivino.com user community data.

**URL Pattern:** `https://www.vivino.com/search/wines?q={query}`

**Confidence:** Medium (user data)

#### `_scrape_wine_com()`
Scrapes Wine.com commercial wine data.

**URL Pattern:** `https://www.wine.com/search/{query}`

**Confidence:** Medium (commercial data)

**Special Patterns:**
- "cellaring potential: 10 years" (converted to range)

#### `_scrape_decanter()`
Searches Decanter magazine reviews.

**Search Pattern:** `"wine_name" vintage site:decanter.com`

**Confidence:** Medium (wine magazine)

#### `_scrape_wine_spectator()`
Searches Wine Spectator reviews.

**Search Pattern:** `"wine_name" vintage site:winespectator.com`

**Confidence:** Medium (wine magazine)

---

## Fallback Rule Engine

### `_get_fallback_window(wine_name, vintage, grape_varietal, country, region, color)`

Provides intelligent estimates when web scraping fails.

**Parameters:** Same as main method

**Returns:** Dict with drinking window estimate

### Rule Categories

#### Bordeaux Classification Rules

**First Growths Detection:**
```python
first_growths = ['lafite', 'latour', 'margaux', 'mouton', 'haut-brion']
if any(name in wine_name.lower() for name in first_growths):
    return {
        'drinking_window': f"{vintage + 8}-{vintage + 40}",
        'confidence': 'medium',
        'source': 'Fallback Rules',
        'notes': 'Bordeaux First Growth estimate'
    }
```

**Château Detection:**
- Left Bank: vintage + 5 to vintage + 25 years
- Right Bank (Saint-Émilion, Pomerol): vintage + 3 to vintage + 20 years

#### Regional Rules

**Burgundy:**
- Domaine + Burgundy keywords detected
- Red: vintage + 3 to vintage + 15 years
- White: vintage + 1 to vintage + 8 years

**Italy:**
- Barolo/Barbaresco: vintage + 5 to vintage + 25 years
- Brunello: vintage + 4 to vintage + 20 years
- Chianti Classico: vintage + 2 to vintage + 12 years

**Champagne:**
- vintage + 3 to vintage + 15 years

#### Varietal Rules

**Red Varietals:**
```python
varietals = {
    'cabernet sauvignon': {
        'usa': (3, 15),
        'general': (4, 18)
    },
    'pinot noir': (2, 10),
    'merlot': (2, 12),
    'syrah': (3, 15)
}
```

**White Varietals:**
```python
varietals = {
    'chardonnay': {
        'chablis': (1, 8),
        'general': (1, 6)
    },
    'sauvignon blanc': (0, 4),
    'riesling': (1, 12)
}
```

#### Color-Based Fallback

**Final Fallback Rules:**
- Red wine: vintage + 2 to vintage + 12 years
- White wine: vintage to vintage + 5 years
- Unknown: vintage + 1 to vintage + 8 years

---

## Utility Methods

### `_calculate_peak_year(drinking_window)`
Calculates the optimal drinking year from a window range.

**Parameters:**
- `drinking_window` (str): Format "YYYY-YYYY"

**Returns:**
- `int`: Peak year (start + 1/3 of range)
- `None`: If calculation fails

**Example:**
```python
peak = service._calculate_peak_year("2025-2040")
# Returns: 2030 (2025 + (40-25)/3)
```

### Caching System

**Cache Key Format:**
```python
cache_key = f"{wine_name}_{vintage}".lower().replace(' ', '_')
```

**Cache Structure:**
```python
self.cache = {
    'chateau_lafite_rothschild_2020': {
        'drinking_window': '2028-2060',
        'confidence': 'medium',
        'source': 'Fallback Rules',
        'notes': 'Bordeaux First Growth estimate',
        'peak_year': 2038
    }
}
```

---

## Error Handling

### Exception Types

**Network Errors:**
- Connection timeouts (15 seconds)
- HTTP status code errors
- DNS resolution failures

**Parsing Errors:**
- Invalid HTML structure
- Regex pattern failures
- Date format issues

**Data Validation Errors:**
- Invalid vintage years
- Malformed drinking windows
- Missing required parameters

### Error Response

When all sources fail, the service guarantees a response through fallback rules:

```python
# Never returns None - always provides estimate
{
    'drinking_window': 'YYYY-YYYY',
    'confidence': 'low',
    'source': 'Fallback Rules',
    'notes': 'Generic wine estimate',
    'peak_year': YYYY
}
```