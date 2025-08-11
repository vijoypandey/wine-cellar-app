import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
import time

class WineScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_wine_data(self, wine_name: str, vintage: int) -> Dict:
        """Search for wine data from multiple sources"""
        wine_data = {
            'drinking_window': None,
            'color': None,
            'country': None,
            'region': None,
            'grape_varietal': None,
            'ratings': []
        }
        
        # Try multiple search approaches
        search_queries = [
            f"{wine_name} {vintage} wine",
            f"{wine_name} {vintage} tasting notes",
            f'"{wine_name}" {vintage} wine review'
        ]
        
        for query in search_queries:
            try:
                results = self._search_web(query)
                if results:
                    wine_data.update(results)
                    break
            except Exception as e:
                print(f"Search failed for '{query}': {e}")
                continue
                
        return wine_data

    def _search_web(self, query: str) -> Optional[Dict]:
        """Search web for wine information"""
        try:
            # Use a wine database search (simplified approach)
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract information from search results
            text_content = soup.get_text().lower()
            
            # Simple pattern matching for wine characteristics
            wine_info = {}
            
            # Color detection
            if any(word in text_content for word in ['red wine', 'cabernet', 'merlot', 'pinot noir', 'syrah', 'shiraz']):
                wine_info['color'] = 'Red'
            elif any(word in text_content for word in ['white wine', 'chardonnay', 'sauvignon blanc', 'riesling', 'pinot grigio']):
                wine_info['color'] = 'White'
            
            # Region detection (simplified)
            regions = {
                'napa': ('USA', 'Napa Valley'),
                'sonoma': ('USA', 'Sonoma'),
                'bordeaux': ('France', 'Bordeaux'),
                'burgundy': ('France', 'Burgundy'),
                'champagne': ('France', 'Champagne'),
                'tuscany': ('Italy', 'Tuscany'),
                'chianti': ('Italy', 'Chianti'),
                'rioja': ('Spain', 'Rioja'),
                'mendoza': ('Argentina', 'Mendoza'),
                'barossa': ('Australia', 'Barossa Valley')
            }
            
            for region_key, (country, region) in regions.items():
                if region_key in text_content:
                    wine_info['country'] = country
                    wine_info['region'] = region
                    break
            
            # Grape varietal detection
            varietals = ['cabernet sauvignon', 'merlot', 'pinot noir', 'chardonnay', 
                        'sauvignon blanc', 'riesling', 'syrah', 'shiraz', 'sangiovese']
            
            for varietal in varietals:
                if varietal in text_content:
                    wine_info['grape_varietal'] = varietal.title()
                    break
            
            # Drinking window (simplified pattern matching)
            drink_patterns = [
                r'drink (\d{4})-(\d{4})',
                r'drinking window (\d{4})-(\d{4})',
                r'best (\d{4})-(\d{4})'
            ]
            
            for pattern in drink_patterns:
                match = re.search(pattern, text_content)
                if match:
                    wine_info['drinking_window'] = f"{match.group(1)}-{match.group(2)}"
                    break
            
            return wine_info
            
        except Exception as e:
            print(f"Web search error: {e}")
            return None

    def get_mock_wine_data(self, wine_name: str, vintage: int) -> Dict:
        """Fallback method with mock data for demonstration"""
        mock_data = {
            'drinking_window': f"{vintage + 2}-{vintage + 15}",
            'color': 'Red' if any(word in wine_name.lower() for word in ['cabernet', 'merlot', 'pinot noir']) else 'White',
            'country': 'France',
            'region': 'Bordeaux',
            'grape_varietal': 'Cabernet Sauvignon',
            'ratings': [
                {'source': 'Wine Spectator', 'rating': 92, 'max_rating': 100},
                {'source': 'Robert Parker', 'rating': 94, 'max_rating': 100}
            ]
        }
        return mock_data