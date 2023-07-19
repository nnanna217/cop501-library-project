############################
# COP 501 Coursework
# Author - F218341
############################
"""
Module to handle database interaction such as Dataloading (reading from a file), SQL statement query builder,
Fields
    ------
    this_file_path: Absolute path of the project
    base_dir: Base directory
    db_path: Path to the DB file
    book_path: Path to Book Metadata
    loan_history_path: Path to Loan History

Classes
-------
    Database,
    SQLStatements,
    Status(Enum),
    LogAction(Enum),
    Logger

Functions
---------
    test_sqlstatement(),
    test_db_loading(),
    test_loan_history_load(),
    random_date_generator(),
    write_to_file()
    read_book_file(),
    generate_loan_reservations()
    insertBLOB()
    readBlobData()
    get_image_path(file)
    insert_images()

"""
import numpy as np
import pandas as pd
import sqlite3
import os
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pickle
from enum import Enum
import datetime

# Define folder paths to allow cross OS compatibility
this_file_path = os.path.abspath(__file__)
base_dir = os.path.dirname(this_file_path)
db_path = os.path.join(base_dir, "datafiles", "Library.db")
book_path = os.path.join(base_dir, "datafiles", "Book_Info.txt")
loan_history_path = os.path.join(base_dir, "datafiles", "Loan_Reservation_History.txt")
img_dir = os.path.join(base_dir, "datafiles/images")
def_img_path = os.path.join(base_dir, "datafiles/images", "0.png")


