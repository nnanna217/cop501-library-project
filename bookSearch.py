############################
# COP 501 Coursework
# Author - F218341
############################
"""
Module to handles ---

Class
-----
Book

"""
import database as db
"""

"""

class Book:
    """

    :Attributes
    -----------
    genre_id = genre_id
    name = name
    purchase_price
    purchase_date

    :Methods
    --------
    get_by_title
    get_by_genre
    get_all
    get_books_by_bookid
    get_books_by_id
    is_valid_bookid
    is_available
    is_reserved
    is_loaned
    get_waitlist
    get_similar_books
    get_loaned_books
    get_available_books

    """
    def __int__(self, genre_id=None, name=None, purchase_price=None, purchase_date=None):
        self.genre_id = genre_id
        self.name = name
        self.purchase_price = purchase_price
        self.purchase_date = purchase_date


    @staticmethod
    def get_by_title(search_string):
        """
        Returns book records from the database
        :param search_string: Specifies the book title
        :return: a tuple containing a boolean flag (true or false) & a string of the results
        """
        query_string = db.SQLStatements().build_query('books', 'fetch_title', title=search_string)
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        return flag, result

    @staticmethod
    def get_by_genre(search_string):
        """
        Returns book records from the database
        :param search_string: Specifies the genre
        :return: a tuple containing a boolean flag (true or false) & a string of the results
        """
        query_string = db.SQLStatements().build_query('books', 'fetch_title', title=search_string)
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        return flag, result

    @staticmethod
    def get_all():
        """
        Returns book records from the database
        :param search_string: Specifies the genre
        :return: a tuple containing a boolean flag (true or false) & a string of the results
        """
        query_string = db.SQLStatements().build_query('books', 'fetch')
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        return flag, result

    @staticmethod
    def get_books_by_bookid(bookid, status_id):
        query_string = db.SQLStatements().build_query('book_loans', 'fetch_book_by_bookid', bookid=bookid,
                                                      status_id=status_id)
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        return flag, result

    @staticmethod
    def get_book_by_id(bookid):
        query_string = db.SQLStatements().build_query('books', 'is_available', bookid=bookid)
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        return flag, result


    @staticmethod
    def is_valid_bookid(bookid):
        query_string = db.SQLStatements().build_query('books', 'fetch_by_id', bookid=bookid)
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        if flag and len(result) > 0:
            return True
        else:
            return False

    @staticmethod
    def is_available(bookid):
        query_string = db.SQLStatements().build_query('books', 'is_available', bookid=bookid)
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        if flag and len(result) > 0:
            return True
        else:
            return False

    @staticmethod
    def is_reserved(bookid):
        query_string = db.SQLStatements().build_query('book_reservations', 'is_reserved', bookid=bookid)
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        if flag and len(result) > 0:
            return True
        else:
            return False

    @staticmethod
    def is_loaned(bookid):
        query_string = db.SQLStatements().build_query('books', 'is_loaned', bookid=bookid)
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        if flag and len(result) > 0:
            return True
        else:
            return False

    @staticmethod
    def get_waitlist(bookid):
        return True

    @staticmethod
    def get_similar_books(bookid):
        query_string = db.SQLStatements().build_query('books', 'get_similar_books', bookid=bookid)
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        return flag, result

    @staticmethod
    def get_loaned_books():
        query_string = db.SQLStatements().build_query('book_loans', 'fetch_loaned_books')
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        return flag, result

    @staticmethod
    def get_available_books():
        query_string = db.SQLStatements().build_query('book_loans', 'fetch_available_books')
        flag, result = db.Database().run_sql_statement(sql_statement=query_string)
        return flag, result


def test_book_search():
    book_title = input("Enter Book Title: ")
    flag, result = Book.get_by_title(search_string=book_title)
    print(result)
    print("-"*50)

    return
def main():
    test_book_search()
    # flag, result = Book.get_all()
    # print(result)
    # print(Book.is_reserved(10012))
    # print(Book.is_valid_bookid(1001))
    # print(Book.is_available(1002))
    # flag, result = Book.get_available_books()


if __name__ == '__main__':
    main()