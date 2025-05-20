from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    date_of_death = Column(Date, nullable=True)

    books = relationship('Book', back_populates='author', cascade='all, delete-orphan')

class Book(db.Model):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True)
    isbn = Column(String(20), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    publication_year = Column(String(4), nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'), nullable=False)

    author = relationship('Author', back_populates='books')
