# Drinking Window Service Documentation

## Overview

The Drinking Window Service is a comprehensive system that provides accurate wine drinking window predictions by consulting multiple trusted wine sources and falling back to intelligent rule-based estimates. This service significantly enhances the wine cellar app's ability to provide valuable aging and consumption guidance.

## Architecture

### Multi-Source Cascade System

The service follows a priority-ordered cascade through trusted wine sources:

**Tier 1: High Accuracy Specific Wine Data**
1. **CellarTracker.com** - Crowd-sourced collector data with real-world drinking experiences
2. **Wine-Searcher.com** - Professional aggregated data from multiple wine sources
3. **eRobertParker.com** - Wine Advocate critic reviews with professional assessments
4. **Vinous.com** - Professional wine reviews from industry experts
5. **JancisRobinson.com** - Master of Wine tasting notes and recommendations

**Tier 2: Generic Wine Type Data**
6. **Vivino.com** - Large user database with community-driven recommendations
7. **Wine.com** - Producer-provided cellaring information
8. **Decanter.com** - Wine magazine professional reviews
9. **Wine Spectator** - Professional ratings with drinking recommendations

**Tier 3: Fallback Rule Engine**
10. Comprehensive rule-based estimates using wine characteristics

### Data Flow

```
Wine Input → Source 1 → Source 2 → ... → Source N → Fallback Rules → Result
            ↓ (if data found)
         Cache & Return
```

## Features

### Enhanced Database Schema

New fields added to the Wine model:
- `drinking_window_confidence`: 'high', 'medium', or 'low'
- `drinking_window_source`: Source that provided the data
- `peak_drinking_year`: Calculated optimal drinking year
- `window_notes`: Additional context about the drinking window

### Confidence Scoring

- **High Confidence**: Data from professional critics or specialized wine sites
- **Medium Confidence**: Data from wine magazines or regional pattern matching
- **Low Confidence**: Generic varietal-based or color-based estimates

### Source Attribution

Every drinking window includes source attribution, allowing users to understand where the recommendation originated and make informed decisions.

## Fallback Rule Engine

### Bordeaux Classifications

**First Growths (Lafite, Latour, Margaux, Mouton, Haut-Brion)**
- Drinking Window: Vintage + 8 to Vintage + 40 years
- Exceptional longevity due to structure and reputation

**Left Bank Bordeaux**
- Drinking Window: Vintage + 5 to Vintage + 25 years
- Cabernet Sauvignon-dominant blends with good aging potential

**Right Bank Bordeaux (Saint-Émilion, Pomerol)**
- Drinking Window: Vintage + 3 to Vintage + 20 years
- Merlot-dominant wines that mature earlier

### Burgundy Classifications

**Red Burgundy**
- Drinking Window: Vintage + 3 to Vintage + 15 years
- Pinot Noir-based wines with moderate aging potential

**White Burgundy**
- Drinking Window: Vintage + 1 to Vintage + 8 years
- Chardonnay-based wines for earlier consumption

### Italian Wine Classifications

**Barolo/Barbaresco**
- Drinking Window: Vintage + 5 to Vintage + 25 years
- Nebbiolo-based wines requiring extended aging

**Brunello di Montalcino**
- Drinking Window: Vintage + 4 to Vintage + 20 years
- Sangiovese-based wines with good longevity

**Chianti Classico**
- Drinking Window: Vintage + 2 to Vintage + 12 years
- Moderate aging potential

### Champagne & Sparkling

**Vintage Champagne**
- Drinking Window: Vintage + 3 to Vintage + 15 years
- Can develop complexity with age

### Varietal-Based Rules

**Red Varietals**
- **Cabernet Sauvignon**: 
  - USA: Vintage + 3 to Vintage + 15 years
  - General: Vintage + 4 to Vintage + 18 years
- **Pinot Noir**: Vintage + 2 to Vintage + 10 years
- **Merlot**: Vintage + 2 to Vintage + 12 years
- **Syrah/Shiraz**: Vintage + 3 to Vintage + 15 years

**White Varietals**
- **Chardonnay**: 
  - Chablis: Vintage + 1 to Vintage + 8 years
  - General: Vintage + 1 to Vintage + 6 years
