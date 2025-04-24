from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import requests
import os

app = Flask(__name__)

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "unidavi")
POSTGRES_DB = os.getenv("POSTGRES_DB", "PERSONAL_LIBRARY")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

book_author = db.Table('book_author',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id', ondelete='CASCADE'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    reviews = db.relationship('Review', backref='user', lazy=True, cascade="all, delete")

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    books = db.relationship('Book', backref='genre', lazy=True)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    books = db.relationship('Book', secondary=book_author, back_populates='authors')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id', ondelete='SET NULL'))
    authors = db.relationship('Author', secondary=book_author, back_populates='books')
    reviews = db.relationship('Review', backref='book', lazy=True, cascade="all, delete")

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id', ondelete='CASCADE'))

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user = User(name=data['name'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created', 'id': user.id}), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'name': user.name})

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.name = data['name']
    db.session.commit()
    return jsonify({'message': 'User updated'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    genre = Genre.query.filter_by(name=data['genre']).first()
    if not genre:
        genre = Genre(name=data['genre'])
        db.session.add(genre)
    book = Book(title=data['title'], genre=genre)
    db.session.add(book)
    for author_name in data.get('authors', []):
        author = Author.query.filter_by(name=author_name).first()
        if not author:
            author = Author(name=author_name)
            db.session.add(author)
        book.authors.append(author)
    db.session.commit()
    return jsonify({'message': 'Book added', 'id': book.id}), 201

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify({
        'id': book.id,
        'title': book.title,
        'genre': book.genre.name if book.genre else None,
        'authors': [author.name for author in book.authors]
    })

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.json
    book.title = data['title']
    if 'genre' in data:
        genre = Genre.query.filter_by(name=data['genre']).first()
        if not genre:
            genre = Genre(name=data['genre'])
            db.session.add(genre)
        book.genre = genre
    if 'authors' in data:
        book.authors = []
        for author_name in data['authors']:
            author = Author.query.filter_by(name=author_name).first()
            if not author:
                author = Author(name=author_name)
                db.session.add(author)
            book.authors.append(author)
    db.session.commit()
    return jsonify({'message': 'Book updated'})

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})

@app.route('/authors', methods=['POST'])
def create_author():
    data = request.json
    author = Author(name=data['name'])
    db.session.add(author)
    db.session.commit()
    return jsonify({'message': 'Author created', 'id': author.id}), 201

@app.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    author = Author.query.get_or_404(author_id)
    return jsonify({'id': author.id, 'name': author.name})

@app.route('/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    author = Author.query.get_or_404(author_id)
    data = request.json
    author.name = data['name']
    db.session.commit()
    return jsonify({'message': 'Author updated'})

@app.route('/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    return jsonify({'message': 'Author deleted'})

@app.route('/genres', methods=['POST'])
def create_genre():
    data = request.json
    genre = Genre(name=data['name'])
    db.session.add(genre)
    db.session.commit()
    return jsonify({'message': 'Genre created', 'id': genre.id}), 201

@app.route('/genres/<int:genre_id>', methods=['GET'])
def get_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    return jsonify({'id': genre.id, 'name': genre.name})

@app.route('/genres/<int:genre_id>', methods=['PUT'])
def update_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    data = request.json
    genre.name = data['name']
    db.session.commit()
    return jsonify({'message': 'Genre updated'})

@app.route('/genres/<int:genre_id>', methods=['DELETE'])
def delete_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    db.session.delete(genre)
    db.session.commit()
    return jsonify({'message': 'Genre deleted'})

@app.route('/reviews', methods=['POST'])
def add_review():
    data = request.json
    review = Review(
        rating=data['rating'],
        comment=data.get('comment'),
        user_id=data['user_id'],
        book_id=data['book_id']
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({'message': 'Review added', 'id': review.id}), 201

@app.route('/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    review = Review.query.get_or_404(review_id)
    return jsonify({
        'id': review.id,
        'rating': review.rating,
        'comment': review.comment,
        'user_id': review.user_id,
        'book_id': review.book_id
    })

@app.route('/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    data = request.json
    review.rating = data['rating']
    review.comment = data.get('comment', review.comment)
    db.session.commit()
    return jsonify({'message': 'Review updated'})

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted'})

@app.route('/books', methods=['GET'])
def list_books():
    books = Book.query.all()
    result = []
    for book in books:
        result.append({
            'id': book.id,
            'title': book.title,
            'genre': book.genre.name if book.genre else None,
            'authors': [author.name for author in book.authors]
        })
    return jsonify(result)

@app.route('/recommend_books', methods=['GET'])
def recommend_books():
    title_query = request.args.get('title')
    genre_query = request.args.get('genre')
    limit = int(request.args.get('limit', 10))
    query_terms = []
    if title_query:
        query_terms.append(f"intitle:{title_query}")
    if genre_query:
        query_terms.append(f"subject:{genre_query}")
    search_query = "+".join(query_terms)
    params = {
        "q": search_query,
        "maxResults": limit,
        "key": os.getenv("GOOGLE_BOOKS_API_KEY")
    }
    url = "https://www.googleapis.com/books/v1/volumes"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        filtered_items = []
        for item in data.get("items", []):
            info = item.get("volumeInfo", {})
            filtered_items.append({
                "title": info.get("title"),
                "description": info.get("description"),
                "link": info.get("infoLink"),
                "authors": info.get("authors")
            })
        return jsonify({"items": filtered_items})
    return jsonify({"error": "Error fetching data"}), response.status_code

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)