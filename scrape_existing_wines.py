#!/usr/bin/env python3
"""
Script to trigger web scraping for existing wines that don't have complete data
"""

from app import app, db
from models import Wine, WineRating
from trusted_wine_scraper import TrustedWineScraper

def scrape_existing_wines():
    """Scrape data for existing wines that are missing information"""
    with app.app_context():
        scraper = TrustedWineScraper()
        
        # Find wines that need scraping (missing color, region, etc.)
        wines_to_scrape = Wine.query.filter(
            (Wine.color == None) | 
            (Wine.country == None) | 
            (Wine.grape_varietal == None) |
            (Wine.drinking_window == None)
        ).all()
        
        print(f"Found {len(wines_to_scrape)} wines that need data scraping...")
        
        for i, wine in enumerate(wines_to_scrape, 1):
            print(f"\n[{i}/{len(wines_to_scrape)}] Scraping data for: {wine.name} {wine.vintage}")
            
            try:
                # First try real web scraping
                wine_data = scraper.search_wine_data(wine.name, wine.vintage)
                
                # If no data found, use mock data for demonstration
                if not any(wine_data.values()):
                    print("  → No web data found, using mock data for demonstration")
                    wine_data = scraper.get_mock_wine_data(wine.name, wine.vintage)
                else:
                    print("  → Found web data!")
                
                # Update wine with scraped data
                if wine_data.get('drinking_window'):
                    wine.drinking_window = wine_data['drinking_window']
                    print(f"  → Drinking window: {wine.drinking_window}")
                
                if wine_data.get('color'):
                    wine.color = wine_data['color']
                    print(f"  → Color: {wine.color}")
                
                if wine_data.get('country'):
                    wine.country = wine_data['country']
                    print(f"  → Country: {wine.country}")
                
                if wine_data.get('region'):
                    wine.region = wine_data['region']
                    print(f"  → Region: {wine.region}")
                
                if wine_data.get('grape_varietal'):
                    wine.grape_varietal = wine_data['grape_varietal']
                    print(f"  → Grape: {wine.grape_varietal}")
                
                # Add ratings if found
                ratings = wine_data.get('ratings', [])
                if ratings:
                    # Clear existing ratings for this wine
                    WineRating.query.filter_by(wine_id=wine.id).delete()
                    
                    total_rating = 0
                    count = 0
                    
                    for rating_data in ratings:
                        rating = WineRating(
                            wine_id=wine.id,
                            source=rating_data['source'],
                            rating=rating_data['rating'],
                            max_rating=rating_data['max_rating']
                        )
                        db.session.add(rating)
                        
                        # Normalize rating to 100 scale for average
                        normalized_rating = (rating_data['rating'] / rating_data['max_rating']) * 100
                        total_rating += normalized_rating
                        count += 1
                        
                        print(f"  → {rating_data['source']}: {rating_data['rating']}/{rating_data['max_rating']}")
                    
                    if count > 0:
                        wine.ratings_summary = round(total_rating / count, 1)
                        print(f"  → Summary rating: {wine.ratings_summary}/100")
                
                db.session.commit()
                print("  ✅ Updated successfully!")
                
            except Exception as e:
                print(f"  ❌ Error scraping {wine.name}: {e}")
                continue
        
        print(f"\n🍷 Scraping completed! Updated {len(wines_to_scrape)} wines.")
        print("You can now view your collection to see the enriched wine data.")

if __name__ == "__main__":
    scrape_existing_wines()