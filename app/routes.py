import io
from flask import Blueprint, make_response, redirect, request, jsonify, render_template, send_file
from flask_jwt_extended import create_access_token
from fpdf import FPDF
from sqlobject.sqlbuilder import LIKE,DESC,AND
from app.models import Books, Members, Transactions,Users,BookDetails,Authors
from werkzeug.security import generate_password_hash, check_password_hash
import http
from auth_middleware import token_required
from logger import CustomLogger

main_bp = Blueprint('main',__name__)
logger = CustomLogger()

@main_bp.route('/signup', methods = ['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        is_member = data['is_member']
        
        logger.critical('Logger in create_user function')
        confirm_password = data['confirm_password']
        
        if not username or not password or not confirm_password or not is_member:
            return jsonify({'message':'Username or password is missing or role not given'}),http.HTTPStatus.BAD_REQUEST
        
        if Users.select(Users.q.username == username).count() > 0:
            return jsonify({'message':'User already exists'}),http.HTTPStatus.CONFLICT
        if password == confirm_password:
            hashed_password = generate_password_hash(password)
            new_user = Users(username=username,password=hashed_password,is_member=is_member)
            if is_member:
                Members(user=new_user.id,amount_paid=0)
                
            return jsonify({'message':'User created successfully'}),http.HTTPStatus.CREATED
        
        return jsonify({'message':'password and confirm password mismatch'}),http.HTTPStatus.BAD_REQUEST
    
    except Exception as e:
        return jsonify({'message':str(e)}), http.HTTPStatus.INTERNAL_SERVER_ERROR
    
@main_bp.route('/signin', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        user = Users.select(Users.q.username == username).getOne(None)

        if not user or not check_password_hash(user.password,password):
            return jsonify({'message':'Invalid username/password'})
        
        access_token = create_access_token(identity=user.id, additional_claims={'user_id':user.id})
        return jsonify({
            'token':access_token,
        }),http.HTTPStatus.OK
    
    except Exception as e:
        logger.error(e)
        return jsonify({'message':'Something went wrong'}), http.HTTPStatus.INTERNAL_SERVER_ERROR
    
@main_bp.route('/add_book', methods=['POST'])
@token_required
def add_book(_):
    logger.info('Inside add book')
    try:
        data=request.get_json()
        book_name=data['book_name']
        author_name=data['author_name']
        isbn=data['isbn']
        quantity=data['quantity']
        
        author = Authors.selectBy(author_name=author_name).getOne(None)
        if author is None:
            author = Authors(author_name=author_name)
        logger.info(author)
        
        book_details = BookDetails.selectBy(book_name=book_name,author=author,isbn=isbn).getOne(None)
        if book_details is None:
            book_details = BookDetails(book_name=book_name,author=author,isbn=isbn)
        logger.info(book_details)
        
        existing_book = Books.selectBy(details=book_details).getOne(None)
        if existing_book:
            existing_book.set(quantity=existing_book.quantity+quantity)
            logger.info(existing_book)
            book_data = {
                'book_id': existing_book.id,
                'book_name': existing_book.details.book_name,
                'author_name': existing_book.details.author.author_name,
                'isbn': existing_book.details.isbn,
                'status': existing_book.status,
                'quantity': existing_book.quantity
            }

            response = {
                'message': 'Book quantity updated successfully',
                'book':book_data
            }
            return jsonify(response),http.HTTPStatus.CREATED
        else:
            new_book = Books(quantity=quantity, details=book_details)
            logger.info(new_book)
            book_data = {
                'book_id': new_book.id,
                'book_name': new_book.details.book_name,
                'author_name': new_book.details.author.author_name,
                'isbn': new_book.details.isbn,
                'status': new_book.status,
                'quantity': new_book.quantity
            }

            response = {
                'message': 'Book added successfully',
                'book':book_data
            }
            return jsonify(response), http.HTTPStatus.CREATED
        

    except Exception as e:
        logger.error(e)
        return jsonify({'message':str(e)}),http.HTTPStatus.BAD_REQUEST

@main_bp.route('/get_books',methods=['GET'])
@token_required
def get_books(_):
    try:
        page = int(request.args.get('page',1))
        per_page = int(request.args.get('per_page',10))
        start = (page - 1) * per_page
        end = start + per_page
        
        books = Books.select()[start:end]
        logger.info(books)
        
        books_list = [{
            'id': book.id,
            'status': book.status,
            'issue_count': book.issue_count,
            'quantity': book.quantity,
            'book_name': book.details.book_name,
            'author_name': book.details.author.author_name,
            'isbn': book.details.isbn
        } for book in books]
        
        total_books = Books.select().count()
        logger.info(total_books)
        
        response = {
            'page':page,
            'per_page':per_page,
            'total_books':total_books,
            'books': books_list
        }
        
        return jsonify(response),http.HTTPStatus.OK
        
    except Exception as e:
        return jsonify({'message':str(e)}),http.HTTPStatus.BAD_REQUEST
    
    
@main_bp.route('/books/<int:book_id>',methods=['GET'])
@token_required
def get_book_by_id(book_id):
    try:
        book = Books.get(book_id)
        logger.info(book)
        
        response = {
            'id': book.id,
            'status': book.status,
            'issue_count': book.issue_count,
            'quantity': book.quantity,
            'book_name': book.details.book_name,
            'author_name': book.details.author.author_name,
            'isbn': book.details.isbn
        }
        
        return jsonify(response)
    
    except Exception as e:  
        return jsonify({'message':str(e)})
    
    
@main_bp.route('/update/books/<int:book_id>',methods=['PATCH'])
@token_required
def update_book(book_id):
    try:
        data = request.get_json()
        book = Books.get(book_id)
        logger.info(book)
        
        if 'status' in data:
            book.status = data['status']
        
        if 'issue_count' in data:
            book.issue_count = data['issue_count']
        
        if 'quantity' in data:
            book.quantity = data['quantity']
        
        if 'details' in data:
            book.details = BookDetails.get(int(data['details']))
            
        if 'book_name' in data:
            book.details.book_name = data['book_name']
            
        if 'author_name' in data:
            book.details.author.author_name = data['author_name']
            
            
        updated_book_data = {
                'id': book.id,
                'status': book.status,
                'issue_count': book.issue_count,
                'quantity': book.quantity,
                'book_name': book.details.book_name,
                'author_name': book.details.author.author_name,
                'isbn': book.details.isbn
        }
        
        return jsonify({'book':updated_book_data,'message':'Book updated successfully'}),http.HTTPStatus.ACCEPTED
    
    except Exception as e:
        return jsonify({'message':'Something went wrong'}),http.HTTPStatus.BAD_REQUEST
    
@main_bp.route('/search_books',methods=['GET'])
@token_required
def search_books(_):
    try:
        query = request.args.get('query', '')  
        page = int(request.args.get('page', 1))  
        per_page = int(request.args.get('per_page', 10))  

        start = (page - 1) * per_page
        end = start + per_page

        books_query = Books.select(
            Books.q.details.book_name.contains(query) |
            Books.q.details.author.author_name.contains(query)
        ).orderBy(Books.details.book_name).limit(per_page)[start:end]
        
        total_books = Books.select(
            Books.q.details.book_name.contains(query) |
            Books.q.details.author.author_name.contains(query)
        ).count()

        books = [{
            'book_id': book.id,
            'book_name': book.details.book_name,
            'author': book.details.author.author_name,
            'isbn': book.details.isbn,
            'status': book.status,
            'issue_count': book.issue_count,
            'quantity': book.quantity
        } for book in books_query]


        response = {
            'page': page,
            'per_page': per_page,
            'total_books': total_books,
            'books': books
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({'message':str(e)})
    
@main_bp.route('/delete/books/<int:book_id>',methods=['DELETE'])
@token_required
def delete_book(book_id):
    try:
        book = Books.get(book_id)
        logger.info(book)
        if book.details:
            book.details.destroySelf()
        book.destroySelf()
        
        return jsonify({'message':'Book deleted successfully'}),http.HTTPStatus.OK
    
    except Exception as e:
        logger.error(e)
        return jsonify({'message':str(e)}),http.HTTPStatus.BAD_REQUEST
    
    
@main_bp.route('/members/<int:member_id>', methods=['GET'])
@token_required
def get_member(member_id):
    try:
        member = Members.get(member_id)
        if not member:
            return jsonify({'message': 'Member not found'}), http.HTTPStatus.NOT_FOUND

        user = Users.get(member.id)

        return jsonify({
            'member_id': member.id,
            'username': user.username,
            'amount_paid': member.amount_paid
        }), http.HTTPStatus.OK

    except Exception as e:
        return jsonify({'message': str(e)}), http.HTTPStatus.INTERNAL_SERVER_ERROR
    
    
@main_bp.route('/get_members',methods=['GET'])
@token_required
def get_members(_):
    try:
        page = int(request.args.get('page',1))
        per_page = int(request.args.get('per_page',10))
        start = (page - 1) * per_page
        end = start + per_page
        members = Members.select()[start:end]
        
        members_list = [{
            'member_id':member.id,
            'username':member.user.username,
            'amount_paid':member.amount_paid
        } for member in members]
        
        total_members = Members.select().count()
        
        return jsonify({
            'members':members_list,
            'page': page,
            'per_page':per_page,
            'total_members':total_members
        }),http.HTTPStatus.OK
        
    except Exception as e:
        return jsonify({'message':f"{e}"}),http.HTTPStatus.INTERNAL_SERVER_ERROR
    
    
@main_bp.route('/update/members/<int:member_id>',methods=['PATCH'])
@token_required
def update_member(member_id):
    try:
        data = request.get_json()
        member = Members.get(member_id)
        if not member:
            return jsonify({'message': 'Member not found'}), http.HTTPStatus.NOT_FOUND
        
        if 'amount_paid' in data:
            member.amount_paid = data['amount_paid']
        if 'username' in data:
            member.user.username = data['username']
            
        updated_member_data = {
            'username':member.user.username,
            'amount_paid':member.amount_paid
        }

        return jsonify({'message': 'Member updated successfully','member':updated_member_data}), http.HTTPStatus.OK

    except Exception as e:
        return jsonify({'message': str(e)}), http.HTTPStatus.INTERNAL_SERVER_ERROR
    
    
@main_bp.route('/issue_book', methods=['POST'])
@token_required
def issue_book(_):
    try:
        data = request.get_json()

        member_id = data.get('member_id')
        book_id = data.get('book_id')

        member = Members.get(member_id)
        if not member:
            return jsonify({'message': 'Member not found'}), http.HTTPStatus.NOT_FOUND

        book = Books.get(book_id)
        if not book:
            return jsonify({'message': 'Book not found'}), http.HTTPStatus.NOT_FOUND

        if book.quantity <= 0:
            return jsonify({'message': 'Book is out of stock','book':book.details.book_name}), http.HTTPStatus.EXPECTATION_FAILED

        if member.debt > 500:
            return jsonify({'message': 'Member has too much debt. Cannot issue book.'}), http.HTTPStatus.FORBIDDEN

        transaction = Transactions(
            book=book,
            member=member,
            issue_date=data.get('issue_date', 'N/A'),
            return_date=None,
            fee=0,
            is_issued=1
        )

        book.quantity -= 1
        book.issue_count += 1
        book_detail = {
            'book_name':book.details.book_name,
            'author_name':book.details.author.author_name,
            'quantity':book.quantity
        }
        return jsonify({
            'message': 'Book issued successfully',
            'transaction_id': transaction.id,
            'book':book_detail
        }), http.HTTPStatus.OK

    except Exception as e:
        return jsonify({'message': str(e)}), http.HTTPStatus.INTERNAL_SERVER_ERROR
    
    
@main_bp.route('/return_book', methods=['POST'])
@token_required
def return_book(_):
    try:
        data = request.get_json()

        transaction_id = data.get('transaction_id')
        return_date = data.get('return_date')

        transaction = Transactions.get(transaction_id)
        if not transaction:
            return jsonify({'message': 'Transaction not found'}), http.HTTPStatus.NOT_FOUND

        if transaction.is_issued == 0:
            return jsonify({'message': 'Book is already returned'}), http.HTTPStatus.FOUND

        book = transaction.book
        member = transaction.member

        fee = data.get('fee', 0)
        transaction.fee = fee

        transaction.return_date = return_date
        transaction.is_issued = 0

        book.quantity += 1
        member.debt += fee  

        return jsonify({
            'message': 'Book returned successfully',
            'transaction_id': transaction.id,
            'fee_charged': fee
        }), http.HTTPStatus.OK

    except Exception as e:
        return jsonify({'message': str(e)}), http.HTTPStatus.INTERNAL_SERVER_ERROR
    
    
@main_bp.route('/pay_debt', methods=['POST'])
@token_required
def pay_debt(_):
    try:
        data = request.get_json()

        user_id = data.get('user_id')
        payment_amount = data.get('amount')

        member = Members.select(Members.q.user == user_id).getOne(None)
        if not member:
            return jsonify({'message': 'Member not found'}), http.HTTPStatus.NOT_FOUND

        if payment_amount <= 0:
            return jsonify({'message': 'Payment amount must be positive'}), http.HTTPStatus.BAD_REQUEST
        
        if member.debt >= 0:
            if member.debt - payment_amount < 0:
                return jsonify({'message':'Do not pay more than your debt'}),http.HTTPStatus.NOT_ACCEPTABLE
            member.amount_paid += payment_amount
            member.debt -= payment_amount

        if member.debt < 0:
            member.debt = 0

        return jsonify({
            'message': 'Payment successful',
            'amount_paid': member.amount_paid,
            'debt_remaining': member.debt
        }), http.HTTPStatus.OK

    except Exception as e:
        return jsonify({'message': str(e)}), http.HTTPStatus.INTERNAL_SERVER_ERROR


@main_bp.route('/top_paying_customers_pdf',methods=['GET'])
@token_required
def top_paying_customers_pdf(_):
    try:
        logger.info('In top paying customers')
        top_customers = Members.select(orderBy=DESC(Members.q.amount_paid))
        logger.info(top_customers)
        customers = [{
            'username': customer.user.username,
            'amount_paid': customer.amount_paid,
            'debt': customer.debt
        } for customer in top_customers]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Top 5 Paying Customers', 0, 1, 'C')
        
        pdf.set_font('Arial', '', 12)
        for customer in customers:
            pdf.cell(0, 10, f"Username: {customer['username']}", 0, 1)
            pdf.cell(0, 10, f"Amount Paid: {customer['amount_paid']}", 0, 1)
            pdf.cell(0, 10, f"Debt: {customer['debt']}", 0, 1)
            pdf.cell(0, 10, '', 0, 1)  
        
        response = make_response(pdf.output(dest='S').encode('latin1'))
        response.headers.set('Content-Disposition', 'attachment', filename='highest_paying_customers_report.pdf')
        response.headers.set('Content-Type', 'application/pdf')
        return response
    
    except Exception as e:
        return jsonify({'message': str(e)}),http.HTTPStatus.BAD_REQUEST
    
    
@main_bp.route('/top_popular_books_pdf')
@token_required
def top_popular_books_pdf(_):
    try:
        popular_books = Books.select(orderBy=DESC(Books.q.issue_count))
        books = [{
            'book_name': book.details.book_name,
            'author': book.details.author.author_name,
            'isbn': book.details.isbn,
            'issue_count': book.issue_count,
            'quantity': book.quantity
        } for book in popular_books]

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Top 5 Popular Books', 0, 1, 'C')
        
        pdf.set_font('Arial', '', 12)
        for book in books:
            pdf.cell(0, 10, f"Book Name: {book['book_name']}", 0, 1)
            pdf.cell(0, 10, f"Author: {book['author']}", 0, 1)
            pdf.cell(0, 10, f"ISBN: {book['isbn']}", 0, 1)
            pdf.cell(0, 10, f"Issued Count: {book['issue_count']}", 0, 1)
            pdf.cell(0, 10, f"Quantity: {book['quantity']}", 0, 1)
            pdf.cell(0, 10, '', 0, 1)  
        
        response = make_response(pdf.output(dest='S').encode('latin1'))
        response.headers.set('Content-Disposition', 'attachment', filename='highest_paying_customers_report.pdf')
        response.headers.set('Content-Type', 'application/pdf')
        return response
    
    except Exception as e:
        return jsonify({'message':str(e)}),http.HTTPStatus.BAD_REQUEST  
