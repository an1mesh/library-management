import requests

def import_books(api_url,params):
    response = requests.get(api_url,params=params)
    
    if response.status_code == 200:
        return response.json()
    
    return None


def insert_books(book_data):
    from app.models import Books
    
    for book in book_data:
        Books(title=book['title'], author=book['author'], isbn=book['isbn'], 
              publisher=book['publisher'], pages=book['pages'], quantity=book.get('quantity', 1))