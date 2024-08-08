from flask import Blueprint, request, jsonify
from sqlobject.sqlbuilder import LIKE
from app.models import Books, Members, Transactions

main_bp = Blueprint('main',__name__)

@main_bp.route('/books',methods = ['GET','POST'])
def manage_books():
    if request.method == 'POST':
        data = request.get_json()
        
        # On creating the object of book it automatically saves the the data (SQLObject feature)
        book = Books(
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            publisher=data['publisher'],
            pages=data['pages'],
            quantity=data['quantity']
        )

        return jsonify({'message':'Book added successfully','book_id':book.id})
    
    elif request.method == 'GET':
        books = Books.select()
        if not books:
            return jsonify({'message':'No books stored'})
        return jsonify([{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'publisher': book.publisher,
            'pages': book.pages,
            'quantity': book.quantity,            
            } for book in books])
        
        
@main_bp.route('/books/<int:id>', methods=['GET','PUT','DELETE'])
def book_detail(id):
    book = Books.get(id)
    
    if not book:
        return jsonify({'message':'Invalid ID'})
    
    else:
        if request.method == 'GET':
            return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'publisher': book.publisher,
            'pages': book.pages,
            'quantity': book.quantity,
            })
            
        elif request.method == 'PUT':
            data = request.get_json()
            book.set(
                title=data.get('title', book.title), author=data.get('author', book.author),
                 isbn=data.get('isbn', book.isbn), publisher=data.get('publisher', book.publisher),
                 pages=data.get('pages', book.pages), quantity=data.get('quantity', book.quantity)
            )
            
            return jsonify({'message':'Book updated successfully'})
        
        elif request.method == 'DELETE':
            book.destroySelf()
            
            return jsonify({'message':'Book deleted'})
            
@main_bp.route('/members',methods=['GET','POST'])
def manage_members():
    if request.method == 'POST':
        data = request.get_json()
        member = Members(
            name = data['name'],
            email = data['email']
        )
        
        return jsonify({'message':'Member added successfully','member_id':member.id})
    
    elif request.method == 'GET':
        members = Members.select()
        
        return jsonify([{
            'id':member.id,
            'name':member.name,
            'email':member.email,
            'debt':member.debt
        }for member in members])
        
@main_bp.route('/members/<int:id>', methods = ['GET','PUT','DELETE'])
def member_detail(id):
    member = Members.get(id)
    
    if request.method == 'GET':
        return jsonify({
            'id':member.id,
            'name':member.name,
            'email':member.email,
            'debt':member.debt
        })
        
    elif request.method == 'PUT':
        data = request.get_json()
        member.set(
            name=data.get('name', member.name), email=data.get('email', member.email),
                   debt=data.get('debt', member.debt)
        )
        
    elif request.method == 'DELETE':
        member.destroySelf()
        
        return jsonify({'message':'member deleted'})
    
    
@main_bp.route('/transactions/issue', methods=['POST'])
def issue_book():
    data = request.get_json()
    member = Members.get(data['member_id'])
    
    if member.debt > 500:
        return jsonify({'message':'Cannot issue book, the debt is more than Rs 500'})
    
    transaction = Transactions(
        member=data['member_id'], book=data['book_id'],
                               issue_date=data['issue_date'], return_date='',
                               fee=0
    )
    
    book = Books.get(data['book_id'])
    book.set(quantity=book.quantity-1)
    
    return jsonify({'message':'Book issued', 'transaction_id':transaction.id})


@main_bp.route('/transactions/return', methods=['POST'])
def return_book():
    data = request.get_json()
    transaction = Transactions.get(data['transaction_id'])
    transaction.set(
        return_date=data['return_date'], fee=data['fee']
    )
    
    book = Books.get(transaction.book)
    book.set(quantity=book.quantity+1)
    
    return jsonify({'message':'Book returned','transaction_id':transaction.id})


@main_bp.route('/books/search', methods = ['GET'])
def search_books():
    query = request.args.get('query','')
    books = Books.select(LIKE(Books.q.title,f'%{query}%') | LIKE(Books.q.author,f'%{query}%'))
    
    return jsonify([
        {'id': book.id, 'title': book.title, 'author': book.author,
                     'isbn': book.isbn, 'publisher': book.publisher, 'pages': book.pages,
                     'quantity': book.quantity} for book in books
    ])
    
    
@main_bp.route('/reports/popular_books', methods = ['GET'])
def popular_books():
    books = Books.select(orderBy=Books.q.quantity)
    return jsonify([{'title': book.title, 'quantity_available': book.quantity} for book in books])


@main_bp.route('/reports/highest_paying_customers', methods = ['GET'])
def highest_paying_customers():
    members = Members.select(orderBy=Members.q.debt.desc())
    return jsonify([{'name': member.name, 'debt': member.debt} for member in members])
    
    

    
    
        
        