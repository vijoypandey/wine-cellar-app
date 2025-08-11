from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Wine, Store, WineRating
from trusted_wine_scraper import TrustedWineScraper
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wine_cellar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
scraper = TrustedWineScraper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_wine')
def add_wine():
    stores = Store.query.all()
    return render_template('add_wine.html', stores=stores)

@app.route('/api/wine_suggestions')
def wine_suggestions():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    # Get existing wine names that match the query
    wines = Wine.query.filter(Wine.name.ilike(f'%{query}%')).distinct(Wine.name).limit(10).all()
    suggestions = [wine.name for wine in wines]
    
    return jsonify(suggestions)

@app.route('/api/store_suggestions')
def store_suggestions():
    query = request.args.get('q', '').strip()
    if len(query) < 1:
        stores = Store.query.all()
        return jsonify([store.name for store in stores])
    
    stores = Store.query.filter(Store.name.ilike(f'%{query}%')).limit(10).all()
    suggestions = [store.name for store in stores]
    
    return jsonify(suggestions)

@app.route('/submit_wine', methods=['POST'])
def submit_wine():
    try:
        # Get form data
        wine_name = request.form.get('wine_name')
        vintage = int(request.form.get('vintage'))
        price = float(request.form.get('price'))
        store_name = request.form.get('store_name')
        cellar_name = request.form.get('cellar_name')
        rack_number = request.form.get('rack_number')
        
        # Get or create store
        store = Store.query.filter_by(name=store_name).first()
        if not store:
            store = Store(name=store_name)
            db.session.add(store)
            db.session.commit()
        
        # Create wine entry
        wine = Wine(
            name=wine_name,
            vintage=vintage,
            price=price,
            store_id=store.id,
            cellar_name=cellar_name,
            rack_number=rack_number
        )
        
        db.session.add(wine)
        db.session.commit()
        
        # Scrape wine data in background
        try:
            wine_data = scraper.search_wine_data(wine_name, vintage)
            
            # If no data found, use mock data for demonstration
            if not any(wine_data.values()):
                wine_data = scraper.get_mock_wine_data(wine_name, vintage)
            
            # Update wine with scraped data
            wine.drinking_window = wine_data.get('drinking_window')
            wine.color = wine_data.get('color')
            wine.country = wine_data.get('country')
            wine.region = wine_data.get('region')
            wine.grape_varietal = wine_data.get('grape_varietal')
            
            # Add ratings
            ratings = wine_data.get('ratings', [])
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
            
            if count > 0:
                wine.ratings_summary = round(total_rating / count, 1)
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error scraping wine data: {e}")
        
        return redirect(url_for('collection'))
        
    except Exception as e:
        return f"Error adding wine: {e}", 400

@app.route('/collection')
def collection():
    # Get filter and sort parameters
    sort_by = request.args.get('sort', 'name')
    filter_color = request.args.get('color', '')
    filter_cellar = request.args.get('cellar', '')
    filter_store = request.args.get('store', '')
    
    # Build query
    query = Wine.query
    
    # Apply filters
    if filter_color:
        query = query.filter(Wine.color == filter_color)
    if filter_cellar:
        query = query.filter(Wine.cellar_name.ilike(f'%{filter_cellar}%'))
    if filter_store:
        query = query.join(Store).filter(Store.name.ilike(f'%{filter_store}%'))
    
    # Apply sorting
    if sort_by == 'name':
        query = query.order_by(Wine.name)
    elif sort_by == 'vintage':
        query = query.order_by(Wine.vintage.desc())
    elif sort_by == 'price':
        query = query.order_by(Wine.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Wine.ratings_summary.desc())
    
    wines = query.all()
    
    # Get unique values for filter dropdowns
    cellars = db.session.query(Wine.cellar_name).distinct().all()
    cellars = [c[0] for c in cellars if c[0]]
    
    stores = Store.query.all()
    
    return render_template('collection.html', 
                         wines=wines, 
                         cellars=cellars,
                         stores=stores,
                         current_sort=sort_by,
                         current_filters={
                             'color': filter_color,
                             'cellar': filter_cellar,
                             'store': filter_store
                         })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)