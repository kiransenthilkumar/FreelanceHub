import os
from dotenv import load_dotenv
from app import create_app, db

# Load environment variables
load_dotenv()

app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
