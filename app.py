import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
from config import Config, config
from models import db, User, FreelancerProfile, Job, Bid, Payment, WorkSubmission, Review

def create_app(config_name='development', test_config=None):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, Config))
    
    if test_config:
        app.config.update(test_config)
    
    # Disable Jinja2 caching for development
    app.jinja_env.cache = None
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth_login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Add template filters
    @app.template_filter('format_date')
    def format_date(date):
        if date:
            return date.strftime('%B %d, %Y')
        return ''
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except:
            return None
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Add cache-busting headers
    @app.after_request
    def add_no_cache_headers(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    @app.context_processor
    def inject_static_version():
        """Inject a cache-busting version (file mtime) for static assets."""
        try:
            css_path = os.path.join(app.root_path, 'static', 'css', 'styles.css')
            if os.path.exists(css_path):
                v = int(os.path.getmtime(css_path))
            else:
                v = int(datetime.utcnow().timestamp())
        except Exception:
            v = int(datetime.utcnow().timestamp())
        return {'css_version': v}
    
    # ================== UTILITY FUNCTIONS ==================
    
    def allowed_file(filename):
        """Check if file is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    
    def client_required(f):
        """Decorator to require client role"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_client():
                flash('You must be logged in as a client to access this page.', 'danger')
                return redirect(url_for('auth_login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def freelancer_required(f):
        """Decorator to require freelancer role"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_freelancer():
                flash('You must be logged in as a freelancer to access this page.', 'danger')
                return redirect(url_for('auth_login'))
            return f(*args, **kwargs)
        return decorated_function
    
    # ================== AUTHENTICATION ROUTES ==================
    
    @app.route('/')
    def index():
        """Landing page"""
        # If user is logged in, send them to their dashboard instead of public landing
        if current_user.is_authenticated:
            if current_user.is_freelancer():
                return redirect(url_for('freelancer_dashboard'))
            else:
                return redirect(url_for('dashboard'))

        jobs_count = Job.query.filter_by(status='open').count()
        users_count = User.query.count()
        freelancers_count = User.query.filter_by(role='freelancer').count()

        recent_jobs = Job.query.filter_by(status='open').order_by(Job.created_at.desc()).limit(6).all()
        now = datetime.utcnow()

        return render_template('index.html', 
                             jobs_count=jobs_count,
                             users_count=users_count,
                             freelancers_count=freelancers_count,
                             recent_jobs=recent_jobs,
                             now=now)
    
    @app.route('/register', methods=['GET', 'POST'])
    def auth_register():
        """User registration"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            role = request.form.get('role')
            
            if not all([name, email, password, confirm_password, role]):
                flash('All fields are required.', 'danger')
                return redirect(url_for('auth_register'))
            
            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return redirect(url_for('auth_register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already exists.', 'danger')
                return redirect(url_for('auth_register'))
            
            user = User(name=name, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            # Create freelancer profile if registering as freelancer
            if role == 'freelancer':
                profile = FreelancerProfile(user_id=user.id)
                db.session.add(profile)
                db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth_login'))
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def auth_login():
        """User login"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not email or not password:
                flash('Email and password are required.', 'danger')
                return redirect(url_for('auth_login'))
            
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.check_password(password):
                flash('Invalid email or password.', 'danger')
                return redirect(url_for('auth_login'))
            
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def auth_logout():
        """User logout"""
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))
    
    # ================== FREELANCER ROUTES ==================
    
    @app.route('/profile', methods=['GET', 'POST'])
    @freelancer_required
    def profile():
        """Freelancer profile"""
        profile = current_user.freelancer_profile
        
        if not profile:
            profile = FreelancerProfile(user_id=current_user.id)
            db.session.add(profile)
            db.session.commit()
        
        if request.method == 'POST':
            profile.bio = request.form.get('bio')
            profile.skills = request.form.get('skills')
            profile.portfolio_link = request.form.get('portfolio_link')
            
            # Handle profile image upload
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file and allowed_file(file.filename):
                    filename = secure_filename(f"{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}")
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    profile.profile_image = filename
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        
        reviews = Review.query.filter_by(freelancer_id=current_user.id).all()
        return render_template('profile.html', profile=profile, reviews=reviews)

    @app.route('/client-profile', methods=['GET', 'POST'])
    @client_required
    def client_profile():
        """Client profile page (basic editable fields)"""
        if request.method == 'POST':
            name = request.form.get('name')
            # we intentionally don't allow changing email here for simplicity
            if name:
                current_user.name = name
                db.session.commit()
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('client_profile'))

        # Show a simple client profile page
        return render_template('client_profile.html')

    @app.route('/freelancer/<int:user_id>')
    @login_required
    def view_freelancer_profile(user_id):
        """View public freelancer profile"""
        user = User.query.get(user_id)
        if not user or not user.is_freelancer():
            flash('Freelancer not found.', 'danger')
            return redirect(url_for('index'))
        
        profile = FreelancerProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            flash('Freelancer profile not found.', 'danger')
            return redirect(url_for('index'))
        
        # Get reviews for this freelancer
        reviews = Review.query.filter_by(freelancer_id=user_id).all()
        
        return render_template('view-freelancer.html', user=user, profile=profile, reviews=reviews)

    @app.route('/change-password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        """Allow any logged-in user to change their password."""
        if request.method == 'POST':
            current_pwd = request.form.get('current_password')
            new_pwd = request.form.get('new_password')
            confirm_pwd = request.form.get('confirm_password')

            if not all([current_pwd, new_pwd, confirm_pwd]):
                flash('All password fields are required.', 'danger')
                return redirect(url_for('change_password'))

            if not current_user.check_password(current_pwd):
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('change_password'))

            if new_pwd != confirm_pwd:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('change_password'))

            current_user.set_password(new_pwd)
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('dashboard'))

        return render_template('change_password.html')
    
    @app.route('/browse-jobs')
    @freelancer_required
    def browse_jobs():
        """Browse available jobs"""
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        
        query = Job.query.filter_by(status='open')
        
        if category:
            query = query.filter_by(category=category)
        
        if search:
            query = query.filter(Job.title.ilike(f'%{search}%') | Job.description.ilike(f'%{search}%'))
        
        pagination = query.order_by(Job.created_at.desc()).paginate(page=page, per_page=12)
        jobs = pagination.items
        
        # Get my bids
        my_bids = Bid.query.filter_by(freelancer_id=current_user.id).all()
        my_bid_job_ids = {bid.job_id for bid in my_bids}
        
        categories = ['web', 'mobile', 'design', 'writing', 'marketing', 'other']
        
        return render_template('browse-jobs.html', 
                             jobs=jobs, 
                             pagination=pagination,
                             my_bid_job_ids=my_bid_job_ids,
                             categories=categories,
                             search=search,
                             category=category)
    
    @app.route('/job/<int:job_id>')
    def job_detail(job_id):
        """View job details"""
        job = Job.query.get_or_404(job_id)
        
        # Get bids if user is the client (show all bids for visibility)
        bids = []
        if current_user.is_authenticated and job.client_id == current_user.id:
            bids = Bid.query.filter_by(job_id=job_id).order_by(Bid.created_at.desc()).all()
        
        # Check if current user has bid on this job (allow multiple bids)
        user_bids = []
        if current_user.is_authenticated and current_user.is_freelancer():
            user_bids = Bid.query.filter_by(job_id=job_id, freelancer_id=current_user.id).order_by(Bid.created_at.desc()).all()
        
        # Get work submission and reviews
        work_submission = job.work_submission
        reviews = job.reviews
        
        return render_template('job-detail.html', job=job, bids=bids, user_bids=user_bids, work_submission=work_submission, reviews=reviews)
    
    @app.route('/job/<int:job_id>/bid', methods=['POST'])
    @freelancer_required
    def place_bid(job_id):
        """Place a bid on a job"""
        job = Job.query.get_or_404(job_id)
        
        if job.status != 'open':
            flash('This job is no longer open.', 'danger')
            return redirect(url_for('job_detail', job_id=job_id))
        
        amount = request.form.get('amount', type=float)
        proposal = request.form.get('proposal')
        delivery_days = request.form.get('delivery_days', type=int)
        
        if not all([amount, proposal, delivery_days]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('job_detail', job_id=job_id))
        
        bid = Bid(job_id=job_id, freelancer_id=current_user.id, 
                 amount=amount, proposal=proposal, delivery_days=delivery_days)
        db.session.add(bid)
        db.session.commit()
        
        flash('Bid placed successfully!', 'success')
        return redirect(url_for('my_bids'))
    
    @app.route('/my-bids')
    @freelancer_required
    def my_bids():
        """View my bids"""
        page = request.args.get('page', 1, type=int)
        status = request.args.get('status', '')
        
        query = Bid.query.filter_by(freelancer_id=current_user.id)
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(Bid.created_at.desc()).paginate(page=page, per_page=10)
        bids = pagination.items
        
        return render_template('my-bids.html', bids=bids, pagination=pagination, status=status)

    @app.route('/bid/<int:bid_id>/details')
    @freelancer_required
    def bid_details(bid_id):
        """View bid and job details with timeline, payment, and reviews"""
        bid = Bid.query.get_or_404(bid_id)
        
        if bid.freelancer_id != current_user.id:
            flash('You do not have permission to view this bid.', 'danger')
            return redirect(url_for('my_bids'))
        
        job = bid.job
        work = job.work_submission
        payment = job.payment
        review = Review.query.filter_by(job_id=job.id, freelancer_id=current_user.id).first()
        
        return render_template('bid-details.html', bid=bid, job=job, work=work, payment=payment, review=review)
    
    @app.route('/submit-work/<int:job_id>', methods=['GET', 'POST'])
    @freelancer_required
    def submit_work(job_id):
        """Submit work for a job"""
        job = Job.query.get_or_404(job_id)
        
        # Check if freelancer is the accepted one
        if job.status not in ['in_progress']:
            flash('This job is not in progress.', 'danger')
            return redirect(url_for('browse_jobs'))
        
        accepted_bid = Bid.query.get(job.accepted_bid_id)
        if not accepted_bid or accepted_bid.freelancer_id != current_user.id:
            flash('You are not assigned to this job.', 'danger')
            return redirect(url_for('browse_jobs'))
        
        work_submission = job.work_submission
        
        if request.method == 'POST':
            description = request.form.get('description')
            
            if 'file' not in request.files:
                flash('No file selected.', 'danger')
                return redirect(url_for('submit_work', job_id=job_id))
            
            file = request.files['file']
            if not file or not file.filename:
                flash('No file selected.', 'danger')
                return redirect(url_for('submit_work', job_id=job_id))
            
            if not allowed_file(file.filename):
                flash('File type not allowed.', 'danger')
                return redirect(url_for('submit_work', job_id=job_id))
            
            filename = secure_filename(f"{job_id}_{datetime.utcnow().timestamp()}_{file.filename}")
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            if work_submission:
                work_submission.file_path = filename
                work_submission.description = description
            else:
                work_submission = WorkSubmission(job_id=job_id, file_path=filename, description=description)
                db.session.add(work_submission)
            
            db.session.commit()
            flash('Work submitted successfully!', 'success')
            return redirect(url_for('browse_jobs'))
        
        return render_template('submit-work.html', job=job, work_submission=work_submission)

    @app.route('/uploads/<path:filename>')
    @login_required
    def uploaded_file(filename):
        """Serve uploaded files securely"""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)

    @app.route('/job/<int:job_id>/work')
    @client_required
    def view_work(job_id):
        """Client view for submitted work"""
        job = Job.query.get_or_404(job_id)

        if job.client_id != current_user.id:
            flash('You do not have permission to view this work.', 'danger')
            return redirect(url_for('my_jobs'))

        work = job.work_submission
        return render_template('view-work.html', job=job, work=work)

    @app.route('/work/<int:job_id>/approve', methods=['POST'])
    @client_required
    def approve_work(job_id):
        """Approve submitted work (client action)"""
        job = Job.query.get_or_404(job_id)
        if job.client_id != current_user.id:
            flash('You do not have permission to perform this action.', 'danger')
            return redirect(url_for('my_jobs'))

        work = job.work_submission
        if not work:
            flash('No work has been submitted for this job.', 'danger')
            return redirect(url_for('job_detail', job_id=job_id))
        # Mark work approved by client and create/ensure payment is pending
        work.status = 'approved'
        job.status = 'awaiting_payment'

        accepted_bid = None
        if job.accepted_bid_id:
            accepted_bid = Bid.query.get(job.accepted_bid_id)

        # Create payment record if not exists
        if not job.payment:
            amount = accepted_bid.amount if accepted_bid else job.budget
            payment = Payment(job_id=job.id, client_id=job.client_id,
                              freelancer_id=accepted_bid.freelancer_id if accepted_bid else None,
                              amount=amount, status='pending')
            db.session.add(payment)
        else:
            job.payment.status = 'pending'

        db.session.commit()
        flash('Work approved. Please complete payment to release funds to the freelancer.', 'success')
        return redirect(url_for('payment_page', job_id=job.id))

    @app.route('/work/<int:job_id>/reject', methods=['POST'])
    @client_required
    def reject_work(job_id):
        """Reject submitted work (client action)"""
        job = Job.query.get_or_404(job_id)
        if job.client_id != current_user.id:
            flash('You do not have permission to perform this action.', 'danger')
            return redirect(url_for('my_jobs'))

        work = job.work_submission
        if not work:
            flash('No work has been submitted for this job.', 'danger')
            return redirect(url_for('job_detail', job_id=job_id))

        work.status = 'rejected'
        job.status = 'in_progress'
        db.session.commit()
        flash('Work rejected. Freelancer notified to resubmit.', 'warning')
        return redirect(url_for('my_jobs'))
    
    # ================== CLIENT ROUTES ==================
    
    @app.route('/post-job', methods=['GET', 'POST'])
    @client_required
    def post_job():
        """Post a new job"""
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            budget = request.form.get('budget', type=float)
            category = request.form.get('category')
            deadline = request.form.get('deadline')
            
            if not all([title, description, budget, category, deadline]):
                flash('All fields are required.', 'danger')
                return redirect(url_for('post_job'))
            
            try:
                deadline = datetime.strptime(deadline, '%Y-%m-%d')
            except ValueError:
                flash('Invalid deadline format.', 'danger')
                return redirect(url_for('post_job'))
            
            if deadline <= datetime.utcnow():
                flash('Deadline must be in the future.', 'danger')
                return redirect(url_for('post_job'))
            
            job = Job(client_id=current_user.id, title=title, description=description,
                     budget=budget, category=category, deadline=deadline)
            db.session.add(job)
            db.session.commit()
            
            flash('Job posted successfully!', 'success')
            return redirect(url_for('my_jobs'))
        
        categories = ['web', 'mobile', 'design', 'writing', 'marketing', 'other']
        return render_template('post-job.html', categories=categories)
    
    @app.route('/my-jobs')
    @client_required
    def my_jobs():
        """View my posted jobs"""
        page = request.args.get('page', 1, type=int)
        status = request.args.get('status', '')
        
        query = Job.query.filter_by(client_id=current_user.id)
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(Job.created_at.desc()).paginate(page=page, per_page=10)
        jobs = pagination.items
        
        # Get reviews for all jobs
        job_reviews = {}
        for job in jobs:
            review = Review.query.filter_by(job_id=job.id, client_id=current_user.id).first()
            job_reviews[job.id] = review
        
        return render_template('my-jobs.html', jobs=jobs, pagination=pagination, status=status, job_reviews=job_reviews)
    
    @app.route('/job/<int:job_id>/bids')
    @client_required
    def view_bids(job_id):
        """View bids for a job"""
        job = Job.query.get_or_404(job_id)
        
        if job.client_id != current_user.id:
            flash('You do not have permission to view these bids.', 'danger')
            return redirect(url_for('my_jobs'))
        
        bids = Bid.query.filter_by(job_id=job_id).all()
        
        return render_template('bids.html', job=job, bids=bids)
    
    @app.route('/bid/<int:bid_id>/accept', methods=['POST'])
    @client_required
    def accept_bid(bid_id):
        """Accept a bid"""
        bid = Bid.query.get_or_404(bid_id)
        job = bid.job
        
        if job.client_id != current_user.id:
            flash('You do not have permission to accept this bid.', 'danger')
            return redirect(url_for('my_jobs'))
        
        if job.status != 'open':
            flash('This job is no longer open.', 'danger')
            return redirect(url_for('view_bids', job_id=job.id))
        
        # Reject all other bids
        for other_bid in job.bids:
            if other_bid.id != bid_id:
                other_bid.status = 'rejected'
        
        bid.status = 'accepted'
        job.status = 'in_progress'
        job.accepted_bid_id = bid.id
        
        db.session.commit()
        
        flash(f'Bid from {bid.freelancer.name} accepted! Job status is now in progress.', 'success')
        return redirect(url_for('view_bids', job_id=job.id))
    
    @app.route('/pay/<int:job_id>', methods=['GET', 'POST'])
    @client_required
    def payment_page(job_id):
        """Payment page"""
        job = Job.query.get_or_404(job_id)
        
        if job.client_id != current_user.id:
            flash('You do not have permission to pay for this job.', 'danger')
            return redirect(url_for('my_jobs'))
        
        if not job.accepted_bid_id:
            flash('This job does not have an accepted bid.', 'danger')
            return redirect(url_for('job_detail', job_id=job_id))

        # Check if payment already exists
        payment = job.payment
        if payment and payment.status in ['paid', 'released']:
            flash('Payment already processed for this job.', 'info')
            return redirect(url_for('payment_confirmation', payment_id=payment.id))

        accepted_bid = Bid.query.get(job.accepted_bid_id)
        
        if request.method == 'POST':
            # Create or update payment record
            if not payment:
                payment = Payment(job_id=job.id, client_id=job.client_id, 
                                freelancer_id=accepted_bid.freelancer_id, amount=accepted_bid.amount)
                db.session.add(payment)
            
            db.session.commit()
            
            return redirect(url_for('mock_payment', payment_id=payment.id))
        
        return render_template('payment.html', job=job, bid=accepted_bid)
    
    @app.route('/mock-payment/<int:payment_id>', methods=['GET', 'POST'])
    @client_required
    def mock_payment(payment_id):
        """Mock payment gateway (Card/UPI)"""
        payment = Payment.query.get_or_404(payment_id)
        
        if payment.client_id != current_user.id:
            flash('You do not have permission to pay this.', 'danger')
            return redirect(url_for('my_jobs'))
        
        if request.method == 'POST':
            payment_method = request.form.get('payment_method', 'card')
            payment.status = 'paid'
            payment.paid_at = datetime.utcnow()

            # mark job as completed
            job = payment.job
            if job:
                job.status = 'completed'

            db.session.commit()
            
            if payment_method == 'upi':
                flash('Payment successful via UPI!', 'success')
            else:
                flash('Payment successful via Card!', 'success')
            return redirect(url_for('payment_confirmation', payment_id=payment_id))
        
        return render_template('mock-payment.html', payment=payment)
    
    @app.route('/payment-confirmation/<int:payment_id>')
    @client_required
    def payment_confirmation(payment_id):
        """Payment confirmation page"""
        payment = Payment.query.get_or_404(payment_id)
        
        if payment.client_id != current_user.id:
            flash('You do not have permission to view this.', 'danger')
            return redirect(url_for('my_jobs'))
        
        return render_template('payment-confirmation.html', payment=payment)
    
    @app.route('/review/<int:job_id>', methods=['GET', 'POST'])
    @client_required
    def review_freelancer(job_id):
        """Review a freelancer"""
        job = Job.query.get_or_404(job_id)
        
        if job.client_id != current_user.id:
            flash('You do not have permission to review for this job.', 'danger')
            return redirect(url_for('my_jobs'))
        
        payment = job.payment
        if not payment or payment.status != 'paid':
            flash('You can only review after payment is completed.', 'danger')
            return redirect(url_for('job_detail', job_id=job_id))
        
        # Check if review already exists
        existing_review = Review.query.filter_by(job_id=job_id, client_id=current_user.id).first()
        if existing_review:
            flash('You have already reviewed this job.', 'danger')
            return redirect(url_for('my_jobs'))
        
        accepted_bid = Bid.query.get(job.accepted_bid_id)
        
        if request.method == 'POST':
            rating = request.form.get('rating', type=int)
            comment = request.form.get('comment')
            
            if not rating or rating < 1 or rating > 5:
                flash('Rating must be between 1 and 5.', 'danger')
                return redirect(url_for('review_freelancer', job_id=job_id))
            
            review = Review(job_id=job_id, client_id=current_user.id,
                          freelancer_id=accepted_bid.freelancer_id, 
                          rating=rating, comment=comment)
            db.session.add(review)
            
            # Update freelancer profile rating
            freelancer = accepted_bid.freelancer
            reviews = Review.query.filter_by(freelancer_id=freelancer.id).all()
            total_rating = sum(r.rating for r in reviews) + rating
            freelancer.freelancer_profile.avg_rating = total_rating / (len(reviews) + 1)
            freelancer.freelancer_profile.total_reviews = len(reviews) + 1
            
            db.session.commit()
            
            flash('Review submitted successfully!', 'success')
            return redirect(url_for('my_jobs'))
        
        return render_template('review.html', job=job, freelancer=accepted_bid.freelancer)
    
    # ================== COMMON ROUTES ==================
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard"""
        if current_user.is_freelancer():
            bids_count = Bid.query.filter_by(freelancer_id=current_user.id).count()
            accepted_bids = Bid.query.filter_by(freelancer_id=current_user.id, status='accepted').count()
            earnings = db.session.query(db.func.sum(Payment.amount)).filter(
                Payment.freelancer_id == current_user.id,
                Payment.status == 'paid'
            ).scalar() or 0
            
            # Get recent jobs by getting freelancer's bids
            freelancer_bids = Bid.query.filter_by(freelancer_id=current_user.id).order_by(Bid.created_at.desc()).limit(5).all()
            recent_jobs = [bid.job for bid in freelancer_bids]
            
            return render_template('dashboard-freelancer.html', 
                                 bids_count=bids_count,
                                 accepted_bids=accepted_bids,
                                 earnings=earnings,
                                 recent_jobs=recent_jobs)
        else:
            # CLIENT DASHBOARD
            jobs_count = Job.query.filter_by(client_id=current_user.id).count()
            open_jobs = Job.query.filter_by(client_id=current_user.id, status='open').count()
            spent = db.session.query(db.func.sum(Payment.amount)).filter(
                Payment.client_id == current_user.id,
                Payment.status.in_(['paid', 'released'])
            ).scalar() or 0
            
            # 1. Get all client's jobs with bid counts
            all_jobs = Job.query.filter_by(client_id=current_user.id).order_by(Job.created_at.desc()).all()
            jobs_with_bids = []
            for job in all_jobs:
                jobs_with_bids.append({
                    'id': job.id,
                    'title': job.title,
                    'status': job.status,
                    'budget': job.budget,
                    'bids_count': len(job.bids),
                    'created_at': job.created_at
                })
            
            # 2. Get all bids for client's jobs
            client_jobs_ids = [job.id for job in all_jobs]
            all_bids = db.session.query(Bid).filter(Bid.job_id.in_(client_jobs_ids)) if client_jobs_ids else []
            bids_list = []
            for bid in all_bids:
                if bid.job:
                    bids_list.append({
                        'id': bid.id,
                        'freelancer_name': bid.freelancer.name if bid.freelancer else 'Unknown',
                        'freelancer_id': bid.freelancer_id,
                        'job_id': bid.job_id,
                        'job_title': bid.job.title,
                        'amount': bid.amount,
                        'proposal': bid.proposal,
                        'status': bid.status,
                        'rating': bid.freelancer.freelancer_profile.avg_rating if bid.freelancer and bid.freelancer.freelancer_profile else 0
                    })
            
            # 3. Get active contracts (accepted bids)
            active_contracts = []
            for job in all_jobs:
                if job.status in ['in_progress', 'awaiting_payment'] and job.accepted_bid_id:
                    accepted_bid = Bid.query.get(job.accepted_bid_id)
                    if accepted_bid:
                        active_contracts.append({
                            'job_id': job.id,
                            'job_title': job.title,
                            'freelancer_name': accepted_bid.freelancer.name if accepted_bid.freelancer else 'Unknown',
                            'freelancer_id': accepted_bid.freelancer_id,
                            'deadline': job.deadline,
                            'work_status': job.work_submission.status if job.work_submission else 'pending',
                            'amount': accepted_bid.amount
                        })
            
            # 4. Get payments
            payments = Payment.query.filter_by(client_id=current_user.id).order_by(Payment.created_at.desc()).limit(20).all()
            payments_list = []
            for payment in payments:
                if payment.job and payment.freelancer:
                    payments_list.append({
                        'id': payment.id,
                        'job_id': payment.job.id,
                        'id': payment.id,
                        'job_name': payment.job.title,
                        'freelancer_name': payment.freelancer.name,
                        'amount': payment.amount,
                        'status': payment.status,
                        'work_status': payment.job.work_submission.status if payment.job.work_submission else None,
                        'created_at': payment.created_at
                    })
            
            # 5. Get reviews given by client
            reviews_given = Review.query.filter_by(client_id=current_user.id).order_by(Review.id.desc()).limit(10).all()
            reviews_list = []
            for review in reviews_given:
                if review.freelancer_reviewed:
                    reviews_list.append({
                        'freelancer_name': review.freelancer_reviewed.name,
                        'rating': review.rating,
                        'comment': review.comment,
                        'job_title': review.job.title if review.job else 'Unknown Job'
                    })
            
            # 6. Count hired freelancers
            hired_freelancers = set()
            for job in all_jobs:
                if job.status in ['in_progress', 'completed', 'awaiting_payment'] and job.accepted_bid_id:
                    accepted_bid = Bid.query.get(job.accepted_bid_id)
                    if accepted_bid:
                        hired_freelancers.add(accepted_bid.freelancer_id)
            
            return render_template('dashboard-client.html',
                                 # KPIs
                                 jobs_count=jobs_count,
                                 open_jobs=open_jobs,
                                 spent=spent,
                                 hired_freelancers_count=len(hired_freelancers),
                                 # Jobs
                                 jobs_with_bids=jobs_with_bids,
                                 # Bids
                                 bids_list=bids_list,
                                 # Active contracts
                                 active_contracts=active_contracts,
                                 # Payments
                                 payments_list=payments_list,
                                 # Reviews
                                 reviews_list=reviews_list,
                                 recent_jobs=all_jobs[:5])

    @app.route('/freelancer-dashboard')
    @login_required
    def freelancer_dashboard():
        """Freelancer dashboard with comprehensive overview."""
        if not current_user.is_freelancer():
            flash('You must be a freelancer to view this page.', 'danger')
            return redirect(url_for('dashboard'))

        # 1. Overview KPIs
        bids_count = Bid.query.filter_by(freelancer_id=current_user.id).count()
        accepted_bids = Bid.query.filter_by(freelancer_id=current_user.id, status='accepted').count()
        earnings = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.freelancer_id == current_user.id,
            Payment.status == 'paid'
        ).scalar() or 0

        # Get freelancer profile
        profile = FreelancerProfile.query.filter_by(user_id=current_user.id).first()
        avg_rating = profile.avg_rating if profile else 0

        # 2. Profile Completion
        profile_completion = 0
        missing_items = []
        if profile:
            profile_completion += 25 if profile.bio else 0
            if not profile.bio:
                missing_items.append('Bio')
            profile_completion += 25 if profile.skills else 0
            if not profile.skills:
                missing_items.append('Skills')
            profile_completion += 25 if profile.profile_image else 0
            if not profile.profile_image:
                missing_items.append('Profile Image')
            profile_completion += 25 if profile.portfolio_link else 0
            if not profile.portfolio_link:
                missing_items.append('Portfolio Link')
        else:
            missing_items = ['Bio', 'Skills', 'Profile Image', 'Portfolio Link']

        # 3. Active Jobs (in_progress status or accepted bids)
        active_bids = Bid.query.filter_by(freelancer_id=current_user.id, status='accepted').all()
        active_jobs = []
        for bid in active_bids:
            job = bid.job
            if job and job.status in ['open', 'in_progress']:
                active_jobs.append({
                    'id': job.id,
                    'title': job.title,
                    'client_name': job.client.name if job.client else 'Unknown',
                    'status': job.status,
                    'deadline': job.deadline,
                    'bid_id': bid.id,
                    'bid_amount': bid.amount
                })

        # 4. My Bids
        recent_bids = Bid.query.filter_by(freelancer_id=current_user.id).order_by(Bid.created_at.desc()).limit(10).all()
        my_bids = []
        for bid in recent_bids:
            job = bid.job
            if job:
                my_bids.append({
                    'id': bid.id,
                    'job_title': job.title,
                    'job_id': job.id,
                    'amount': bid.amount,
                    'status': bid.status,
                    'created_at': bid.created_at
                })

        # 5. Payment Status
        payments = Payment.query.filter_by(freelancer_id=current_user.id).order_by(Payment.created_at.desc()).limit(10).all()
        payment_info = []
        for payment in payments:
            job = payment.job
            if job:
                payment_info.append({
                    'job_name': job.title,
                    'job_id': job.id,
                    'amount': payment.amount,
                    'status': payment.status,
                    'created_at': payment.created_at
                })

        # 6. Reviews & Ratings
        reviews = Review.query.filter_by(freelancer_id=current_user.id).order_by(Review.id.desc()).limit(10).all()
        review_list = []
        for review in reviews:
            if review.client_reviewer:
                review_list.append({
                    'client_name': review.client_reviewer.name,
                    'rating': review.rating,
                    'comment': review.comment,
                    'job_title': review.job.title if review.job else 'Unknown Job'
                })

        return render_template('freelancer-dashboard.html',
                             # KPIs
                             bids_count=bids_count,
                             accepted_bids=accepted_bids,
                             earnings=earnings,
                             avg_rating=avg_rating,
                             # Profile
                             profile_completion=profile_completion,
                             missing_items=missing_items,
                             # Active Jobs
                             active_jobs=active_jobs,
                             # Bids
                             my_bids=my_bids,
                             # Payments
                             payment_info=payment_info,
                             # Reviews
                             reviews=review_list)
    
    @app.route('/transactions')
    @login_required
    def transactions():
        """View transaction history"""
        page = request.args.get('page', 1, type=int)
        
        if current_user.is_freelancer():
            pagination = Payment.query.filter_by(freelancer_id=current_user.id).order_by(Payment.created_at.desc()).paginate(page=page, per_page=10)
        else:
            pagination = Payment.query.filter_by(client_id=current_user.id).order_by(Payment.created_at.desc()).paginate(page=page, per_page=10)
        
        payments = pagination.items
        return render_template('transactions.html', payments=payments, pagination=pagination)
    
    # ================== ERROR HANDLERS ==================
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('403.html'), 403
    
    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(debug=os.environ.get('FLASK_ENV') == 'development')
