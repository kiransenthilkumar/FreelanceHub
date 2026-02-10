```markdown
# FreelanceHub 🚀

A modern freelancing platform connecting clients with talented freelancers. Built with Flask, SQLite, and Tailwind CSS.

---

## Quick Overview

- Post jobs, receive proposals, accept bids, approve work, and make (mock) payments.
- Freelancers browse jobs, place bids, submit work, and receive reviews.
- Role-based UI: Client vs Freelancer views and actions.

---

## Features

### Client
- Post jobs with title, description, budget, category, deadline
- View bids, accept bid, view active contracts
- Approve submitted work and release payment (mock)
- Rate and review freelancers
- Dashboard with job/bid/payment summaries

### Freelancer
- Create/edit profile and portfolio
- Browse jobs and place multiple bids per job
- Submit work and track payment status
- Dashboard showing bids, active jobs, earnings and transactions

### System
- Authentication (Flask-Login), password hashing, role-based access
- File uploads (profile images, work files) with validation and secure filenames
- SQLite + SQLAlchemy models for Users, Jobs, Bids, Payments, Reviews, WorkSubmission
- Responsive UI with Tailwind CSS and Font Awesome icons

---

## Demo & Seed Data (test accounts)

I seeded demo data for testing. Use these accounts to sign in quickly:

Clients
- client1@example.com / password123
- client2@example.com / password123
- client3@example.com / password123
- client4@example.com / password123
- client5@example.com / password123

Freelancers
- freelancer1@example.com / password123
- freelancer2@example.com / password123
- freelancer3@example.com / password123
- freelancer4@example.com / password123
- freelancer5@example.com / password123

Note: Run `python demo_data.py` to recreate this demo dataset.

---

## Quickstart (5 minutes)

1. Create and activate virtualenv
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Seed demo data (optional)
```bash
python demo_data.py
```

4. Run the app
```bash
python app.py
```

Open http://localhost:5000

---

## Usage Highlights

- Register as a client to post jobs or as a freelancer to bid.
- Clients: `Post Job` → `My Jobs` → `View Bids` → `Accept Bid` → approve work → `Pay Now` → review.
- Freelancers: `Browse Jobs` → view job → `Place Bid` → if accepted, `Submit Work` → track payments.

---

## Database Schema (summary)

- Users: id, name, email, password_hash, role (client/freelancer), created_at
- FreelancerProfile: user_id, bio, skills, portfolio_link, profile_image, avg_rating, total_reviews
- Jobs: id, client_id, title, description, budget, category, deadline, status, accepted_bid_id
- Bids: id, job_id, freelancer_id, amount, proposal, delivery_days, status
- Payments: id, job_id, client_id, freelancer_id, amount, status, paid_at
- WorkSubmission: id, job_id, file_path, description, status
- Reviews: id, job_id, client_id, freelancer_id, rating, comment

---

## Implementation Notes & Features Matrix

See the full `FEATURES.md` for the completion matrix. In short:

- Authentication, role-based guards, profile management, job posting, bidding system, payments (mock), reviews, dashboards, and transaction history are implemented.
- File uploads are validated and saved to `uploads/`.
- Pagination and basic search/filtering are included on listings.

---

## Troubleshooting

- If port 5000 is in use, change port in `app.py` when calling `app.run()`.
- To reset the DB, run:
```bash
rm freelancing.db  # or delete the SQLite file
python demo_data.py
```
- If templates throw attribute errors, check model attribute names in `models.py` (e.g., `client_reviewer`, `freelancer_reviewed`).

---

## Deployment (Render)

1. Push repo to GitHub
2. Create a Render Web Service, point to repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:create_app()`
5. Add env vars: `SECRET_KEY`, `FLASK_ENV=production`

---

## Project Structure

```
FreelancingWebsite/
├── app.py
├── models.py
├── config.py
├── demo_data.py
├── requirements.txt
├── templates/
├── static/
└── uploads/
```

---

## Contributing & Support

Contributions welcome. Open issues or PRs on the repository. For quick help, review `app.py` routes and `models.py` for structure and relationships.

---

## License

MIT License

---

Happy freelancing! 🎉
```
# FreelanceHub 🚀

A modern freelancing platform connecting clients with talented freelancers. Built with Flask, SQLite, and Tailwind CSS.

## ✨ Features

### For Clients
- 📝 Post jobs with detailed descriptions
- 💰 Set custom budgets and deadlines
- 👥 Review freelancer proposals
- ✅ Accept bids from freelancers
- 💳 Mock payment system
- ⭐ Rate and review completed work

### For Freelancers
- 🔍 Browse available jobs
- 📋 Create and manage detailed profiles
- 💼 Submit proposals and bids
- 📁 Upload completed work
- 💰 Track earnings and payments
- ⭐ Build reputation through reviews

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML + Tailwind CSS
- **Authentication**: Flask-Login with Session-based Auth
- **Server**: Gunicorn (for production)
- **Deployment**: Render

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd FreelancingWebsite
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your settings (optional for development)
```

