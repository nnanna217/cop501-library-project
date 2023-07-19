############################
# COP 501 Coursework
# Author - F218341
############################
"""
Module to handles ---

Functions
---------
    return_book(bookid)
    notify_if_reserved(bookid)

"""

import datetime
import database as d
from bookSearch import Book


def return_book(bookid):
    """
    Returns checkout books providing the id is valid and the book has previously been checked out
    :param bookid: bookid to be returned
    :return: Tuple (type: boolean, str, dataframe)
    """
    message = ""
    flag = False
    result = ""
    statement = d.SQLStatements()
    today = str(datetime.date.today())

    if not Book.is_valid_bookid(bookid) or Book.is_available(bookid):
        message = "Error - This book cannot be returned as it is an invalid selection OR was never checked out"
        flag = "booked"
        print(message)
        return flag, message, result
    else:
        flag, result = Book.get_books_by_bookid(bookid, d.Status.LOANED.value)
        # Update the table view
    member_id = result.member_id.values[0]
    query = statement.build_query('book_loans', 'return_book', return_date=today, modified_date=today,
                                  status_id=d.Status.AVAILABLE.value, bookid=bookid)
    flag, success = statement.execute(query)
    message = "Book has been returned"
    print(message)
    # add log query that the book has been returned
    d.Logger.log(bookid, member_id, d.LogAction.BOOK_RETURNED.value, today)
    return flag, message, result


def notify_if_reserved(bookid):
    return Book.is_reserved(bookid)


if __name__ == '__main__':
    # Sample data for reserved books - range(1000, 1039)
    # Sample data for loaned/checked out books - range (1040, 1139)
    # Sample data for Available books - range (1000, 1039) and range (1140, 1549)
    bookid = input("Enter a bookid: ")
    assert isinstance(return_book(bookid), tuple)
    assert isinstance(notify_if_reserved(bookid), bool)
    if notify_if_reserved(bookid):
        print(f"{bookid} is reserved")
    else:
        print(f"{bookid} is not reserved")

