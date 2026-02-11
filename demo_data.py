"""
Demo data script to populate the database with sample jobs, users, and bids.
Run this from the project root: python demo_data.py
"""

from app import create_app, db
from models import User, FreelancerProfile, Job, Bid, Payment, Review, WorkSubmission
from datetime import datetime, timedelta


def create_demo_data():
    app = create_app()

    with app.app_context():
        # Reset database
        db.drop_all()
        db.create_all()

        # Create 5 clients
        clients = []
        client_names = ["Saro", "Boost", "Akash", "Abdul", "Vishal"]
        for i, name in enumerate(client_names, start=1):
            u = User(name=name, email=f"client{i}@example.com", role="client")
            u.set_password("password123")
            clients.append(u)

        # Create 5 freelancers
        freelancers = []
        freelancer_names = ["Kiran", "Sachin", "Nishanth", "Pravin", "Vishnu"]
        for i, name in enumerate(freelancer_names, start=1):
            u = User(name=name, email=f"freelancer{i}@example.com", role="freelancer")
            u.set_password("password123")
            freelancers.append(u)

        db.session.add_all(clients + freelancers)
        db.session.commit()

        # Create freelancer profiles
        profiles = []
        profiles.append(FreelancerProfile(user_id=freelancers[0].id, bio="Backend developer with 5+ years building APIs and integrations.", skills="Python,Flask,SQL", avg_rating=4.6, total_reviews=12))
        profiles.append(FreelancerProfile(user_id=freelancers[1].id, bio="Mobile and web developer focused on performance and UX.", skills="JavaScript,React,React Native", avg_rating=4.5, total_reviews=9))
        profiles.append(FreelancerProfile(user_id=freelancers[2].id, bio="Full-stack engineer experienced in MERN stack and cloud deployment.", skills="Node,Express,React,AWS", avg_rating=4.7, total_reviews=15))
        profiles.append(FreelancerProfile(user_id=freelancers[3].id, bio="UI/UX specialist and prototyper who designs clear user journeys.", skills="Figma,Prototyping,Design Systems", avg_rating=4.4, total_reviews=7))
        profiles.append(FreelancerProfile(user_id=freelancers[4].id, bio="SEO & content strategist delivering measurable traffic growth.", skills="SEO,Content,Analytics", avg_rating=4.8, total_reviews=18))

        db.session.add_all(profiles)
        db.session.commit()

        # Create 2-3 different jobs per client — all left as 'open'
        jobs = []
        jobs_per_client = {
            0: [
                ("Local Business Website", "Build a responsive website for a local business.", 35000, "web", 21),
                ("Landing Page A/B Test", "Create 2 landing page variants for conversion testing.", 7000, "design", 10),
                ("SEO Basics", "On-page SEO fixes and basic optimization.", 9000, "marketing", 14),
            ],
            1: [
                ("Product Upload & Optimization", "Upload and optimize 150 product listings.", 12000, "data", 7),
                ("4-week Social Campaign", "Create assets and copy for a 4-week campaign.", 22000, "marketing", 21),
            ],
            2: [
                ("Company Blog Setup", "Setup blog with templates and initial 5 posts.", 15000, "writing", 14),
                ("Product Photography Edit", "Edit and optimize 50 product photos.", 10000, "design", 12),
                ("Content Calendar", "Create a 3-month content calendar and briefs.", 8000, "writing", 10),
            ],
            3: [
                ("CRM Integration", "Integrate CRM with contact forms and workflows.", 40000, "web", 20),
                ("Dashboard Analytics", "Build dashboard to surface key metrics.", 45000, "web", 28),
            ],
            4: [
                ("Brand Guidelines", "Create simple brand guidelines and color palette.", 9000, "design", 9),
                ("Ad Banner Set", "Design 10 ad banners in multiple sizes.", 5000, "design", 6),
                ("Packaging Mockups", "Create 3 packaging mockups for product line.", 15000, "design", 11),
            ],
        }

        for client_idx, job_list in jobs_per_client.items():
            client = clients[client_idx]
            for title, desc, budget, category, days in job_list:
                jobs.append(Job(
                    client_id=client.id,
                    title=title,
                    description=desc,
                    budget=budget,
                    category=category,
                    deadline=datetime.utcnow() + timedelta(days=days),
                    status="open",
                ))

        db.session.add_all(jobs)
        db.session.commit()

        # Create bids: every freelancer bids on every job, leave all statuses as pending
        bids = []
        for job in jobs:
            # ensure job stays 'open'
            job.status = 'open'
        db.session.commit()

        for job in jobs:
            for idx, freelancer in enumerate(freelancers, start=1):
                amount = max(100, int(job.budget * (0.75 + 0.05 * idx)))
                proposal = f"Proposal by {freelancer_names[idx-1]} for {job.title}"
                b = Bid(job_id=job.id, freelancer_id=freelancer.id, amount=amount, proposal=proposal, delivery_days=7 + idx, status='pending')
                bids.append(b)

        db.session.add_all(bids)
        db.session.commit()

        print("Demo data created successfully!")
        print("\nTest Accounts:")
        print("Clients:")
        for i, c in enumerate(clients, start=1):
            print(f"  - client{i}@example.com / password123")
        print("Freelancers:")
        for i, f in enumerate(freelancers, start=1):
            print(f"  - freelancer{i}@example.com / password123")
        print(f"\nJobs created: {len(jobs)}")
        print(f"Bids created: {len(bids)}")
        print(f"Users created: {db.session.query(User).count()}")


if __name__ == "__main__":
    create_demo_data()