### 5. Initialize Database

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 6. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📝 Usage

### Register as Client/Freelancer

1. Click "Register" on the home page
2. Fill in your details (name, email, password)
3. Select role: **Client** (post jobs) or **Freelancer** (bid on jobs)
4. Click "Create Account"

### Client Workflow

1. **Post a Job**
   - Navigate to "Post Job"
   - Fill in title, description, budget, category, deadline
   - Submit

2. **View Bids**
   - Go to "My Jobs"
   - Click "View Bids" on a job
   - Compare freelancers and their proposals

3. **Accept Freelancer**
   - Click "Accept Bid" next to chosen freelancer
   - Job status changes to "In Progress"

4. **Make Payment**
   - Click "Pay Now" on completed job
   - Review mock payment details
   - Click "Confirm Payment"

5. **Review**
   - After payment, click "Review"
   - Rate freelancer (1-5 stars)
   - Leave feedback

### Freelancer Workflow

1. **Update Profile**
   - Go to "Profile"
   - Add bio, skills, hourly rate, portfolio link
   - Upload profile picture

2. **Browse Jobs**
   - Navigate to "Browse Jobs"
   - Filter by category or search
   - Click "View Details" to see full job info

3. **Place Bid**
   - Click "Place Bid"
   - Enter bid amount, delivery time, proposal
   - Submit

4. **Submit Work**
   - After bid is accepted
   - Go to "My Bids" → "Submit Work"
   - Upload project files
   - Add any notes

5. **Track Earnings**
   - View "Dashboard" for earnings summary
   - Check "Transactions" for payment history

## 🗄️ Database Schema

### Users
- id, name, email, password_hash, role (client/freelancer), created_at

### Freelancer Profiles
- user_id, bio, skills, hourly_rate, portfolio_link, profile_image, avg_rating, total_reviews

### Jobs
- id, client_id, title, description, budget, category, deadline, status, accepted_bid_id, created_at

### Bids
- id, job_id, freelancer_id, amount, proposal, delivery_days, status, created_at

### Payments
- id, job_id, client_id, freelancer_id, amount, status (pending/paid/released), created_at

### Reviews
- id, job_id, client_id, freelancer_id, rating (1-5), comment, created_at

## 🔒 Security Features

✅ Password hashing with Werkzeug  
✅ Session-based authentication  
✅ Role-based access control  
✅ CSRF protection  
✅ File upload validation  
✅ SQL injection prevention with SQLAlchemy ORM  

## 📦 Project Structure

```
FreelancingWebsite/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── wsgi.py               # WSGI entry point for production
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── browse-jobs.html  # Job listing
│   ├── job-detail.html   # Job details
│   ├── profile.html      # User profile
│   ├── post-job.html     # Post job form
│   ├── my-jobs.html      # Client's jobs
│   ├── my-bids.html      # Freelancer's bids
│   ├── bids.html         # View bids for job
│   ├── payment.html      # Payment page
│   ├── mock-payment.html # Mock payment gateway
│   ├── payment-confirmation.html # Confirmation
│   ├── review.html       # Review form
│   ├── submit-work.html  # Work submission
│   ├── dashboard-*.html  # User dashboards
│   ├── transactions.html # Transaction history
│   └── error pages       # 404, 403, 500
└── uploads/              # Uploaded files (profile pictures, work files)
```

## 🌐 Deployment on Render

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Create Render Service

1. Go to [render.com](https://render.com)
2. Sign up/login
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: freelancehub
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:create_app()`
6. Add environment variables:
   - `SECRET_KEY`: Strong random string
   - `FLASK_ENV`: production

### 3. Deploy

Click "Deploy" and wait for the build to complete.

## 🧪 Testing

### Test Accounts

You can create test accounts or use these scenarios:

**Client Account:**
- Email: client@example.com
- Password: password123
- Role: Client

**Freelancer Account:**
- Email: freelancer@example.com
- Password: password123
- Role: Freelancer

## 🐛 Troubleshooting

### Database Errors

```bash
# Reset database
rm freelancing.db
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### Import Errors

Make sure all packages are installed:
```bash
pip install -r requirements.txt
```

### Port Already in Use

Change port in `app.py`:
```python
app.run(debug=True, port=5001)
```

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 👨‍💻 Author

Created as a demonstration of a full-stack freelancing platform.

## 🤝 Contributing

Contributions are welcome! Feel free to fork and submit pull requests.

## 📞 Support

For issues or questions, please create an issue in the repository.

---

**Happy Freelancing! 🎉**
#
