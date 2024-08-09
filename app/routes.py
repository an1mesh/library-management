from flask import Blueprint, make_response, redirect, request, jsonify, render_template
from fpdf import FPDF
from sqlobject.sqlbuilder import LIKE,DESC,AND
from app.models import Books, Members, Transactions

main_bp = Blueprint('main',__name__)

@main_bp.route('/')
def home():
    return render_template('index.html')

#CRUD ON BOOKS
@main_bp.route('/books',methods = ['GET','POST'])
def manage_books():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()

        elif request.content_type == 'application/x-www-form-urlencoded':
            data = request.form

        # On creating the object of book it automatically saves the the data (SQLObject feature)
        book = Books(
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            publisher=data['publisher'],
            pages=int(data['pages']),
            quantity=int(data['quantity'])
        )

        books = Books.select()
        return render_template('books.html',books=books)
        # return jsonify({'message':'Book added successfully','book_id':book.id}),201
    
    elif request.method == 'GET':
        books = Books.select()
        if not books:
            return jsonify({'message':'No books stored'})
        
        return render_template('books.html',books=books)
        # return jsonify([{
        #     'id': book.id,
        #     'title': book.title,
        #     'author': book.author,
        #     'isbn': book.isbn,
        #     'publisher': book.publisher,
        #     'pages': book.pages,
        #     'quantity': book.quantity,            
        #     } for book in books]),200
        
        
@main_bp.route('/books/<int:id>', methods=['GET','PUT','POST'])
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
            }),200
            
        elif request.method == 'PUT':
            data = request.get_json()
            book.set(
                title=data.get('title', book.title), author=data.get('author', book.author),
                 isbn=data.get('isbn', book.isbn), publisher=data.get('publisher', book.publisher),
                 pages=data.get('pages', book.pages), quantity=data.get('quantity', book.quantity)
            )
            
            return jsonify({'message':'Book updated successfully'}),202
        
        elif request.method == 'POST':
            query = Books.select(Transactions.q.book == book.id)
            if query.count() > 0:
                return jsonify({'message':'Book cannot deleted as its involved in a transaction right now'}),400
            book.destroySelf()
            
            return redirect('/books')
            # return jsonify({'message':'Book deleted'}),200


@main_bp.route('/books/update/<int:id>', methods=['GET','POST'])
def edit_book(id):
    book = Books.get(id)

    if request.method == 'POST':
        data = request.form
        book.set(
            title=data.get('title', book.title), author=data.get('author', book.author),
                isbn=data.get('isbn', book.isbn), publisher=data.get('publisher', book.publisher),
                pages=int(data.get('pages', book.pages)), quantity=int(data.get('quantity', book.quantity))
        )
        
        return redirect('/books')
    
    return render_template('/update.html', book=book)

# CRUD ON MEMBERS
@main_bp.route('/members',methods=['GET','POST'])
def manage_members():
    if request.method == 'POST':
        data = request.get_json()
        member = Members(
            name = data['name'],
            email = data['email']
        )
        
        return jsonify({'message':'Member added successfully','member_id':member.id}),201
    
    elif request.method == 'GET':
        members = Members.select()
        
        return jsonify([{
            'id':member.id,
            'name':member.name,
            'email':member.email,
            'debt':member.debt
        }for member in members]),200
        
@main_bp.route('/members/<int:id>', methods = ['GET','PUT','DELETE'])
def member_detail(id):
    member = Members.get(id)
    
    if request.method == 'GET':
        return jsonify({
            'id':member.id,
            'name':member.name,
            'email':member.email,
            'debt':member.debt
        }),200
        
    elif request.method == 'PUT':
        data = request.get_json()
        member.set(
            name=data.get('name', member.name), email=data.get('email', member.email),
                   debt=data.get('debt', member.debt)
        )
        
    elif request.method == 'DELETE':
        query = Transactions.select(AND(Transactions.q.member == member.id, Transactions.q.return_date == None))
        if query.count() > 0:
            return jsonify({'message':'member cannot be deleted he/she has an ongoing transaction'}),400
        member.destroySelf()
        
        return jsonify({'message':'member deleted'}),200
    

