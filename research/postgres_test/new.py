"""Test module."""

from models import Review
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://test:test@localhost:5432/test')
Session = sessionmaker(bind=engine)
session = Session()


# user = session.execute(select(User).where(User.id == '02b09793-ee03-437c-9c00-e0fba214da3b')).fetchone()
# review = session.query(Review).filter(Review.user_id == '4ec2f987-9ba7-413f-b691-4d034e2a948e').first()
# # reviews = len(user.reviews)
# print(review.text)

user_reviews_count = session.query(Review).filter(Review.user_id == '4ec2f987-9ba7-413f-b691-4d034e2a948e').count()

print(user_reviews_count)