- **Sauvignon Blanc**: Vintage to Vintage + 4 years
- **Riesling**: Vintage + 1 to Vintage + 12 years

## Technical Implementation

### Class Structure

```python
class DrinkingWindowService:
    def __init__(self):
        # Initialize session and sources
    
    def get_drinking_window(wine_name, vintage, grape_varietal, country, region, color):
        # Main entry point - returns complete drinking window data
    
    def _scrape_source(source, ...):
        # Route to specific source scraper
    
    def _scrape_[source_name](...):
        # Individual source scrapers
    
    def _get_fallback_window(...):
        # Rule-based fallback system
    
    def _calculate_peak_year(drinking_window):
        # Calculate peak drinking year from range
```

### Pattern Matching

Each source uses specific regex patterns to extract drinking windows:

```python
patterns = [
    r'drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
    r'drinking window[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
    r'best[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
    r'cellar until[:\s]+(\d{4})',
    # ... more patterns
]
```

### Caching System

The service includes an in-memory cache to avoid re-scraping the same wines:

```python
cache_key = f"{wine_name}_{vintage}".lower().replace(' ', '_')
if cache_key in self.cache:
    return self.cache[cache_key]
```

### Rate Limiting

Respectful scraping with 1-second delays between sources:

```python
time.sleep(1)
```

## Usage Examples

### Basic Usage

```python
from drinking_window_service import DrinkingWindowService

service = DrinkingWindowService()
result = service.get_drinking_window(
    wine_name="Chateau Lafite Rothschild",
    vintage=2020,
    grape_varietal="Cabernet Sauvignon",
    country="France",
    region="Bordeaux",
    color="Red"
)

print(f"Drinking Window: {result['drinking_window']}")
print(f"Peak Year: {result['peak_year']}")
print(f"Confidence: {result['confidence']}")
print(f"Source: {result['source']}")
```

### Integration with Flask App

The service is automatically integrated into the wine submission process:

```python
# In app.py
window_data = drinking_window_service.get_drinking_window(
    wine_name=wine_name,
    vintage=vintage,
    grape_varietal=wine_data.get('grape_varietal'),
    country=wine_data.get('country'),
    region=wine_data.get('region'),
    color=wine_data.get('color')
)

# Update wine with enhanced drinking window info
wine.drinking_window = window_data.get('drinking_window')
wine.drinking_window_confidence = window_data.get('confidence')
wine.drinking_window_source = window_data.get('source')
wine.peak_drinking_year = window_data.get('peak_year')
wine.window_notes = window_data.get('notes')
```

## Error Handling

The service includes comprehensive error handling:
- Network timeouts for web scraping
- Graceful fallback when sources are unavailable
- Pattern matching failures
- Invalid date ranges

All errors are caught and logged, allowing the system to continue with the next source or fallback rules.

## Performance Considerations

- **Caching**: Prevents redundant API calls for the same wine
- **Timeouts**: 15-second timeout per source prevents hanging
- **Rate Limiting**: Respectful 1-second delays between sources
- **Early Termination**: Stops searching once high-confidence data is found

## Future Enhancements

Potential improvements for the service:
1. **Persistent Caching**: Store results in database to avoid re-scraping
2. **API Integration**: Direct API access where available
3. **Machine Learning**: Train models on historical drinking window data
4. **User Feedback**: Allow users to rate drinking window accuracy
5. **Vintage Scoring**: Consider vintage quality in calculations
6. **Professional Subscriptions**: Access to premium wine databases

## Troubleshooting

### Common Issues

**Service returns only fallback rules**
- Check internet connectivity
- Verify target websites are accessible
- Consider that some sites may block automated access

**Peak year not calculated**
- Ensure drinking window format is "YYYY-YYYY"
- Check `_calculate_peak_year` method

**Low confidence ratings**
- This is expected for generic wines or when specific data isn't found
- The fallback rules still provide reasonable estimates

### Testing

Use the provided test script to verify functionality:

```bash
python3 test_drinking_window.py
```

This will test the service with various wine types and display results with confidence levels and sources.