# ISSUE AND RETURN BOOKS    
@main_bp.route('/transactions/issue', methods=['POST'])
def issue_book():
    data = request.get_json()
    member = Members.select(Members.q.id == data['member_id']).getOne(None)
    book = Books.select(Books.q.id == data['book_id']).getOne(None)
    print(member)
    if member is None:
        return jsonify({'message':'No member found with this ID'}),404
    elif book is None:
        return jsonify({'message':'No book found with this ID'}),404
    elif member.debt > 500:
        return jsonify({'message':'Cannot issue book, the debt is more than Rs 500'}),406
    
    transaction = Transactions(
        member=data['member_id'], book=data['book_id'],
                               issue_date=data['issue_date'], return_date='',
                               fee=0
    )
    
    book = Books.get(data['book_id'])
    book.set(quantity=book.quantity-1)
    
    return jsonify({'message':'Book issued', 'transaction_id':transaction.id}),200

@main_bp.route('/transactions/return', methods=['POST'])
def return_book():
    data = request.get_json()
    transaction = Transactions.select(Transactions.q.id == data['transaction_id']).getOne(None)
    if transaction is None:
        return jsonify({'message':'No transaction found with this ID'})
    transaction = Transactions.get(data['transaction_id'])
    transaction.set(
        return_date=data['return_date'], fee=int(data['fee'])
    )
    
    book = Books.get(transaction.book)
    book.set(quantity=book.quantity+1)
    
    return jsonify({'message':'Book returned','transaction_id':transaction.id}),200


@main_bp.route('/books/search', methods = ['GET'])
def search_books():
    query = request.args.get('query','')
    books = Books.select(LIKE(Books.q.title,f'%{query}%') | LIKE(Books.q.author,f'%{query}%'))
    
    return jsonify([
        {'id': book.id, 'title': book.title, 'author': book.author,
                     'isbn': book.isbn, 'publisher': book.publisher, 'pages': book.pages,
                     'quantity': book.quantity} for book in books
    ]),200
    
# REPORTS 
@main_bp.route('/reports/popular_books', methods = ['GET'])
def popular_books():
    books = Books.select(orderBy=DESC(Books.q.quantity))
    if books.count() != 0:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', size=12)

        pdf.cell(200,10,txt='Popular books report', ln=True, align='C')

        pdf.cell(100,10,'Book Title', border=1)
        pdf.cell(40,10,'Quantity available',border=1,ln=True)

        for book in books:
            pdf.cell(100, 10, book.title, border=1)
            pdf.cell(40, 10, str(book.quantity), border=1, ln=True)

        response = make_response(pdf.output(dest='S').encode('latin1'))
        response.headers.set('Content-Disposition', 'attachment', filename='popular_books_report.pdf')
        response.headers.set('Content-Type', 'application/pdf')

        return response
    
    else:
        return jsonify({'message':'No books in record'})
        # return jsonify([{'title': book.title, 'quantity_available': book.quantity} for book in books])


@main_bp.route('/reports/highest_paying_customers', methods = ['GET'])
def highest_paying_customers():
    members = Members.select(orderBy=DESC(Members.q.debt))
    if members.count() != 0:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial',size=12)

        pdf.cell(200,10,txt='Highest paying customers report', ln=True, align='C')

        pdf.cell(100,10,'Customer name',border=1)
        pdf.cell(50,10,'Debt (Rs.)',border=1,ln=True)

        for member in members:
            pdf.cell(100, 10, member.name, border=1)
            pdf.cell(50, 10, f"Rs. {member.debt:.2f}", border=1, ln=True)

        response = make_response(pdf.output(dest='S').encode('latin1'))
        response.headers.set('Content-Disposition', 'attachment', filename='highest_paying_customers_report.pdf')
        response.headers.set('Content-Type', 'application/pdf')
        return response
    else:
        return jsonify({'message':'No members to show'})
    # return jsonify([{'name': member.name, 'debt': member.debt} for member in members])
    
    

    
    
        
        