class Database:
    """
    Fields
    ------
    db_Name:
    Methods
    -------
    set_db:
    get_db:
    get_connection:
    run_sql_statement:
    load_books:
    load_loan_reservation_history:

    """

    dbName = db_path

    def __int__(self, currentdb=db_path):
        self.dbName = currentdb

    def set_db(self, db_name):
        self.dbName = db_name

    def get_db(self):
        return self.dbName

    def get_connection(self):
        return sqlite3.connect(self.get_db())

    def run_sql_statement(self, sql_statement):
        """
        Executes a built SQLstatment query using pandas
        :param sql_statement: SQLStament object containing a query
        :return: Tuple (flag:boolean, result: dataframe)
        """
        global sqlite_connection
        flag = True
        try:
            sqlite_connection = sqlite3.connect(self.get_db())
            df = pd.read_sql(sql_statement, sqlite_connection)

        except sqlite3.Error as error:
            flag = False
            result = "DB error: " + str(error)
        finally:
            if sqlite_connection:
                sqlite_connection.close()

        return flag, df

    def load_books(self, file_name=book_path):
        """
        Reads txt files (Book_Info.txt) and loads into the database.Also creates reference tables - status & log-action.
        Pre-populate the books, status & log_action table with data.
        :param file_name: string value of the file
        :return: None
        """

        # Read file from txt file - Book_info & Loan_Reservation_History
        book_data = pd.read_csv(book_path, sep="|")
        book_data.rename(columns={
            "BookID": "BookID", "Name": "title", "Author": "author", "Price": "purchase_price", "Genre": "genre",
            "purchase_date": "purchase_date"
        }, inplace=True)

        # Create Reference Tables - Status, Logs_Actions table
        status = {"name": ['available', 'loaned', 'reserved']}
        log_actions = {"name": ['book_checkout', 'book_returned', 'book_reserved', 'book_reservation_cancelled']}
        status_df = pd.DataFrame(status)
        log_actions_df = pd.DataFrame(log_actions)

        # Insert records into db
        sqlite_connection = self.get_connection()
        book_data.to_sql("books", sqlite_connection, if_exists='replace', index=False)
        status_df.to_sql("status", sqlite_connection, if_exists='replace', index='id')
        log_actions_df.to_sql("log_actions", sqlite_connection, if_exists='replace', index='id')

        sqlite_connection.close()

    def load_loan_reservation_history(self):
        '''
        Reads txt files (Loan_history.txt) and loads into the database.
        Performs Data cleaning to segment data into the following
        - Reserved Only
        - Reserved & Checked Out
        - Checkout Only
        - Checked out & Returned
        - Reserved, Checked Out & Returned
        :param None
        :return: None
        '''
        db = Database()
        connection = db.get_connection()
        bk_history = pd.read_csv(loan_history_path, sep="|")

        # Fetch only reserved books from loan history
        reserved_only = bk_history[(bk_history['reservation_date'] != '--') &
                                   (bk_history['checkout_date'] == '--') & (bk_history['return_date'] == '--')]
        reserved_only['action_id'] = LogAction.BOOK_RESERVED.value
        reserved_only['created_date'] = datetime.date.today()

        # Fetch books that were reserved and checked out successfully
        reserved_checkouts = bk_history[(bk_history['reservation_date'] != '--') &
                                        (bk_history['checkout_date'] != '--') & (bk_history['return_date'] == '--')]
        reserved_checkouts['action_id'] = LogAction.BOOK_RESERVED.value
        reserved_checkouts['created_date'] = datetime.date.today()

        # Fetch books that weren't reserved, but checked out (walk-ins)
        checkout_only = bk_history[(bk_history['reservation_date'] == '--') &
                                   (bk_history['checkout_date'] != '--') & (bk_history['return_date'] == '--')]
        checkout_only['action_id'] = LogAction.BOOK_CHECKOUT.value
        checkout_only['created_date'] = datetime.date.today()

        # Fetch returned books (ie. checkout -> returned; reserved->checkout->returned)
        checkout_returns = bk_history[(bk_history['reservation_date'] == '--') &
                                   (bk_history['checkout_date'] != '--') & (bk_history['return_date'] != '--')]
        checkout_returns['action_id'] = LogAction.BOOK_RETURNED.value
        checkout_returns['created_date'] = datetime.date.today()

        reserved_returns = bk_history[(bk_history['reservation_date'] != '--') &
                                      (bk_history['checkout_date'] != '--') & (bk_history['return_date'] != '--')]
        reserved_returns['action_id'] = LogAction.BOOK_RETURNED.value
        reserved_returns['created_date'] = datetime.date.today()

        # Insert records into db (pre-populate books_inventory, book_reservations, & book logs tables)
        reserved_only[['bookid','member_id']].to_sql("book_reservations", connection, if_exists='append', index=False)
        reserved_only[['bookid','member_id','action_id','created_date']].to_sql("book_transaction_logs", connection,
                                                                                if_exists='append', index=False)

        reserved_checkouts['status_id'] = Status.LOANED.value
        reserved_checkouts[['bookid', 'member_id', 'checkout_date', 'created_date', 'status_id']]. \
            to_sql("book_loans", connection, if_exists='append', index=False)
        reserved_checkouts[['bookid', 'member_id', 'action_id', 'created_date']]. \
            to_sql("book_transaction_logs", connection, if_exists='append', index=False)
        reserved_checkouts['action_id'] = LogAction.BOOK_CHECKOUT.value
        reserved_checkouts[['bookid', 'member_id', 'action_id', 'created_date']]. \
            to_sql("book_transaction_logs", connection, if_exists='append', index=False)

        checkout_only['status_id'] = Status.LOANED.value
        checkout_only[['bookid', 'member_id', 'checkout_date', 'created_date', 'status_id']]. \
            to_sql("book_loans", connection, if_exists='append', index=False)
        checkout_only[['bookid', 'member_id', 'action_id', 'created_date']]. \
            to_sql("book_transaction_logs", connection, if_exists='append', index=False)

        checkout_returns['status_id'] = Status.AVAILABLE.value
        checkout_returns[['bookid', 'member_id', 'checkout_date', 'return_date', 'created_date', 'status_id']]. \
            to_sql("book_loans", connection, if_exists='append', index=False)
        checkout_returns[['bookid', 'member_id', 'action_id', 'created_date']].\
            to_sql("book_transaction_logs", connection, if_exists='append', index=False)
        checkout_returns['action_id'] = LogAction.BOOK_CHECKOUT.value
        checkout_returns[['bookid', 'member_id', 'action_id', 'created_date']]. \
            to_sql("book_transaction_logs", connection, if_exists='append', index=False)

        reserved_returns['status_id'] = Status.AVAILABLE.value
        reserved_returns[['bookid', 'member_id', 'checkout_date', 'return_date', 'created_date', 'status_id']]. \
            to_sql("book_loans", connection, if_exists='append', index=False)
        reserved_returns[['bookid', 'member_id', 'action_id', 'created_date']]. \
            to_sql("book_transaction_logs", connection, if_exists='append', index=False)
        reserved_returns['action_id'] = LogAction.BOOK_CHECKOUT.value
        reserved_returns[['bookid', 'member_id', 'action_id', 'created_date']]. \
            to_sql("book_transaction_logs", connection, if_exists='append', index=False)
        reserved_returns['action_id'] = LogAction.BOOK_RESERVED.value
        reserved_returns[['bookid', 'member_id', 'action_id', 'created_date']]. \
            to_sql("book_transaction_logs", connection, if_exists='append', index=False)

    def clear_db(self):
        statement = SQLStatements()
        statement.execute("DELETE FROM book_loans;")
        statement.execute("DELETE FROM book_reservations;")
        statement.execute("DELETE FROM book_transaction_logs;")
        statement.execute("DELETE FROM books;")

    def initialize_db(self):
        self.clear_db()
        self.load_books()
        self.load_loan_reservation_history()


