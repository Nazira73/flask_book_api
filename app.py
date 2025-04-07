from flask import Flask, jsonify, request

app = Flask(__name__)

books = []
next_id = 1  # Used to generate unique book IDs

# Add initial book
books.append({'id': 1, 'title': 'Let us C', 'author': 'Yashwant Kanetkar'})
next_id += 1

@app.route("/books", methods=['GET', 'POST'])
def handle_books():
    global next_id
    if request.method == 'GET':
        return jsonify(books)
    elif request.method == 'POST':
        data = request.get_json()
        for book in data:
            book['id'] = next_id
            next_id += 1
            books.append(book)
        return jsonify({"message": "Books added successfully", "books": data}), 201

@app.route("/books/<int:book_id>", methods=['PUT', 'PATCH', 'DELETE'])
def modify_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    if request.method == 'PUT':
        new_data = request.get_json()
        book.update({
            'title': new_data.get('title'),
            'author': new_data.get('author')
        })
        return jsonify({"message": "Book replaced successfully", "book": book})

    elif request.method == 'PATCH':
        updates = request.get_json()
        book.update(updates)
        return jsonify({"message": "Book updated successfully", "book": book})

    elif request.method == 'DELETE':
        books.remove(book)
        return jsonify({"message": "Book deleted successfully", "book": book})

if __name__ == "__main__":
    app.run(debug=True)