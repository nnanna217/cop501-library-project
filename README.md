
# COP 501 Coursework
# Author - F218341


## Database Structure

    - Schema Structure -
     View ERD via the GUI menu (in menu.py). Navigate to Database -> View DBStructure
        Tables - books, books_loans, book_reservation, book_transaction_logs, log_action, status, book_images
        Views - available_books, loaned_books


## database.py module

    - Initialization - Defined in initialize_db - Reads the Book_Info & Loan Reservation files and preloads the DB using
            data wrangling and loading 7 tables as described in the Schema section
    - Clearing Database - Defined in initialize_db (and GUI in the File -> Clear Database menu)
    - OOP Structure
        The module was built as a combination of different logical aspects as objects. It contains the following Classes
        - SQLStatement Class - Abstraction for building & executing query objects for inserting, retrieving & updating the database records.
                        SQL statements are stored in a dictionary & **kwargs are used to assign parameters dynamically
        - Database Class
        - Logger Class - Abstracts logging functionality
        - LogAction Class - Inherits the Enum Class to define reusable constants mirroring the log_action table.
        - Status - Inherits the Enum Class to define reusable constants mirroring the status table.

    This module also contains other helper functions for testing and data wrangling.

## menu.py module

    Build the GUI using a hybrid of OOP components and modular functions
    Watch this 7mins walkthrough of the Library application https://youtu.be/XrSVTUE-ghE

    - Extras
        - Checking out multi books at one go
            Steps to replicate
                - Navigate to the Loan/Checkout Tab
                - Doubleclick on a desired book (search by book id also narrows down search and notifies you if the
                book is unavailable)
                - Selected books appear below. You can select multiple books.
                - Enter member ID and email address.
                - Click checkout. (An email containing the list of books checked out will be sent to you)
        - Sending email receipt to the borrower - email contains a list of books borrowed
        - Regex validation of input strings (email checks, number checks)
        - Stripped color styling of the table records
        - Image display on single click event of Treeview.



## bookSelect.py module

    - Displayed the following
        - Top 10 most searched books (most booked or reserved)
        - A pie chart of Top Genres borrowed
        - A bar chart of Top authors borrowed.
    The visualizations were designed using meta-data from the book transaction logs.
    Due to time constraints, I could not add desired advanced recommendation.

## bookSearch.py module
    - N/A

## bookCheckout.py module
    - I was constrained by time to fully implement Reserve book. While notification for reservation was implemented
    Display book reservation  option was not implemented

## bookReturn.py module
    - N/A

