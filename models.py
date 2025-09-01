from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    wines = db.relationship('Wine', backref='store', lazy=True)

class Wine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    vintage = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    cellar_name = db.Column(db.String(100), nullable=False)
    rack_number = db.Column(db.String(20), nullable=False)
    
    # Auto-populated fields from web scraping
    drinking_window = db.Column(db.String(50))
    color = db.Column(db.String(10))  # 'Red' or 'White'
    country = db.Column(db.String(100))
    region = db.Column(db.String(100))
    grape_varietal = db.Column(db.String(200))
    ratings_summary = db.Column(db.Float)  # Average of up to 4 ratings
    
    # Enhanced drinking window tracking
    drinking_window_confidence = db.Column(db.String(10))  # 'high', 'medium', 'low'
    drinking_window_source = db.Column(db.String(50))  # Track data source
    peak_drinking_year = db.Column(db.Integer)  # Calculated from window
    window_notes = db.Column(db.String(200))  # Additional context
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    ratings = db.relationship('WineRating', backref='wine', lazy=True, cascade='all, delete-orphan')

class WineRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wine_id = db.Column(db.Integer, db.ForeignKey('wine.id'), nullable=False)
    source = db.Column(db.String(100), nullable=False)  # e.g., 'Wine Spectator', 'Robert Parker'
    rating = db.Column(db.Float, nullable=False)
    max_rating = db.Column(db.Float, nullable=False, default=100)  # To normalize different scales