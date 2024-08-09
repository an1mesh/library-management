# Library Management System

This is a web-based Library Management System built using Flask and SQLObject. The system provides functionalities for managing books, members, transactions (book issuance and returns), and generating reports.

## Features

- **CRUD Operations on Books**: 
  - Add, view, update, and delete books from the library's catalog.
  
- **CRUD Operations on Members**:
  - Add, view, update, and delete members of the library.
  
- **Book Transactions**:
  - Issue books to members.
  - Return books and calculate fees.
  
- **Search Functionality**:
  - Search for books by title or author.
  
- **Reports**:
  - Generate reports on the most popular books.
  - Generate reports on the highest paying customers.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework.
- **SQLObject**: An Object-Relational Mapper (ORM) for Python that provides an easy-to-use interface to interact with the database.
- **FPDF**: A PDF generation library for Python, used for generating reports.
