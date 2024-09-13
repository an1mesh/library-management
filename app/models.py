from sqlobject import SQLObject, IntCol, StringCol, ForeignKey, RelatedJoin, BoolCol

class Books(SQLObject):
    status = StringCol(default='available')
    issue_count = IntCol(default=0)
    quantity = IntCol(default=0)
    details = ForeignKey('BookDetails')  # one-to-one relationship with BookDetails
class BookDetails(SQLObject):
    book_name = StringCol()
    author = ForeignKey('Authors')  # many-to-one relationship with Authors
    isbn = StringCol()
    books = RelatedJoin('Books')  # Reverse relationship from Books

class Authors(SQLObject):
    author_name = StringCol()
    books = RelatedJoin('BookDetails')  # Reverse relationship from BookDetails

class Transactions(SQLObject):
    book = ForeignKey('Books')  # many-to-one relationship with Books
    member = ForeignKey('Members')  # many-to-one relationship with Members
    issue_date = StringCol()
    return_date = StringCol()
    fee = IntCol()
    is_issued = IntCol()

class Members(SQLObject):
    user = ForeignKey('Users')  # one-to-one relationship with Users
    amount_paid = IntCol(notNone=True)
    debt = IntCol(default=0)

class Users(SQLObject):
    username = StringCol(unique=True)
    password = StringCol(notNone=True)
    is_member = BoolCol(notNone=True)
    member = RelatedJoin('Members')  # Reverse relationship from Members
    

def setup_db():
    Books.createTable(ifNotExists=True)
    BookDetails.createTable(ifNotExists=True)
    Authors.createTable(ifNotExists=True)
    Members.createTable(ifNotExists=True)
    Transactions.createTable(ifNotExists=True)
    Users.createTable(ifNotExists=True)
