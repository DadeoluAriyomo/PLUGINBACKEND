from app import create_app, db
from app.models.category import Category


categories = [
    "Business Registration & Compliance",
    "Branding, Design & Identity",
    "Digital & Creative Economy",
    "Website, App & Software Development",
    "Digital Marketing & E-Commerce",
    "Video, Film & Entertainment",
    "Media, Talent & Influencer Services",
    "Music & Audio Production",
    "Writing, Editing & Publishing",
    "Education, Coaching & Personal Development",
    "Fashion & Beauty",
    "Home & Lifestyle",
    "Agriculture & Agro-Tech",
    "Transport & Logistics",
    "Local Services & Errands",
    "Health, Wellness & Fitness",
    "Legal & Financial Services",
    "Luxury & VIP Services",
    "Tourism & Hospitality",
    "DIY & Handcrafted Services"
]


app = create_app()

with app.app_context():

    for category_name in categories:

        existing_category = Category.query.filter_by(
            name=category_name
        ).first()

        if not existing_category:
            category = Category(
                name=category_name
            )

            db.session.add(category)

    db.session.commit()

    print("Categories seeded successfully!")