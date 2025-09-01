# Installation & Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git (for version control)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd wine-cellar-app
```

### 2. Install Dependencies

Install the required Python packages:

```bash
pip3 install -r requirements.txt
```

**Required packages:**
- Flask==3.0.0
- SQLAlchemy==2.0.23
- Flask-SQLAlchemy==3.1.1
- requests==2.31.0
- beautifulsoup4==4.12.2
- lxml==4.9.3
- Werkzeug==3.0.1

### 3. Database Setup

Initialize the SQLite database with enhanced schema:

```bash
python3 -c "
from app import app
from models import db
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
```

This creates `wine_cellar.db` with the following tables:
- `wine` - Main wine records with enhanced drinking window fields
- `store` - Wine store information
- `wine_rating` - Individual ratings from different sources

### 4. Verify Installation

Test the drinking window service:

```bash
python3 test_drinking_window.py
```

Expected output should show drinking windows for various wine types with confidence levels and sources.

## Running the Application

### Development Mode

Start the Flask development server:

```bash
python3 app.py
```

The application will be available at: `http://localhost:5000`

### Production Deployment

For production deployment, consider using:

**Option 1: Gunicorn**
```bash
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Option 2: Docker (create Dockerfile)**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python3", "app.py"]
```

## Configuration

### Environment Variables

Create a `.env` file for sensitive configuration:

```bash
# .env
SECRET_KEY=your-production-secret-key-here
DATABASE_URL=sqlite:///wine_cellar.db
FLASK_ENV=production
```

Update `app.py` to use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///wine_cellar.db')
```

### Database Configuration

**SQLite (Default):**
- File-based database
- Perfect for development and small deployments
- No additional setup required

**PostgreSQL (Production):**
```bash
pip3 install psycopg2-binary
```

Update database URI:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/wine_cellar_db'
```

**MySQL (Alternative):**
```bash
pip3 install PyMySQL
```

Update database URI:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/wine_cellar_db'
```

## Testing

### Unit Tests

Run the drinking window service tests:

```bash
python3 -m pytest test_drinking_window.py -v
```

### Manual Testing

1. **Start the application:**
   ```bash
   python3 app.py
   ```

2. **Navigate to:** `http://localhost:5000`

3. **Test the workflow:**
   - Add a wine (e.g., "Chateau Lafite Rothschild 2020")
   - Wait for background scraping to complete
   - View the collection to see drinking window data

### Expected Behavior

When adding wines, you should see:
- Drinking windows appear in collection view
- Confidence badges (high/medium/low)
- Source attribution
- Peak drinking years
- Proper fallback to rule-based estimates

## Troubleshooting

### Common Issues

**1. Module Import Errors**
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:** Ensure all dependencies are installed
```bash
pip3 install -r requirements.txt
```

**2. Database Errors**
```
sqlalchemy.exc.OperationalError: no such table: wine
```
**Solution:** Initialize the database
```bash
python3 -c "from app import app; from models import db; app.app_context().push(); db.create_all()"
```

**3. Network/SSL Warnings**
```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+
```
**Solution:** This is a warning, not an error. The application will still function correctly.

**4. No Drinking Window Data**
```
All wines show fallback rules only
```
**Possible causes:**
- Network connectivity issues
- Websites blocking requests
- Rate limiting by target sites

**Solution:** This is expected behavior. The fallback rules provide reasonable estimates when web scraping fails.

### Debug Mode

Enable Flask debug mode for development:

```python
# In app.py
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

### Logging

Add logging to debug issues:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In drinking_window_service.py
logger.debug(f"Attempting to scrape {source} for {wine_name} {vintage}")
```

## Performance Optimization

### Caching

The service includes in-memory caching, but for production consider:

**Redis Caching:**
```bash
pip3 install redis
```

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Cache drinking window results
cache_key = f"wine:{wine_name}:{vintage}"
r.setex(cache_key, 86400, json.dumps(result))  # 24 hour cache
```

### Database Indexing

Add indexes for better query performance:

```sql
CREATE INDEX idx_wine_name_vintage ON wine(name, vintage);
CREATE INDEX idx_wine_color ON wine(color);
CREATE INDEX idx_wine_country_region ON wine(country, region);
```

### Rate Limiting

For high-traffic applications, implement rate limiting:

```bash
pip3 install Flask-Limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## Security Considerations

### Input Validation

Ensure proper input validation:

```python
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, validators

class WineForm(FlaskForm):
    wine_name = StringField('Wine Name', [validators.Length(min=1, max=200)])
    vintage = IntegerField('Vintage', [validators.NumberRange(min=1800, max=2030)])
```

### Database Security

- Use parameterized queries (already implemented with SQLAlchemy)
- Validate all user inputs
- Consider SQL injection prevention

### Web Scraping Ethics

- Respect robots.txt files
- Implement reasonable delays between requests (1 second implemented)
- Monitor for rate limiting responses
- Consider reaching out to sites for API access

## Backup and Maintenance

### Database Backup

**SQLite Backup:**
```bash
cp wine_cellar.db wine_cellar_backup_$(date +%Y%m%d).db
```

**Automated Backup Script:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp wine_cellar.db backups/wine_cellar_$DATE.db
find backups/ -name "wine_cellar_*.db" -mtime +30 -delete
```

### Log Rotation

Set up log rotation for production:

```bash
# /etc/logrotate.d/wine-cellar-app
/var/log/wine-cellar-app/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    postrotate
        systemctl reload wine-cellar-app
    endscript
}
```

## Monitoring

Consider implementing monitoring for production:

**Health Check Endpoint:**
```python
@app.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return {'status': 'healthy'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```

**Metrics Collection:**
- Response times
- Database query performance
- Scraping success rates
- Error rates by source