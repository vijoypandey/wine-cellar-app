#!/usr/bin/env python3
"""
Wine scraper that searches trusted wine sources for accurate information
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
import time
import urllib.parse

class TrustedWineScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Trusted wine sources
        self.trusted_sources = [
            'site:thewinegate.com',
            'site:decanter.com',
            'site:winespectator.com',
            'site:jancisrobinson.com',
            'site:robertparker.com',
            'site:wine.com',
            'site:vivino.com'
        ]
    
    def search_wine_data(self, wine_name: str, vintage: int) -> Dict:
        """Search trusted sources for wine information"""
        wine_data = {
            'drinking_window': None,
            'color': None,
            'country': None,
            'region': None,
            'grape_varietal': None,
            'ratings': []
        }
        
        # Try searching trusted sources
        for source in self.trusted_sources:
            try:
                result = self._search_trusted_source(wine_name, vintage, source)
                if result:
                    # Merge results, keeping non-None values
                    for key, value in result.items():
                        if value and not wine_data.get(key):
                            wine_data[key] = value
                    
                    # If we have sufficient data, stop searching
                    if self._has_sufficient_data(wine_data):
                        break
                        
                # Rate limit to be respectful
                time.sleep(1)
                
            except Exception as e:
                print(f"Failed to search {source}: {e}")
                continue
        
        # If we still don't have basic info, use educated guessing as fallback
        if not self._has_sufficient_data(wine_data):
            fallback = self._get_educated_guess(wine_name, vintage)
            for key, value in fallback.items():
                if value and not wine_data.get(key):
                    wine_data[key] = value
        
        return wine_data
    
    def _search_trusted_source(self, wine_name: str, vintage: int, source: str) -> Optional[Dict]:
        """Search a specific trusted source"""
        try:
            # Create search query
            query = f'"{wine_name}" {vintage} {source}'
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Extract wine information from search results
            wine_info = {}
            
            # Color detection - look for specific phrases
            color_patterns = {
                'red wine': 'Red',
                'red bordeaux': 'Red',
                'cabernet sauvignon': 'Red',
                'merlot': 'Red',
                'pinot noir': 'Red',
                'syrah': 'Red',
                'shiraz': 'Red',
                'tempranillo': 'Red',
                'sangiovese': 'Red',
                'white wine': 'White',
                'chardonnay': 'White',
                'sauvignon blanc': 'White',
                'riesling': 'White',
                'pinot grigio': 'White',
                'gewürztraminer': 'White',
                'champagne': 'White',
                'sparkling': 'White'
            }
            
            for pattern, color in color_patterns.items():
                if pattern in text_content:
                    wine_info['color'] = color
                    break
            
            # Region detection with more specific patterns
            region_patterns = [
                # French regions
                (r'bordeaux', ('France', 'Bordeaux')),
                (r'burgundy', ('France', 'Burgundy')),
                (r'champagne', ('France', 'Champagne')),
                (r'rhône|rhone', ('France', 'Rhône Valley')),
                (r'loire', ('France', 'Loire Valley')),
                (r'alsace', ('France', 'Alsace')),
                (r'languedoc', ('France', 'Languedoc')),
                
                # California regions
                (r'napa valley', ('USA', 'Napa Valley')),
                (r'sonoma', ('USA', 'Sonoma County')),
                (r'alexander valley', ('USA', 'Alexander Valley')),
                (r'russian river', ('USA', 'Russian River Valley')),
                (r'santa barbara', ('USA', 'Santa Barbara County')),
                (r'paso robles', ('USA', 'Paso Robles')),
                
                # Italian regions  
                (r'tuscany|toscana', ('Italy', 'Tuscany')),
                (r'piedmont|piemonte', ('Italy', 'Piedmont')),
                (r'veneto', ('Italy', 'Veneto')),
                (r'chianti', ('Italy', 'Chianti')),
                
                # Spanish regions
                (r'rioja', ('Spain', 'Rioja')),
                (r'ribera del duero', ('Spain', 'Ribera del Duero')),
                
                # German regions
                (r'mosel', ('Germany', 'Mosel')),
                (r'rheingau', ('Germany', 'Rheingau')),
                
                # Australian regions
                (r'barossa', ('Australia', 'Barossa Valley')),
                (r'hunter valley', ('Australia', 'Hunter Valley')),
                (r'margaret river', ('Australia', 'Margaret River')),
                
                # Other regions
                (r'mendoza', ('Argentina', 'Mendoza')),
                (r'maipo', ('Chile', 'Maipo Valley')),
                (r'stellenbosch', ('South Africa', 'Stellenbosch')),
            ]
            
            for pattern, (country, region) in region_patterns:
                if re.search(pattern, text_content):
                    wine_info['country'] = country
                    wine_info['region'] = region
                    break
            
            # Grape varietal detection
            varietal_patterns = {
                'cabernet sauvignon': 'Cabernet Sauvignon',
                'merlot': 'Merlot',
                'pinot noir': 'Pinot Noir',
                'syrah': 'Syrah',
                'shiraz': 'Shiraz',
                'chardonnay': 'Chardonnay',
                'sauvignon blanc': 'Sauvignon Blanc',
                'riesling': 'Riesling',
                'pinot grigio': 'Pinot Grigio',
                'sangiovese': 'Sangiovese',
                'tempranillo': 'Tempranillo',
                'nebbiolo': 'Nebbiolo',
                'grenache': 'Grenache',
                'bordeaux blend': 'Bordeaux Blend'
            }
            
            for varietal, formal_name in varietal_patterns.items():
                if varietal in text_content:
                    wine_info['grape_varietal'] = formal_name
                    break
            
            # Drinking window detection
            drink_patterns = [
                r'drink (\d{4})[- ]?(?:to )?(\d{4})',
                r'drinking window[:\s]+(\d{4})[- ]?(?:to )?(\d{4})',
                r'cellar until (\d{4})',
                r'best (\d{4})[- ]?(?:to )?(\d{4})',
                r'mature (\d{4})[- ]?(\d{4})'
            ]
            
            for pattern in drink_patterns:
                match = re.search(pattern, text_content)
                if match:
                    if match.lastindex == 2:  # Two groups (range)
                        wine_info['drinking_window'] = f"{match.group(1)}-{match.group(2)}"
                    else:  # One group (single year)
                        start_year = int(match.group(1))
                        wine_info['drinking_window'] = f"{start_year}-{start_year + 10}"
                    break
            
            return wine_info if wine_info else None
            
        except Exception as e:
            print(f"Error searching {source}: {e}")
            return None
    
    def _has_sufficient_data(self, data: Dict) -> bool:
        """Check if we have enough useful data"""
        return bool(data.get('color') and (data.get('country') or data.get('grape_varietal')))
    
    def _get_educated_guess(self, wine_name: str, vintage: int) -> Dict:
        """Fallback educated guessing based on wine name"""
        wine_name_lower = wine_name.lower()
        result = {}
        
        # Château detection for Bordeaux
        if wine_name_lower.startswith('chateau') or wine_name_lower.startswith('château'):
            result.update({
                'country': 'France',
                'region': 'Bordeaux',
                'color': 'Red',
                'grape_varietal': 'Bordeaux Blend',
                'drinking_window': f"{vintage + 3}-{vintage + 20}"
            })
        
        # Domaine detection for Burgundy
        elif 'domaine' in wine_name_lower and any(word in wine_name_lower for word in ['burgundy', 'bourgogne', 'chablis']):
            result.update({
                'country': 'France',
                'region': 'Burgundy',
                'drinking_window': f"{vintage + 2}-{vintage + 12}"
            })
        
        # Basic varietal detection
        elif any(red_grape in wine_name_lower for red_grape in ['cabernet', 'merlot', 'pinot noir', 'syrah', 'shiraz']):
            result.update({
                'color': 'Red',
                'drinking_window': f"{vintage + 2}-{vintage + 12}"
            })
        
        elif any(white_grape in wine_name_lower for white_grape in ['chardonnay', 'sauvignon blanc', 'riesling']):
            result.update({
                'color': 'White', 
                'drinking_window': f"{vintage}-{vintage + 6}"
            })
        
        return result

# Test the scraper
if __name__ == "__main__":
    scraper = TrustedWineScraper()
    
    test_wines = [
        ("Chateau Pontet-Canet", 2020),
        ("Caymus Cabernet Sauvignon", 2021),
        ("Dom Perignon", 2014)
    ]
    
    for wine_name, vintage in test_wines:
        print(f"\n--- Testing: {wine_name} {vintage} ---")
        result = scraper.search_wine_data(wine_name, vintage)
        for key, value in result.items():
            if value:
                print(f"{key}: {value}")
        print("---")