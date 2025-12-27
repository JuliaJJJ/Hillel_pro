from sqlalchemy import Column, Integer, String, Date, ForeignKey,Table
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    password = Column(String(120), nullable=False)
    email = Column(String(120), unique=True)
    login = Column(String(50), nullable=False, unique=True)
    phone_number = Column(String(20))
    photo = Column(String(255))
    additional_info = Column(String(255))
    birth_date = Column(Date)

    def __repr__(self):
        return f'<User {self.login!r}>'


class Actor(Base):
    __tablename__ = 'actor'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birth_day = Column(Date)
    death_day = Column(Date)
    description = Column(String(255))


class Film(Base):
    __tablename__ = 'film'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    poster = Column(String(255))
    description = Column(String(255))
    rating = Column(Integer, nullable=False)
    duration = Column(Integer)
    added_at = Column(Integer, nullable=False)
    country = Column(String(50), nullable=False)

    def __repr__(self):
        return f'<Film {self.name!r}>'


class Genre(Base):
    __tablename__ = 'genre'

    genre = Column(String(50), primary_key=True)


class GenreFilm(Base):
    __tablename__ = 'genre_film'

    id = Column(Integer, primary_key=True)
    genre_id = Column(String(50), ForeignKey('genre.genre'))
    film_id = Column(Integer, ForeignKey('film.id'))


class ActorFilm(Base):
    __tablename__ = 'actor_film'

    id = Column(Integer, primary_key=True)
    actor_id = Column(Integer, ForeignKey('actor.id'))
    film_id = Column(Integer, ForeignKey('film.id'))


class List(Base):
    __tablename__ = 'list'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(50), nullable=False)


class ListFilm(Base):
    __tablename__ = 'list_film'

    id = Column(Integer, primary_key=True)
    list_id = Column(Integer, ForeignKey('list.id'))
    film_id = Column(Integer, ForeignKey('film.id'))


class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey('film.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    grade = Column(Integer)
    description = Column(String(255))


class Country(Base):
    __tablename__ = 'country'

    country_name = Column(String(50), primary_key=True, unique=True)
