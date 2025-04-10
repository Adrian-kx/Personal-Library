from flask import Flask, request, jsonify
import json
import random
import requests

app = Flask(__name__)

# Função para carregar livros do arquivo local (caso seja necessário para outros endpoints)
def load_books():
    try:
        with open("books.json", "r") as file:
            content = file.read().strip()
            if not content:
                return []  # Retorna uma lista vazia se o arquivo estiver vazio
            books = json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        books = []
    return books

# Função para salvar livros no arquivo local
def save_books(books):
    with open("books.json", "w") as file:
        json.dump(books, file, indent=4)

# Endpoint para adicionar um livro ao arquivo local
@app.route('/add_book', methods=['POST'])
def add_book():
    data = request.json
    title = data.get('title')
    genre = data.get('genre')

    if not title or not genre:
        return jsonify({"error": "Title and genre are required"}), 400

    # Carregar os livros existentes
    books = load_books()

    # Criar um novo livro e adicionar à lista
    new_book = {
        "title": title,
        "genre": genre
    }
    books.append(new_book)
    save_books(books)

    return jsonify({"message": "Book added successfully"}), 201

# Endpoint para listar os livros locais e obter 3 indicações aleatórias
@app.route('/my_books', methods=['GET'])
def my_books():
    books = load_books()
    if not books:
        return jsonify({"message": "No books found."}), 404

    return jsonify({
        "my_books": books
    })

# Endpoint para recomendar livros usando a API do Google Books e retornar apenas os campos desejados:
# nome, descricao, link do livro e autores.
@app.route('/recommend_books', methods=['GET'])
def recommend_books():
    title_query = request.args.get('title')
    genre_query = request.args.get('genre')
    # Define um valor padrão para o número máximo de resultados
    limit = int(request.args.get('limit', 20))

    if not title_query and not genre_query:
        return jsonify({"error": "Please provide a title or genre for recommendations"}), 400

    # Monta a query para a API do Google Books utilizando os operadores de busca:
    # - intitle: para o título
    # - subject: para o gênero
    query_terms = []
    if title_query:
        query_terms.append(f"intitle:{title_query}")
    if genre_query:
        query_terms.append(f"subject:{genre_query}")
    
    search_query = "+".join(query_terms)

    # Parâmetros para consulta na API do Google Books
    params = {
        "q": search_query,
        "key": "AIzaSyDF7nzWOqN_Pq8qWhB54yQjteh56ZrMLFI",
        "maxResults": limit
    }
    url = "https://www.googleapis.com/books/v1/volumes"
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        filtered_items = []
        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})
            filtered_item = {
                "nome": volume_info.get("title"),
                "descricao": volume_info.get("description"),
                "link": volume_info.get("infoLink"),
                "autores": volume_info.get("authors")
            }
            filtered_items.append(filtered_item)
        return jsonify({"items": filtered_items})
    else:
        return jsonify({"error": "Erro ao buscar dados na API do Google Books"}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