class SQLStatements:
    """
    Module to handle logic for building & executing SQL statement
    Attribute(s)
    ------
        sqlScripts: dictionary - contains a sql scripts for all database tables

    Method(s)
    ---------
    build_query(collection, statement, **kwargs): Takes tablename, query template, and search parameters
    execute(statement): executes a given query

    """

    sqlScripts = {

        "books": {
            "fetch": "SELECT BookID, title, author, genre FROM books ;",
            "fetch_by_id": "SELECT BookID, title, author, genre FROM books where BookID={bookid};",
            "fetch_title": "SELECT BookID, title, author, genre FROM books where title LIKE '%{title}%';",
            "getGenreById": "",
            "is_valid": "SELECT BookID, title FROM books WHERE BookID = (SELECT bookid FROM book_reservations "
                           "WHERE bookid={bookid}) ",
            "is_available": "SELECT BookID, title from available_books where BookID = {bookid}",
            "is_loaned": "SELECT BookID, title from loaned_books where BookID = {bookid}",
            "is_reserved": "",
            "get_similar_books": "SELECT BookID, title from available_books WHERE title LIKE "
                                 "(SELECT title from books WHERE BookID = {bookid}) and BookID <> {bookid}",
            "logscript": "INSERT INTO book_transaction_logs(bookid, member_id, action_id, created_date) "
                                 "VALUES ({book_id},{member_id},{action_id},'{created_date}')",
        },
        "book_loans": {
            "fetch_book_history": "Fetch history by book_id;",
            "fetch_book_by_bookid": f"SELECT * FROM book_loans as a INNER JOIN books as b "
                                    "ON a.bookid = b.BookID where a.bookid={bookid} and status_id={status_id}",
            "check_out": "INSERT INTO book_loans(bookid,member_id,checkout_date,created_date,status_id) VALUES "
                         "({bookid},{member_id},'{checkout_date}','{created_date}',{status_id})",
            "return_book": "UPDATE book_loans SET return_date='{return_date}', modified_date='{modified_date}', "
                           "status_id = {status_id} WHERE bookid={bookid} and status_id=1",
            "fetch_loaned_books": "SELECT BookID, title from loaned_books",
            "fetch_available_books": "SELECT BookID, title from available_books",
            "fetch_loaned_book": "SELECT bookid, member_id book_loans WHERE bookid={bookid}"
        },
        "book_reservations": {
            "fetch_by_book_id": "",
            "fetch_wait_list": "SELECT id FROM book_reservations WHERE book_id = {book_id} and member_id = {member_id}",
            "add_to_wait_list": "INSERT INTO book_reservations VALUES ({book_id},{member_id},{created_date})",
            "remove_from_wait_list": "DELETE FROM book_reservations where id={id}",
            "is_reserved": "SELECT BookID, title FROM books WHERE BookID = (SELECT bookid FROM book_reservations "
                           "WHERE bookid={bookid}) ",
            "get_waitlist": "SELECT  title, COUNT(b.BookID) as reserved FROM books as b INNER JOIN book_reservations "
                            "as bs on b.BookID= bs.bookid GROUP BY b.title",
        },
        "book_transaction_logs": {
            "top_searched_titles": "SELECT title,genre, author, COUNT(*) as 'counts' FROM books a "
                                   "INNER JOIN book_transaction_logs b ON a.BookID=b.bookid WHERE action_id in (0, 2) "
                                   "GROUP BY title "
                                   "ORDER BY COUNT(*) DESC",
            "top_search_authors": "SELECT author, COUNT(*) as 'counts' FROM books a INNER JOIN book_transaction_logs b "
                                  "ON a.BookID=b.bookid WHERE action_id in (0, 2) "
                                  "GROUP BY author "
                                  "ORDER BY COUNT(*) DESC",
            "top_search_genre": "SELECT genre, COUNT(*) as 'counts' FROM books a INNER JOIN book_transaction_logs b "
                                "ON a.BookID=b.bookid WHERE action_id in (0, 2) "
                                "GROUP BY genre "
                                "ORDER BY COUNT(*) DESC",
        }
    }

    def build_query(self, collection, statement, **kwargs):
        """

        :param collection:
        :param statement:
        :param kwargs:
        :return:
        """
        try:
            statements = self.sqlScripts.get(collection)
            query = statements[statement]
            if len(kwargs) > 0:
                query_string = query.format(**kwargs)
            else:
                query_string = query

            return query_string
        # except KeyError:
        #     print(f"{collection}.{statement} issues")
        except TypeError:
            print(f"{collection}.{statement} statement could not be found.")

    def execute(self, statement):
        flag = True
        try:
            db = Database()
            sqlite_connection = sqlite3.connect(db.get_db())
            cursor = sqlite_connection.cursor()
            result = cursor.execute(statement)
            sqlite_connection.commit()
        except sqlite3.Error as error:
            flag = False
            result = "DB error: " + str(error)
        finally:
            sqlite_connection.close()

        return flag, result


