from sqlobject import SQLObject, StringCol, IntCol

class Books(SQLObject):
    title = StringCol()
    author = StringCol()
    isbn = StringCol()
    publisher = StringCol()
    pages = IntCol()
    quantity = IntCol()

class Members(SQLObject):
    name = StringCol()
    email = StringCol()
    debt = IntCol(default=0)

class Transactions(SQLObject):
    member = IntCol()
    book = IntCol()
    issue_date = StringCol()
    return_date = StringCol()
    fee = IntCol()

def setup_db():
    Books.createTable(ifNotExists=True)
    Members.createTable(ifNotExists=True)
    Transactions.createTable(ifNotExists=True)