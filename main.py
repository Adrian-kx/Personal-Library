from flask import Flask, request, jsonify
import json
import random

app = Flask(__name__)

# Função para carregar livros do arquivo
def load_books():
    try:
        with open("books.json", "r") as file:
            books = json.load(file)
    except FileNotFoundError:
        books = []
    return books

# Função para salvar livros no arquivo
def save_books(books):
    with open("books.json", "w") as file:
        json.dump(books, file, indent=4)

# Endpoint para adicionar um livro
@app.route('/add_book', methods=['POST'])
def add_book():
    data = request.json
    title = data.get('title')
    genre = data.get('genre')

    if not title or not genre:
        return jsonify({"error": "Title and genre are required"}), 400

    # Carregar os livros existentes
    books = load_books()

    # Criar um novo livro
    new_book = {
        "title": title,
        "genre": genre
    }

    # Adicionar o novo livro à lista e salvar
    books.append(new_book)
    save_books(books)

    return jsonify({"message": "Book added successfully"}), 201

# Endpoint para listar seus livros e obter 3 indicações
@app.route('/my_books', methods=['GET'])
def my_books():
    books = load_books()
    if not books:
        return jsonify({"message": "No books found."}), 404

    # Seleciona 3 livros aleatórios para indicações
    recommended_books = random.sample(books, min(3, len(books)))

    return jsonify({
        "my_books": books,
        "recommended_books": recommended_books
    })

# Endpoint para indicar livros com base no título e gênero
@app.route('/recommend_books', methods=['GET'])
def recommend_books():
    title_query = request.args.get('title')
    genre_query = request.args.get('genre')
    limit = int(request.args.get('limit', 20))

    if not title_query and not genre_query:
        return jsonify({"error": "Please provide a title or genre for recommendations"}), 400

    # Carregar livros e encontrar indicações
    books = load_books()

    # Filtrar livros com base no título ou gênero
    recommendations = [book for book in books if title_query.lower() in book['title'].lower() or genre_query.lower() in book['genre'].lower()]

    # Limitar a quantidade de livros recomendados
    recommendations = recommendations[:limit]

    return jsonify({"recommended_books": recommendations})

if __name__ == '__main__':
    app.run(debug=True)
