#!/usr/bin/env python3
"""
Test script for the enhanced drinking window service
"""

from drinking_window_service import DrinkingWindowService

def test_service():
    service = DrinkingWindowService()
    
    test_cases = [
        # Bordeaux First Growth
        ("Chateau Lafite Rothschild", 2020, "Cabernet Sauvignon", "France", "Bordeaux", "Red"),
        
        # California Cabernet
        ("Caymus Cabernet Sauvignon", 2021, "Cabernet Sauvignon", "USA", "Napa Valley", "Red"),
        
        # Champagne
        ("Dom Perignon", 2014, "Chardonnay", "France", "Champagne", "White"),
        
        # Burgundy
        ("Domaine de la Cote Pinot Noir", 2020, "Pinot Noir", "France", "Burgundy", "Red"),
        
        # Italian Barolo
        ("Barolo Brunate", 2018, "Nebbiolo", "Italy", "Piedmont", "Red"),
        
        # German Riesling
        ("Dr. Loosen Riesling", 2022, "Riesling", "Germany", "Mosel", "White"),
    ]
    
    print("=== Testing Enhanced Drinking Window Service ===\n")
    
    for wine_name, vintage, grape, country, region, color in test_cases:
        print(f"Wine: {wine_name} {vintage}")
        print(f"Details: {grape}, {country} - {region}, {color}")
        
        result = service.get_drinking_window(
            wine_name=wine_name,
            vintage=vintage,
            grape_varietal=grape,
            country=country,
            region=region,
            color=color
        )
        
        print(f"Drinking Window: {result['drinking_window']}")
        print(f"Peak Year: {result.get('peak_year', 'N/A')}")
        print(f"Confidence: {result['confidence']}")
        print(f"Source: {result['source']}")
        print(f"Notes: {result['notes']}")
        print("-" * 60)
        print()

if __name__ == "__main__":
    test_service()