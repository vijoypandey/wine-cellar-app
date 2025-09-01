#!/usr/bin/env python3
"""
Comprehensive Drinking Window Service
Implements multi-source lookup for accurate wine drinking windows
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Tuple
import time
import urllib.parse
import json
from datetime import datetime

class DrinkingWindowService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Source priority order - high accuracy specific sources first
        self.sources = [
            'cellartracker',
            'wine_searcher', 
            'erobertparker',
            'vinous',
            'jancisrobinson',
            'vivino',
            'wine_com',
            'decanter',
            'wine_spectator'
        ]
        
        # Cache to avoid re-scraping
        self.cache = {}
        
    def get_drinking_window(self, wine_name: str, vintage: int, grape_varietal: str = None, 
                          country: str = None, region: str = None, color: str = None) -> Dict:
        """
        Get drinking window with confidence score and source attribution
        Returns: {
            'drinking_window': 'YYYY-YYYY',
            'peak_year': YYYY,
            'confidence': 'high|medium|low', 
            'source': 'source_name',
            'notes': 'additional info'
        }
        """
        cache_key = f"{wine_name}_{vintage}".lower().replace(' ', '_')
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try sources in priority order
        for source in self.sources:
            try:
                result = self._scrape_source(source, wine_name, vintage, grape_varietal, country, region, color)
                if result and result.get('drinking_window'):
                    # Add peak year calculation
                    peak_year = self._calculate_peak_year(result['drinking_window'])
                    if peak_year:
                        result['peak_year'] = peak_year
                    self.cache[cache_key] = result
                    return result
                
                # Rate limit between sources
                time.sleep(1)
                
            except Exception as e:
                print(f"Error scraping {source}: {e}")
                continue
        
        # Fallback to rule-based estimation
        fallback = self._get_fallback_window(wine_name, vintage, grape_varietal, country, region, color)
        # Add peak year to fallback
        peak_year = self._calculate_peak_year(fallback['drinking_window'])
        if peak_year:
            fallback['peak_year'] = peak_year
        self.cache[cache_key] = fallback
        return fallback
    
    def _scrape_source(self, source: str, wine_name: str, vintage: int, grape_varietal: str, 
                      country: str, region: str, color: str) -> Optional[Dict]:
        """Route to specific source scraper"""
        scrapers = {
            'cellartracker': self._scrape_cellartracker,
            'wine_searcher': self._scrape_wine_searcher,
            'erobertparker': self._scrape_erobertparker,
            'vinous': self._scrape_vinous,
            'jancisrobinson': self._scrape_jancisrobinson,
            'vivino': self._scrape_vivino,
            'wine_com': self._scrape_wine_com,
            'decanter': self._scrape_decanter,
            'wine_spectator': self._scrape_wine_spectator
        }
        
        scraper = scrapers.get(source)
        if scraper:
            return scraper(wine_name, vintage, grape_varietal, country, region, color)
        return None
    
    def _scrape_cellartracker(self, wine_name: str, vintage: int, grape_varietal: str, 
                             country: str, region: str, color: str) -> Optional[Dict]:
        """Scrape CellarTracker.com for crowd-sourced drinking windows"""
        try:
            # CellarTracker search URL
            query = f"{wine_name} {vintage}"
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.cellartracker.com/list.asp?Table=List&iUserOverride=0&szSearch={encoded_query}"
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for drinking window patterns in text
            text_content = soup.get_text().lower()
            
            # CellarTracker specific patterns
            patterns = [
                r'drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'drinking window[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'mature[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'best[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'cellar until[:\s]+(\d{4})',
                r'drink from[:\s]+(\d{4})',
                r'ready[:\s]+(\d{4})\s*[-–]\s*(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_content)
                if match:
                    if match.lastindex == 2:  # Range
                        start, end = int(match.group(1)), int(match.group(2))
                        return {
                            'drinking_window': f"{start}-{end}",
                            'confidence': 'high',
                            'source': 'CellarTracker',
                            'notes': 'Crowd-sourced collector data'
                        }
                    else:  # Single year - create range
                        start_year = int(match.group(1))
                        return {
                            'drinking_window': f"{start_year}-{start_year + 8}",
                            'confidence': 'medium',
                            'source': 'CellarTracker',
                            'notes': 'Estimated range from single year'
                        }
            
            return None
            
        except Exception as e:
            print(f"CellarTracker scraping error: {e}")
            return None
    
    def _scrape_wine_searcher(self, wine_name: str, vintage: int, grape_varietal: str,
                             country: str, region: str, color: str) -> Optional[Dict]:
        """Scrape Wine-Searcher.com for professional aggregated data"""
        try:
            query = f"{wine_name} {vintage}"
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.wine-searcher.com/find/{encoded_query}"
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Wine-Searcher specific patterns
            patterns = [
                r'drinking window[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'best consumed[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'cellar until[:\s]+(\d{4})',
                r'ready to drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_content)
                if match:
                    if match.lastindex == 2:
                        start, end = int(match.group(1)), int(match.group(2))
                        return {
                            'drinking_window': f"{start}-{end}",
                            'confidence': 'high',
                            'source': 'Wine-Searcher',
                            'notes': 'Professional aggregated data'
                        }
            
            return None
            
        except Exception as e:
            print(f"Wine-Searcher scraping error: {e}")
            return None
    
    def _scrape_erobertparker(self, wine_name: str, vintage: int, grape_varietal: str,
                             country: str, region: str, color: str) -> Optional[Dict]:
        """Scrape eRobertParker.com for Wine Advocate critic reviews"""
        try:
            # Search via Google for Parker reviews
            query = f'"{wine_name}" {vintage} site:erobertparker.com'
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Parker-style drinking window patterns
            patterns = [
                r'drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'anticipated maturity[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'cellar for[:\s]+(\d+)\s*years',
                r'ready in[:\s]+(\d+)\s*years',
                r'best[:\s]+(\d{4})\s*[-–]\s*(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_content)
                if match:
                    if 'years' in pattern:  # Convert years to date range
                        years_from_vintage = int(match.group(1))
                        start = vintage + max(1, years_from_vintage - 2)
                        end = vintage + years_from_vintage + 8
                        return {
                            'drinking_window': f"{start}-{end}",
                            'confidence': 'high',
                            'source': 'Robert Parker Wine Advocate',
                            'notes': 'Professional critic assessment'
                        }
                    elif match.lastindex == 2:
                        start, end = int(match.group(1)), int(match.group(2))
                        return {
                            'drinking_window': f"{start}-{end}",
                            'confidence': 'high',
                            'source': 'Robert Parker Wine Advocate',
                            'notes': 'Professional critic assessment'
                        }
            
            return None
            
        except Exception as e:
            print(f"eRobertParker scraping error: {e}")
            return None
    
    def _scrape_vinous(self, wine_name: str, vintage: int, grape_varietal: str,
                      country: str, region: str, color: str) -> Optional[Dict]:
        """Scrape Vinous.com for professional wine reviews"""
        try:
            query = f'"{wine_name}" {vintage} site:vinous.com'
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Vinous-style patterns
            patterns = [
                r'drinking window[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'best from[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'cellar[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'ready[:\s]+(\d{4})\s*[-–]\s*(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_content)
                if match:
                    start, end = int(match.group(1)), int(match.group(2))
                    return {
                        'drinking_window': f"{start}-{end}",
                        'confidence': 'high',
                        'source': 'Vinous',
                        'notes': 'Professional wine critic review'
                    }
            
            return None
            
        except Exception as e:
            print(f"Vinous scraping error: {e}")
            return None
    
    def _scrape_jancisrobinson(self, wine_name: str, vintage: int, grape_varietal: str,
                              country: str, region: str, color: str) -> Optional[Dict]:
        """Scrape JancisRobinson.com for MW tasting notes"""
        try:
            query = f'"{wine_name}" {vintage} site:jancisrobinson.com'
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Jancis Robinson style patterns
            patterns = [
                r'drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'drinking window[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'best[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'mature[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'cellar until[:\s]+(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_content)
                if match:
                    if match.lastindex == 2:
                        start, end = int(match.group(1)), int(match.group(2))
                        return {
                            'drinking_window': f"{start}-{end}",
                            'confidence': 'high',
                            'source': 'Jancis Robinson',
                            'notes': 'Master of Wine assessment'
                        }
                    else:
                        end_year = int(match.group(1))
                        start_year = max(vintage + 1, end_year - 10)
                        return {
                            'drinking_window': f"{start_year}-{end_year}",
                            'confidence': 'medium',
                            'source': 'Jancis Robinson',
                            'notes': 'Estimated from cellar until date'
                        }
            
            return None
            
        except Exception as e:
            print(f"Jancis Robinson scraping error: {e}")
            return None
    
    def _scrape_vivino(self, wine_name: str, vintage: int, grape_varietal: str,
                      country: str, region: str, color: str) -> Optional[Dict]:
        """Scrape Vivino.com for user reviews and drinking suggestions"""
        try:
            query = f"{wine_name} {vintage}"
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.vivino.com/search/wines?q={encoded_query}"
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Vivino patterns
            patterns = [
                r'drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'best[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'drinking window[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'ready[:\s]+(\d{4})\s*[-–]\s*(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_content)
                if match:
                    start, end = int(match.group(1)), int(match.group(2))
                    return {
                        'drinking_window': f"{start}-{end}",
                        'confidence': 'medium',
                        'source': 'Vivino',
                        'notes': 'User community data'
                    }
            
            return None
            
        except Exception as e:
            print(f"Vivino scraping error: {e}")
            return None
    
    def _scrape_wine_com(self, wine_name: str, vintage: int, grape_varietal: str,
                        country: str, region: str, color: str) -> Optional[Dict]:
        """Scrape Wine.com for producer-provided drinking windows"""
        try:
            query = f"{wine_name} {vintage}"
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.wine.com/search/{encoded_query}"
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Wine.com patterns
            patterns = [
                r'drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'drinking window[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'best consumed[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'cellaring potential[:\s]+(\d+)\s*years'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_content)
                if match:
                    if 'years' in pattern:
                        years = int(match.group(1))
                        start = vintage + 2
                        end = vintage + years
                        return {
                            'drinking_window': f"{start}-{end}",
                            'confidence': 'medium',
                            'source': 'Wine.com',
                            'notes': 'Producer-provided cellaring info'
                        }
                    else:
                        start, end = int(match.group(1)), int(match.group(2))
                        return {
                            'drinking_window': f"{start}-{end}",
                            'confidence': 'medium',
                            'source': 'Wine.com',
                            'notes': 'Commercial wine data'
                        }
            
            return None
            
        except Exception as e:
            print(f"Wine.com scraping error: {e}")
            return None
    
    def _scrape_decanter(self, wine_name: str, vintage: int, grape_varietal: str,
                        country: str, region: str, color: str) -> Optional[Dict]:
        """Scrape Decanter.com for professional drinking windows"""
        try:
            query = f'"{wine_name}" {vintage} site:decanter.com'
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Decanter patterns
            patterns = [
                r'drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'drinking window[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'best[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'cellar until[:\s]+(\d{4})',
                r'ready[:\s]+(\d{4})\s*[-–]\s*(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_content)
                if match:
                    if match.lastindex == 2:
                        start, end = int(match.group(1)), int(match.group(2))
                        return {
                            'drinking_window': f"{start}-{end}",
                            'confidence': 'medium',
                            'source': 'Decanter',
                            'notes': 'Wine magazine professional review'
                        }
            
            return None
            
        except Exception as e:
            print(f"Decanter scraping error: {e}")
            return None
    
    def _scrape_wine_spectator(self, wine_name: str, vintage: int, grape_varietal: str,
                              country: str, region: str, color: str) -> Optional[Dict]:
        """Scrape Wine Spectator for professional ratings and drinking windows"""
        try:
            query = f'"{wine_name}" {vintage} site:winespectator.com'
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Wine Spectator patterns
            patterns = [
                r'drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'drinking window[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'best[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'cellar until[:\s]+(\d{4})',
                r'ready[:\s]+(\d{4})\s*[-–]\s*(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_content)
                if match:
                    if match.lastindex == 2:
                        start, end = int(match.group(1)), int(match.group(2))
                        return {
                            'drinking_window': f"{start}-{end}",
                            'confidence': 'medium',
                            'source': 'Wine Spectator',
                            'notes': 'Professional wine magazine rating'
                        }
            
            return None
            
        except Exception as e:
            print(f"Wine Spectator scraping error: {e}")
            return None
    
    def _scrape_erobertparker(self, wine_name: str, vintage: int, grape_varietal: str,
                             country: str, region: str, color: str) -> Optional[Dict]:
        """Scrape eRobertParker.com for Wine Advocate critic reviews"""
        try:
            # Search via Google for Parker reviews
            query = f'"{wine_name}" {vintage} site:erobertparker.com'
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Parker-style drinking window patterns
            patterns = [
                r'drink[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'anticipated maturity[:\s]+(\d{4})\s*[-–]\s*(\d{4})',
                r'cellar for[:\s]+(\d+)\s*years',
                r'ready in[:\s]+(\d+)\s*years',
                r'best[:\s]+(\d{4})\s*[-–]\s*(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_content)
                if match:
                    if 'years' in pattern:  # Convert years to date range
                        years_from_vintage = int(match.group(1))
                        start = vintage + max(1, years_from_vintage - 2)
                        end = vintage + years_from_vintage + 8
                        return {
                            'drinking_window': f"{start}-{end}",
                            'confidence': 'high',
                            'source': 'Robert Parker Wine Advocate',
                            'notes': 'Professional critic assessment'
                        }
                    elif match.lastindex == 2:
                        start, end = int(match.group(1)), int(match.group(2))
                        return {
                            'drinking_window': f"{start}-{end}",
                            'confidence': 'high',
                            'source': 'Robert Parker Wine Advocate',
                            'notes': 'Professional critic assessment'
                        }
            
            return None
            
        except Exception as e:
            print(f"eRobertParker scraping error: {e}")
            return None
    
    def _get_fallback_window(self, wine_name: str, vintage: int, grape_varietal: str,
                           country: str, region: str, color: str) -> Dict:
        """Comprehensive fallback rule engine based on wine characteristics"""
        
        wine_name_lower = wine_name.lower() if wine_name else ""
        grape_lower = grape_varietal.lower() if grape_varietal else ""
        region_lower = region.lower() if region else ""
        country_lower = country.lower() if country else ""
        
        # Bordeaux First Growths - exceptional longevity
        if any(name in wine_name_lower for name in [
            'lafite', 'latour', 'margaux', 'mouton', 'haut-brion'
        ]):
            return {
                'drinking_window': f"{vintage + 8}-{vintage + 40}",
                'confidence': 'medium',
                'source': 'Fallback Rules',
                'notes': 'Bordeaux First Growth estimate'
            }
        
        # Bordeaux Châteaux general
        if wine_name_lower.startswith(('chateau', 'château')) or 'bordeaux' in region_lower:
            if 'saint-emilion' in wine_name_lower or 'pomerol' in wine_name_lower:
                return {
                    'drinking_window': f"{vintage + 3}-{vintage + 20}",
                    'confidence': 'medium',
                    'source': 'Fallback Rules',
                    'notes': 'Right Bank Bordeaux estimate'
                }
            else:
                return {
                    'drinking_window': f"{vintage + 5}-{vintage + 25}",
                    'confidence': 'medium',
                    'source': 'Fallback Rules',
                    'notes': 'Left Bank Bordeaux estimate'
                }
        
        # Burgundy
        if 'domaine' in wine_name_lower and ('burgundy' in region_lower or 'bourgogne' in wine_name_lower):
            if color == 'Red':
                return {
                    'drinking_window': f"{vintage + 3}-{vintage + 15}",
                    'confidence': 'medium',
                    'source': 'Fallback Rules',
                    'notes': 'Burgundy red wine estimate'
                }
            else:
                return {
                    'drinking_window': f"{vintage + 1}-{vintage + 8}",
                    'confidence': 'medium',
                    'source': 'Fallback Rules',
                    'notes': 'Burgundy white wine estimate'
                }
        
        # Champagne
        if 'champagne' in region_lower or 'champagne' in wine_name_lower:
            return {
                'drinking_window': f"{vintage + 3}-{vintage + 15}",
                'confidence': 'medium',
                'source': 'Fallback Rules',
                'notes': 'Champagne estimate'
            }
        
        # Italian wines
        if country_lower == 'italy':
            if 'barolo' in wine_name_lower or 'barbaresco' in wine_name_lower:
                return {
                    'drinking_window': f"{vintage + 5}-{vintage + 25}",
                    'confidence': 'medium',
                    'source': 'Fallback Rules',
                    'notes': 'Nebbiolo-based wine estimate'
                }
            elif 'brunello' in wine_name_lower:
                return {
                    'drinking_window': f"{vintage + 4}-{vintage + 20}",
                    'confidence': 'medium',
                    'source': 'Fallback Rules',
                    'notes': 'Brunello di Montalcino estimate'
                }
            elif 'chianti classico' in wine_name_lower:
                return {
                    'drinking_window': f"{vintage + 2}-{vintage + 12}",
                    'confidence': 'medium',
                    'source': 'Fallback Rules',
                    'notes': 'Chianti Classico estimate'
                }
        
        # Grape varietal-based rules
        if grape_lower:
            if 'cabernet sauvignon' in grape_lower:
                if country_lower == 'usa':
                    return {
                        'drinking_window': f"{vintage + 3}-{vintage + 15}",
                        'confidence': 'low',
                        'source': 'Fallback Rules',
                        'notes': 'US Cabernet Sauvignon estimate'
                    }
                else:
                    return {
                        'drinking_window': f"{vintage + 4}-{vintage + 18}",
                        'confidence': 'low',
                        'source': 'Fallback Rules',
                        'notes': 'Cabernet Sauvignon general estimate'
                    }
            
            elif 'pinot noir' in grape_lower:
                return {
                    'drinking_window': f"{vintage + 2}-{vintage + 10}",
                    'confidence': 'low',
                    'source': 'Fallback Rules',
                    'notes': 'Pinot Noir estimate'
                }
            
            elif 'merlot' in grape_lower:
                return {
                    'drinking_window': f"{vintage + 2}-{vintage + 12}",
                    'confidence': 'low',
                    'source': 'Fallback Rules',
                    'notes': 'Merlot estimate'
                }
            
            elif 'syrah' in grape_lower or 'shiraz' in grape_lower:
                return {
                    'drinking_window': f"{vintage + 3}-{vintage + 15}",
                    'confidence': 'low',
                    'source': 'Fallback Rules',
                    'notes': 'Syrah/Shiraz estimate'
                }
            
            elif 'chardonnay' in grape_lower:
                if 'chablis' in wine_name_lower:
                    return {
                        'drinking_window': f"{vintage + 1}-{vintage + 8}",
                        'confidence': 'low',
                        'source': 'Fallback Rules',
                        'notes': 'Chablis Chardonnay estimate'
                    }
                else:
                    return {
                        'drinking_window': f"{vintage + 1}-{vintage + 6}",
                        'confidence': 'low',
                        'source': 'Fallback Rules',
                        'notes': 'Chardonnay general estimate'
                    }
            
            elif 'sauvignon blanc' in grape_lower:
                return {
                    'drinking_window': f"{vintage}-{vintage + 4}",
                    'confidence': 'low',
                    'source': 'Fallback Rules',
                    'notes': 'Sauvignon Blanc estimate'
                }
            
            elif 'riesling' in grape_lower:
                return {
                    'drinking_window': f"{vintage + 1}-{vintage + 12}",
                    'confidence': 'low',
                    'source': 'Fallback Rules',
                    'notes': 'Riesling estimate'
                }
        
        # Basic color-based fallback
        if color == 'Red':
            return {
                'drinking_window': f"{vintage + 2}-{vintage + 12}",
                'confidence': 'low',
                'source': 'Fallback Rules',
                'notes': 'Generic red wine estimate'
            }
        elif color == 'White':
            return {
                'drinking_window': f"{vintage}-{vintage + 5}",
                'confidence': 'low',
                'source': 'Fallback Rules',
                'notes': 'Generic white wine estimate'
            }
        
        # Ultimate fallback
        return {
            'drinking_window': f"{vintage + 1}-{vintage + 8}",
            'confidence': 'low',
            'source': 'Fallback Rules',
            'notes': 'Generic wine estimate'
        }
    
    def _calculate_peak_year(self, drinking_window: str) -> Optional[int]:
        """Calculate peak drinking year from window range"""
        try:
            if '-' in drinking_window:
                start, end = map(int, drinking_window.split('-'))
                # Peak is typically in first third of drinking window
                peak = start + (end - start) // 3
                return peak
        except:
            pass
        return None

# Test the service
if __name__ == "__main__":
    service = DrinkingWindowService()
    
    test_wines = [
        ("Chateau Lafite Rothschild", 2020),
        ("Caymus Cabernet Sauvignon", 2021),
        ("Dom Perignon", 2014),
        ("Screaming Eagle", 2019),
        ("Opus One", 2018)
    ]
    
    for wine_name, vintage in test_wines:
        print(f"\n--- Testing: {wine_name} {vintage} ---")
        result = service.get_drinking_window(wine_name, vintage)
        for key, value in result.items():
            print(f"{key}: {value}")
        print("---")