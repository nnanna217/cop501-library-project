############################
# COP 501 Coursework
# Author - F218341
############################
import datetime
import database as db
from bookSearch import Book


def get_similar_books(bookid):
    query_string = db.SQLStatements().build_query('books', 'get_similar_books', bookid=bookid)
    flag, result = db.Database().run_sql_statement(sql_statement=query_string)
    return flag, result


def checkout(member_id, bookid):
    """
    Implements checkout after all necessary checks have been made
    :param member_id: borrower id
    :param bookid: book to be checked out
    :return: None
    """
    statement = db.SQLStatements()
    today = str(datetime.date.today())
    if not Book.is_valid_bookid(bookid):
        print(f"Error - Invalid selection. Book with ID {bookid} does not exist")
    # elif Book.is_loaned(bookid) or Book.is_reserved(bookid):
    #     print(f"Book - {bookid} is currently available as it has been loaned/reserved")
    #     get_similar_books(bookid)
    else:
        query = statement.build_query('book_loans', 'check_out', checkout_date=today, created_date=today,
                                      status_id=db.Status.LOANED.value, bookid=bookid, member_id=member_id)

        flag, result = statement.execute(query)
        log = db.Logger.log(bookid, member_id, db.LogAction.BOOK_CHECKOUT.value, today)
        print("Book has been checked out", flag, result)

def add_to_waitlist(self):
    return


def remove_from_waitlist(self):
    return


def verify_checkout(bookid):
    """
    Checks if a book can be checked out. Validates if it's a valid number and if loaned or reserved
    :param bookid: bookid to be returned
    :return: Tuple (type: boolean, str, dataframe)
    """
    statement = db.SQLStatements()
    flag = False
    result = ""
    message = ""

    if not Book.is_valid_bookid(bookid):
        print(f"Error - Invalid selection. Book with ID {bookid} does not exist")
        message = f"Error - Invalid selection. Book with ID {bookid} does not exist"
    elif Book.is_loaned(bookid) or Book.is_reserved(bookid):
        flag, result = Book.get_similar_books(bookid)
        if len(result) > 0:
            message = f"Book - {bookid} is currently unavailable - Choose a similar book"
            print(message)
        else:
            message = f"No copy of {bookid} is currently available as it has been loaned or researved"
            print(message)
    else:
        flag, result = Book.get_book_by_id(bookid)
    print(flag, message, result)
    return flag, message, result


if __name__ == '__main__':
    # Sample data for reserved books - range(1000, 1039)
    # Sample data for loaned/checked out books - range (1040, 1139)
    # Sample data for Available books - range (1000, 1039) and range (1140, 1549)
    # Sample data for Similar books - 1040, 1041, 1032,1033, 1035, 1036, 1046, 1047, 1048, 1050, 1051, 1052, 1056, 1057
    bookid = input("Enter a bookid: ")
    a, b = get_similar_books(bookid)
    print(b)
    print("=" * 50)
    bookid2 = input("Enter a bookid: ")
    verify_checkout(bookid2)
    print("="*50)
    member_id= input("Enter a Member ID: ")
    bookid3 = input("Enter a Book ID: ")
    checkout(member_id=member_id, bookid=bookid3)
