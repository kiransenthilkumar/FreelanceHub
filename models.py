from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for both clients and freelancers"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'client' or 'freelancer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    freelancer_profile = db.relationship('FreelancerProfile', uselist=False, backref='user', cascade='all, delete-orphan')
    jobs = db.relationship('Job', backref='client', foreign_keys='Job.client_id', cascade='all, delete-orphan')
    bids = db.relationship('Bid', backref='freelancer', cascade='all, delete-orphan')
    payments_as_client = db.relationship('Payment', foreign_keys='Payment.client_id', backref='client')
    payments_as_freelancer = db.relationship('Payment', foreign_keys='Payment.freelancer_id', backref='freelancer')
    reviews_given = db.relationship('Review', foreign_keys='Review.client_id', backref='client_reviewer')
    reviews_received = db.relationship('Review', foreign_keys='Review.freelancer_id', backref='freelancer_reviewed')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    def is_freelancer(self):
        return self.role == 'freelancer'
    
    def is_client(self):
        return self.role == 'client'
    
    def __repr__(self):
        return f'<User {self.email}>'


class FreelancerProfile(db.Model):
    """Freelancer profile details"""
    __tablename__ = 'freelancer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    bio = db.Column(db.Text)
    skills = db.Column(db.String(500))  # comma-separated
    portfolio_link = db.Column(db.String(255))
    profile_image = db.Column(db.String(255))  # filename
    avg_rating = db.Column(db.Float, default=0)
    total_reviews = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FreelancerProfile {self.user_id}>'


class Job(db.Model):
    """Job postings by clients"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # web, mobile, design, writing, etc
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='open')  # open, in_progress, completed, cancelled
    accepted_bid_id = db.Column(db.Integer, db.ForeignKey('bids.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bids = db.relationship('Bid', backref='job', foreign_keys='Bid.job_id', cascade='all, delete-orphan')
    accepted_bid = db.relationship('Bid', uselist=False, foreign_keys='Job.accepted_bid_id')
    payment = db.relationship('Payment', uselist=False, backref='job', cascade='all, delete-orphan')
    work_submission = db.relationship('WorkSubmission', uselist=False, backref='job', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='job', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Job {self.title}>'


class Bid(db.Model):
    """Bids placed by freelancers on jobs"""
    __tablename__ = 'bids'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    proposal = db.Column(db.Text, nullable=False)
    delivery_days = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Bid job_id={self.job_id} freelancer_id={self.freelancer_id}>'


class Payment(db.Model):
    """Payment records"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, released
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    released_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Payment job_id={self.job_id}>'


class WorkSubmission(db.Model):
    """Work submissions by freelancers"""
    __tablename__ = 'work_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True, unique=True)
    file_path = db.Column(db.String(255), nullable=False)  # file path
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='submitted')  # submitted, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WorkSubmission job_id={self.job_id}>'


class Review(db.Model):
    """Reviews and ratings"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review job_id={self.job_id}>'
