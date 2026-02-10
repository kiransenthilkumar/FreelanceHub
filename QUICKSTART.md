# FreelanceHub - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Load Demo Data
```bash
python demo_data.py
```

This creates test accounts and sample jobs:
- **Clients**: alice@example.com, bob@example.com
- **Freelancers**: charlie@example.com, diana@example.com, eve@example.com
- **Password**: password123

### Step 3: Run the Application
```bash
python app.py
```

The app will be available at: **http://localhost:5000**

## 📚 Test the Features

### As a Client:
1. Login with alice@example.com / password123
2. Click "My Jobs" - You'll see 2 sample jobs
3. Click "View Bids" to see freelancer proposals
4. Click "Accept Bid" to hire a freelancer
5. Click "Pay Now" to complete the mock payment
6. Click "Review" to rate the freelancer

### As a Freelancer:
1. Login with charlie@example.com / password123
2. Click "Profile" to update your skills and portfolio
3. Click "Browse Jobs" to find available work
4. Click "Place Bid" on a job
5. Wait for the client to accept your bid
6. Click "My Bids" → "Submit Work" to upload your files
7. View earnings in "Dashboard"

## 🎨 Customization

### Change App Title/Logo
Edit [templates/base.html](templates/base.html) - Line 27:
```html
<a href="{{ url_for('index') }}" class="text-2xl font-bold text-blue-600">
    <i class="fas fa-briefcase"></i> FreelanceHub
</a>
```

### Add More Job Categories
Edit [app.py](app.py) - Post job route:
```python
categories = ['web', 'mobile', 'design', 'writing', 'marketing', 'other', 'your-category']
```

### Customize Colors
All colors use Tailwind CSS classes. Common colors:
- Primary: `blue-600` 
- Success: `green-600`
- Danger: `red-600`
- Warning: `yellow-600`

## 🔧 Troubleshooting

### Port 5000 Already in Use?
Edit app.py and change:
```python
app.run(debug=True, port=5001)
```

### Database Issues?
```bash
rm freelancing.db  # Remove old database
python demo_data.py  # Create fresh database
```

### Missing Uploads Folder?
The `uploads/` folder is created automatically on first file upload.

## 📝 Project Structure

```
FreelancingWebsite/
├── app.py              # Main application
├── models.py           # Database models
├── config.py           # Configuration
├── demo_data.py        # Sample data generator
├── templates/          # 23 HTML templates
└── uploads/            # User uploads
```

## 🌟 Key Features Demonstrated

✅ User authentication (Client/Freelancer roles)
✅ Job posting & job discovery
✅ Bidding system with proposals
✅ Work file uploads
✅ Mock payment system
✅ Rating & reviews
✅ User dashboards
✅ Transaction history
✅ Responsive design with Tailwind CSS
✅ SQLite database with SQLAlchemy ORM

## 📦 Deployment (Render)

See [README.md](README.md) for detailed deployment instructions.

## 🤔 Need Help?

Check the [README.md](README.md) for comprehensive documentation or review the code comments in:
- `app.py` - Routes and logic
- `models.py` - Database structure
- `templates/` - HTML templates

---

**Happy freelancing! 🎉**
