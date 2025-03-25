from db.base import Base
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class DismissedMovie(Base):
    __tablename__ = "dismissed_movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)


class RecommendedMovie(Base):
    __tablename__ = "recommended_movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genres = Column(String)
    original_language = Column(String)
    popularity = Column(Float)
    vote_average = Column(Float)
    vote_count = Column(Integer)
    first_air_date = Column(String)
    year = Column(String)
    tmdb_id = Column(Integer)
    image = Column(String)
    overview = Column(String)
    status = Column(String, default="")

    radarr_movie_id = Column(Integer, ForeignKey("radarr_movies.id"))

    radarr_movie = relationship("RadarrMovie", back_populates="recommended_movies")

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "genres": self.genres,
            "original_language": self.original_language,
            "popularity": self.popularity,
            "vote_average": self.vote_average,
            "vote_count": self.vote_count,
            "first_air_date": self.first_air_date,
            "year": self.year,
            "tmdb_id": self.tmdb_id,
            "image": self.image,
            "overview": self.overview,
            "status": self.status,
        }


class RadarrMovie(Base):
    __tablename__ = "radarr_movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    genres = Column(String)
    tmdb_id = Column(Integer)

    recommended_movies = relationship("RecommendedMovie", back_populates="radarr_movie")

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "genres": self.genres,
            "tmdb_id": self.tmdb_id,
        }