class Status(Enum):
    """
    Constants to represent reference values from the Status Table
    """
    AVAILABLE = 0
    LOANED = 1
    RESERVED = 2


class LogAction(Enum):
    """
        Constants to represent reference values from the Log Actions Table
    """
    BOOK_CHECKOUT = 0
    BOOK_RETURNED = 1
    BOOK_RESERVED = 2
    BOOK_RESERVATION_CANCELLED = 3


class Logger:
    """
    A class to abstract logging library app activities
    """

    @staticmethod
    def log(bookid, member_id, action_id, created_date):
        """
        Log an activity in book_logs_transaction table
        :param book_id: Book
        :param member_id: Member
        :param action_id: Type of activity (checkout, reservation, return)
        :param created_date: Date activity happened
        :return: Tuple (flag:boolean, result: dataframe)
        """
        statement = SQLStatements()
        query = "INSERT INTO book_transaction_logs(bookid, member_id, action_id, created_date) VALUES " \
                "({},{},{},'{}')".format(bookid, member_id, action_id, created_date)
        flag, log_record = statement.execute(query)
        return flag, log_record

####### BEGINNING OF MISCELLENOUS HELPER FUNTIONS ########

def random_date_generator(start_date, range_in_days):
    """

    :param start_date:
    :param range_in_days:
    :return:
    """
    # reference - https://stackoverflow.com/questions/41006182/generate-random-dates-within-a-range-in-numpy
    days_to_add = np.arange(0, range_in_days)
    random_date = np.datetime64(start_date) + np.random.choice(days_to_add)
    return random_date


def write_to_file():

    data = ['datafiles/books.csv', 'datafiles/bestsellers with categories.csv']
    df = pd.read_csv(data[1])
    books = df[['BookID', 'Name', 'Author', 'Price', 'Genre']]
    purchase_date = []

    for i in range(550):
        purchase_date.append(str(random_date_generator('2020-01-01', 60)))

    books['purchase_date'] = purchase_date
    loan_reservation_data = generate_loan_reservations(200)
    books.to_csv("datafiles/Book_Info.txt", sep='|', index=False, mode='w')
    loan_reservation_data.to_csv("datafiles/Loan_Reservation_History.txt", sep='|', index=False, mode='w')


