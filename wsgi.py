from app import create_app, db
import os

# Choose config based on environment; default to production on Render
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name=config_name)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
