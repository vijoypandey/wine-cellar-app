#!/usr/bin/env python3
"""
Demo data script to populate the wine cellar database with sample entries
"""

from app import app, db
from models import Wine, Store, WineRating

def create_demo_data():
    """Create sample wine entries for demonstration"""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create sample stores
        stores_data = [
            "Wine.com",
            "Total Wine & More", 
            "Local Wine Shop",
            "Costco",
            "BevMo!"
        ]
        
        stores = []
        for store_name in stores_data:
            store = Store(name=store_name)
            db.session.add(store)
            stores.append(store)
        
        db.session.commit()
        
        # Create sample wines
        wines_data = [
            {
                'name': 'Caymus Cabernet Sauvignon',
                'vintage': 2021,
                'price': 89.99,
                'store': stores[0],
                'cellar_name': 'Main Cellar',
                'rack_number': 'A1',
                'color': 'Red',
                'country': 'USA',
                'region': 'Napa Valley',
                'grape_varietal': 'Cabernet Sauvignon',
                'drinking_window': '2024-2035',
                'ratings_summary': 92.5
            },
            {
                'name': 'Kendall-Jackson Vintners Reserve Chardonnay',
                'vintage': 2022,
                'price': 21.99,
                'store': stores[1],
                'cellar_name': 'Main Cellar',
                'rack_number': 'B3',
                'color': 'White',
                'country': 'USA',
                'region': 'California',
                'grape_varietal': 'Chardonnay',
                'drinking_window': '2024-2027',
                'ratings_summary': 88.0
            },
            {
                'name': 'Opus One',
                'vintage': 2019,
                'price': 450.00,
                'store': stores[2],
                'cellar_name': 'Premium Cellar',
                'rack_number': 'P1',
                'color': 'Red',
                'country': 'USA',
                'region': 'Napa Valley',
                'grape_varietal': 'Bordeaux Blend',
                'drinking_window': '2025-2040',
                'ratings_summary': 96.0
            },
            {
                'name': 'Dom Perignon',
                'vintage': 2014,
                'price': 220.00,
                'store': stores[3],
                'cellar_name': 'Champagne Cellar',
                'rack_number': 'C1',
                'color': 'White',
                'country': 'France',
                'region': 'Champagne',
                'grape_varietal': 'Chardonnay & Pinot Noir',
                'drinking_window': '2024-2030',
                'ratings_summary': 94.5
            },
            {
                'name': 'Silver Oak Alexander Valley Cabernet Sauvignon',
                'vintage': 2020,
                'price': 65.00,
                'store': stores[4],
                'cellar_name': 'Main Cellar',
                'rack_number': 'A5',
                'color': 'Red',
                'country': 'USA',
                'region': 'Alexander Valley',
                'grape_varietal': 'Cabernet Sauvignon',
                'drinking_window': '2023-2032',
                'ratings_summary': 90.0
            }
        ]
        
        for wine_data in wines_data:
            wine = Wine(
                name=wine_data['name'],
                vintage=wine_data['vintage'],
                price=wine_data['price'],
                store_id=wine_data['store'].id,
                cellar_name=wine_data['cellar_name'],
                rack_number=wine_data['rack_number'],
                color=wine_data['color'],
                country=wine_data['country'],
                region=wine_data['region'],
                grape_varietal=wine_data['grape_varietal'],
                drinking_window=wine_data['drinking_window'],
                ratings_summary=wine_data['ratings_summary']
            )
            db.session.add(wine)
        
        db.session.commit()
        
        # Add some sample ratings
        wines = Wine.query.all()
        rating_sources = [
            ('Wine Spectator', 100),
            ('Robert Parker', 100), 
            ('Jeb Dunnuck', 100),
            ('Wine Advocate', 100)
        ]
        
        for wine in wines:
            # Add 2-4 ratings per wine
            import random
            num_ratings = random.randint(2, 4)
            used_sources = random.sample(rating_sources, num_ratings)
            
            for source, max_rating in used_sources:
                # Generate rating close to the summary rating
                base_rating = wine.ratings_summary or 85
                rating_value = base_rating + random.uniform(-3, 3)
                rating_value = max(80, min(100, rating_value))  # Keep within bounds
                
                rating = WineRating(
                    wine_id=wine.id,
                    source=source,
                    rating=rating_value,
                    max_rating=max_rating
                )
                db.session.add(rating)
        
        db.session.commit()
        
        print("✅ Demo data created successfully!")
        print(f"Added {len(stores)} stores")
        print(f"Added {len(wines_data)} wines")
        print("Added multiple ratings per wine")

if __name__ == "__main__":
    create_demo_data()