def generate_loan_reservations(size, start=1000, end=1200):
    """

    :param size:
    :param start:
    :param end:
    :return:
    """
    # Initialize Loan_Reservation attributes
    # book_id = np.random.randint(start, end, size)
    book_id = np.arange(start, end)
    reservation_date = []
    checkout_date = []
    return_date = []
    member_id = np.random.randint(1000, 9999, size)

    # Load with reservations record -> no checkout -> no return - 20% of records
    for i in range(int(0.20*size)):
        reservation_date.append(str(random_date_generator('2020-04-04', 60)))
        checkout_date.append("--")
        return_date.append("--")

    # Load with reservations record -> with checkout -> with no return - 25% of records
    for i in range(int(0.25 * size)):
        reservation_date.append(str(random_date_generator('2020-03-01', 30)))
        checkout_date.append(str(random_date_generator('2020-04-01', 30)))
        return_date.append("--")

    # Load with no reservations record -> with checkout -> with no return - 25% of records
    for i in range(int(0.25 * size)):
        reservation_date.append("--")
        checkout_date.append(str(random_date_generator('2020-04-01', 60)))
        return_date.append("--")

    # Load with no reservations record -> with checkout -> no return - 25% of records
    for i in range(int(0.25 * size)):
        reservation_date.append("--")
        checkout_date.append(str(random_date_generator('2020-04-01', 30)))
        return_date.append(str(random_date_generator('2020-05-01', 60)))

    # Load with reservations record -> with checkout -> with return - 5% of records
    for i in range(int(0.05 * size)):
        reservation_date.append(str(random_date_generator('2020-04-01', 30)))
        checkout_date.append(str(random_date_generator('2020-05-01', 30)))
        return_date.append(str(random_date_generator('2020-06-01', 60)))

    categories_dict = {
        'bookid': book_id,
        'reservation_date': reservation_date,
        'checkout_date': checkout_date,
        'return_date': return_date,
        'member_id': member_id
        }
    df = pd.DataFrame(categories_dict)
    return df


def insertBLOB(bookid, photo):
    try:
        sqliteConnection = Database().get_connection()
        # sqliteConnection = sqlite3.connect('imagedb.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        sqlite_insert_blob_query = """ INSERT INTO book_images(id, photo) VALUES (?, ?)"""

        img = mpimg.imread(photo)
        bkPhoto = pickle.dumps(img)  # packing imagedata

        # Convert data into tuple format
        data_tuple = (bookid, bkPhoto)

        cursor.execute(sqlite_insert_blob_query, data_tuple)
        sqliteConnection.commit()
        print("Image and file inserted successfully as a BLOB into a table")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("the sqlite connection is closed")


def readBlobData(id):
    fig = plt.figure(figsize=(4,6))
    try:
        sqliteConnection = Database().get_connection()
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        sql_fetch_blob_query = """SELECT * from book_images where id = ?"""
        cursor.execute(sql_fetch_blob_query, (id,))
        record = cursor.fetchall()
        for row in record:
            # print("Id = ", row[0], "Name = ", row[1])
            # name = row[1]
            photo = pickle.loads(row[1])  # unpacking photo to array
            imgplot = plt.imshow(photo)
        cursor.close()
        plt.axis('off')
        plt.show()
    except sqlite3.Error as error:
        print("Failed to read blob data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("sqlite connection is closed")
    return fig

def get_image_path(file):
    return os.path.join(img_dir, f"bk{file}.jpeg")

def insert_images():
    bookid = 1000
    for i in range(11):
        insertBLOB(bookid, get_image_path(i))
        bookid = bookid + 1


####### END OF MISCELLENOUS HELPER FUNTIONS ########
############ TEST METHODS #################
def test_sqlstatment():

    # Testing SQLStatement Class parsing implementation
    statement = SQLStatements()
    # query = statement.fetch_records("authors", "getAuthorById", id=1)
    query = statement.build_query("books", "fetch")

    # Testing Database class implementation
    db = Database()
    flag, result = db.run_sql_statement(query)
    if flag:
        print(result)
    else:
        print("error: ", result)


def test_db_loading():
    db = Database()
    db.load_books()


def test_loan_history_load():
    db = Database()
    db.load_loan_reservation_history()

##### END OF TEST METHODS ############




if __name__ == '__main__':
    db = Database()
    # write_to_file()
    # db.initialize_db()
    # Insert blob
    # insert_images()
    # readBlobData(1002)
    # # db.clear_db()
    # generate_loan_reservations(200)
    # test_sqlstatment()
    # test_db_loading()
    # test_loan_history_load()
    # main()







