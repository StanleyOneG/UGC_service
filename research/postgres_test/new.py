"""Test module."""


from models import Movie
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://test:test@localhost:5432/test')
Session = sessionmaker(bind=engine)
session = Session()


# user = session.execute(select(User).where(User.id == '02b09793-ee03-437c-9c00-e0fba214da3b')).fetchone()
# review = session.query(Review).filter(Review.user_id == '4ec2f987-9ba7-413f-b691-4d034e2a948e').first()
# # reviews = len(user.reviews)
# print(review.text)

# movie_id = (
#     session.query(UserMovieRating.rating, Movie.id)
#     .join(UserMovie, UserMovieRating.user_movie_id == UserMovie.id)
#     .join(Movie, UserMovie.movie_id == Movie.id)
#     .limit(5)
#     .all()
# )

# print(movie_id)

# movie = '6da592a9-3957-48f6-ae8b-af7a79db343d'

# movie_rating = (
#     session.query(func.avg(UserMovieRating.rating))
#     .join(UserMovie, UserMovieRating.user_movie_id == UserMovie.id)
#     .filter(UserMovie.movie_id == movie)
#     .scalar()
# )

# print(movie_rating)

# movies with rating 10
# movies = (
#     session.query(Movie)
#     .join(UserMovie, UserMovie.movie_id == Movie.id)
#     .join(UserMovieRating, UserMovieRating.user_movie_id == UserMovie.id)
#     .filter(UserMovieRating.rating == 10)
#     .limit(5)
#     .all()
# )
# print(movies)
# movie = 'a11440a5-dfe8-4455-bbeb-d8f53bf2d661'

# movie_rating = session.query(func.avg(UserMovieRating.rating)).filter(UserMovieRating.movie_id == movie).first()

# print(movie_rating)
# # print(movie_rating)

movies = [str(movie._asdict().get('id')) for movie in session.query(Movie.id).limit(4).all()]
print(movies)
