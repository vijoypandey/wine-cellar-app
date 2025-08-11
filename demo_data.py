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
        
        # Create sample wines - only user-entered data, let the app scrape the rest
        wines_data = [
            {
                'name': 'Caymus Cabernet Sauvignon',
                'vintage': 2021,
                'price': 89.99,
                'store': stores[0],
                'cellar_name': 'Main Cellar',
                'rack_number': 'A1'
            },
            {
                'name': 'Kendall-Jackson Vintners Reserve Chardonnay',
                'vintage': 2022,
                'price': 21.99,
                'store': stores[1],
                'cellar_name': 'Main Cellar',
                'rack_number': 'B3'
            },
            {
                'name': 'Opus One',
                'vintage': 2019,
                'price': 450.00,
                'store': stores[2],
                'cellar_name': 'Premium Cellar',
                'rack_number': 'P1'
            },
            {
                'name': 'Dom Perignon',
                'vintage': 2014,
                'price': 220.00,
                'store': stores[3],
                'cellar_name': 'Champagne Cellar',
                'rack_number': 'C1'
            },
            {
                'name': 'Silver Oak Alexander Valley Cabernet Sauvignon',
                'vintage': 2020,
                'price': 65.00,
                'store': stores[4],
                'cellar_name': 'Main Cellar',
                'rack_number': 'A5'
            }
        ]
        
        for wine_data in wines_data:
            wine = Wine(
                name=wine_data['name'],
                vintage=wine_data['vintage'],
                price=wine_data['price'],
                store_id=wine_data['store'].id,
                cellar_name=wine_data['cellar_name'],
                rack_number=wine_data['rack_number']
            )
            db.session.add(wine)
        
        db.session.commit()
        
        print("✅ Demo data created successfully!")
        print(f"Added {len(stores)} stores")
        print(f"Added {len(wines_data)} wines")
        print("Wine characteristics (color, region, ratings, etc.) will be populated via web scraping when you view the collection or add new wines.")

if __name__ == "__main__":
    create_demo_data()