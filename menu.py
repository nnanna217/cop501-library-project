############################
# COP 501 Coursework
# Author - F218341
############################
import re
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import Label as lb
import matplotlib.pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tempfile
from graphviz import Source
import numpy as np
import database as db
import bookCheckout as ck
import bookSearch as bs
import bookSelect as bks
import bookReturn as br
import textwrap
import smtplib as s
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart as mPAth


class workspace:
    def __init__(self, UI):
        self.__ResultTableAll = UI

    def clearResult(self):
        self._UIResult.delete("1.0",END)



#######################GUI CLASS#######################################################

class MainGUI:

    def __init__(self, window):
        self.checkout_books = []
        self.__mainWin = window
        self.__mainWin.title("Library Application")
        self.__mainWin.geometry('1680x1020')
        self.__CreateMenubar()
        self.__CreateBookResultPlace()
        # self.__bookDisplayPanel()

    def getWorkspaceUI(self):
        return self.__ResultLoanTable, self.__ResultBooksTable, self.__wrapper1, self.__wrapper2


    def __CreateMenubar(self):
        menubar = Menu(self.__mainWin)
        filemenu = Menu(menubar, tearoff=1)
        filemenu.add_command(label="Initialise DB", command=lambda: db.Database().initialize_db())
        filemenu.add_command(label="Clear Database", command=lambda: db.Database().clear_db())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.__mainWin.destroy)
        menubar.add_cascade(label="File", menu=filemenu)  #

        DBmenu = Menu(menubar, tearoff=1)
        DBmenu.add_command(label="View DBStructure", command=lambda: showDataModel(self.__mainWin))
        menubar.add_cascade(label="Database", menu=DBmenu)  #

        self.__mainWin.config(menu=menubar)


    def __CreateBookResultPlace(self):
        """
        Create container for the tab frame components
        :return: None
        """
        member_id = StringVar()
        email = StringVar()
        ############ Tabs and frames #################
        tabControl = Notebook(self.__mainWin)
        tabControl.grid(column=0, row=0, rowspan=10)
        searchtab = Frame(tabControl)
        checkouttab = Frame(tabControl)
        returntab = Frame(tabControl)
        purchasetab = Frame(tabControl)
        tabControl.add(searchtab, text='All Books')
        tabControl.add(checkouttab, text='Loan/Checkout Books')
        tabControl.add(returntab, text='Return books')
        tabControl.add(purchasetab, text='Purchase books')

        # Frame components
        self.searchFrame = Frame(searchtab)
        self.searchFrame.grid(column=0, row=0, rowspan=10)
        self.checkoutFrame = Frame(checkouttab)
        self.checkoutFrame.grid(column=0, row=0, rowspan=10)
        self.returnFrame = Frame(returntab)
        self.returnFrame.grid(column=0, row=0, rowspan=10)
        self.purchaseFrame = Frame(purchasetab)
        self.purchaseFrame.grid(column=0, row=0, rowspan=10)

        # Frame components
        self.__SearchBookFrame(self.searchFrame)
        self.__LoanBookFrame(self.checkoutFrame)
        self.__ReturnBookFrame(self.returnFrame)
        self.__PurchaseBookFrame(self.purchaseFrame)

        separator = Separator(self.checkoutFrame, orient='horizontal')
        separator.pack(fill='x', pady=10)

        # Add Notification message label for notifications
        self.__message_label = lb(self.checkoutFrame, text="", background="#E4E5E8")
        self.__message_label.pack(pady=10)

        # Add Multiple book Checkout component
        self.__ResultCheckoutTable = Treeview(self.checkoutFrame, columns=(1, 2), show="headings", height="5")
        self.__checkoutFields(self.checkoutFrame, member_id, email)

        # Add Return book placeholder table
        self.__ResultReturnTable = Treeview(self.returnFrame, columns=(1, 2, 3, 4), show="headings", height="5")
        self.__return_message_label = lb(self.returnFrame, text="", background="#E4E5E8")
        self.__return_message_label.pack(pady=10)

    def __SearchBookFrame(self, frame):
        """
        Tab frame for book search
        :param frame:
        :return:
        """
        wrapper1 = LabelFrame(frame, text="Find a book", labelanchor='w', relief=RIDGE)
        wrapper2 = LabelFrame(frame, text="Book List")
        wrapper1.pack(expand="no", padx=20, pady=15)
        wrapper2.pack(fill="both", expand="yes", padx=20, pady=5)

        # Search Area
        q = StringVar()
        button = Button(wrapper1, text="Reset", command=lambda: self.reset_books())
        button.pack(side=RIGHT, padx=10, )
        button2 = Button(wrapper1, text="Search", command=lambda: self.search_book_by_title(q))
        button2.pack(side=RIGHT, padx=10)
        entry = Entry(wrapper1, width=64, textvariable=q)
        entry.pack(side=RIGHT, padx=6)
        label = lb(wrapper1, text="Search")
        label.pack(side=RIGHT, padx=10)

        # Table Area
        flag, result = bs.Book.get_all()
        self.__ResultBooksTable = Treeview(wrapper2, columns=(1, 2, 3, 4), show="headings", height="20")
        self.__ResultBooksTable.pack(side=LEFT)
        self.__bookCountLabel = lb(wrapper2, text=f"{len(result)} records found")
        self.__bookCountLabel.pack(side=TOP, before=self.__ResultBooksTable)

        self.__ResultBooksTable.heading(1, text="Book ID")
        self.__ResultBooksTable.heading(2, text="Title")
        self.__ResultBooksTable.heading(3, text="Author")
        self.__ResultBooksTable.heading(4, text="Genre")
        self.__ResultBooksTable.column(1, minwidth=0, width=75)
        self.__ResultBooksTable.column(2, minwidth=0, width=450, stretch=YES)
        self.__ResultBooksTable.column(3, minwidth=0, width=250)
        self.__ResultBooksTable.column(4, minwidth=0, width=175)
        # Add Vertival scroll bar
        self.__add_verticalscrollar(wrapper2, self.__ResultBooksTable)
        self.__ResultBooksTable.bind("<ButtonRelease-1>", self.__displaybookImageEvent, add="+")

        # Add some table style
        MainGUI.add_table_style(self.__ResultBooksTable)

        # Fetch Data from DB and populate in frame
        if flag:
            self.__update_book_view(self.__ResultBooksTable,dataframe=result)

    def __displaybookImageEvent(self, event):
        row = self.__ResultBooksTable.identify_row(event.y)
        item = self.__ResultBooksTable.item(self.__ResultBooksTable.focus())
        self.__bookDisplayPanel()

    def __LoanBookFrame(self, frame):
        """
        Tab frame for loans & checkout
        :param frame:
        :return:
        """
        self.__wrapper1 = LabelFrame(frame, text="Checkout Book")
        self.__wrapper2 = LabelFrame(frame, text="List of available books")
        self.__wrapper1.pack(fill="both", expand="yes", padx=20, pady=15)
        self.__wrapper2.pack(fill="both", expand="yes", padx=20, pady=5)

        # Checkout Search Area
        book_id = StringVar()
        label = Label(self.__wrapper1, text="BookID")
        label.pack(side=LEFT, padx=5)
        entry1 = Entry(self.__wrapper1, textvariable=book_id)
        entry1.pack(side=LEFT, padx=5)
        button = Button(self.__wrapper1, text="Reset", command=lambda: self.reset_checkout_table())
        button.pack(side=LEFT, padx=5, )
        button2 = Button(self.__wrapper1, text="Search", command=lambda: self.fetch_for_checkout(book_id))
        button2.pack(side=LEFT, padx=5)
        flag, result = bs.Book.get_available_books()
        # flag, result = bs.Book.get_loaned_books()

        # Table Area
        self.__ResultLoanTable = Treeview(self.__wrapper2, columns=(1, 2, 3), show="headings", height="10")
        self.__ResultLoanTable.pack(side=LEFT)
        self.__loanCountlabel = lb(self.__wrapper2, text=f"{len(result)} records found")
        self.__loanCountlabel.pack(side=TOP, before=self.__ResultLoanTable)
        self.__ResultLoanTable.heading(1, text="Book ID")
        self.__ResultLoanTable.heading(2, text="Title")
        self.__ResultLoanTable.heading(3, text="Author")
        self.__ResultLoanTable.column(1, minwidth=0, width=75)
        self.__ResultLoanTable.column(2, minwidth=0, width=400, stretch=YES)
        self.__ResultLoanTable.column(3, minwidth=0, width=250)
        self.__add_verticalscrollar(self.__wrapper2, self.__ResultLoanTable)

        # Add some table style
        MainGUI.add_table_style(self.__ResultLoanTable)
        if flag:
            self.__update_book_view(self.__ResultLoanTable, dataframe=result)
            self.__loanCountlabel.config(text=f"{len(result)} records found")

        self.__ResultLoanTable.bind("<Double-1>", self.__add_to_checkout, add="+")


    def __ReturnBookFrame(self, frame):
        """
        Tab frame for returning a book
        :param frame:
        :return:
        """
        self.__wrapper1 = LabelFrame(frame, text="Return Book")
        self.__wrapper2 = LabelFrame(frame, text="List of available books")
        self.__wrapper1.pack(fill="both", expand="yes", padx=20, pady=15)
        self.__wrapper2.pack(fill="both", expand="yes", padx=20, pady=5)

        # Checkout Search Area
        book_id = StringVar()
        label = Label(self.__wrapper1, text="BookID")
        label.pack(side=LEFT, padx=5)
        entry1 = Entry(self.__wrapper1, textvariable=book_id)
        entry1.pack(side=LEFT, padx=5)
        button = Button(self.__wrapper1, text="Reset", command=lambda: donothing())
        button.pack(side=LEFT, padx=5, )
        button2 = Button(self.__wrapper1, text="Submit",
                         command=lambda: self.__show_returned_book(self.__add_return_book_table(), book_id))
        button2.pack(side=LEFT, padx=5)

    def __PurchaseBookFrame(self, frame):
        """
        Tab frame for purchasing a book
        :param frame:
        :return:
        """
        wrapper1 = LabelFrame(frame, text="Purchase", labelanchor='w', relief=RIDGE)
        wrapper2 = LabelFrame(frame, text="Top book recommendations for purchase")
        wrapper1.pack(expand="no", padx=20, pady=15)
        wrapper2.pack(fill="both", expand="yes", padx=20, pady=5)

        # Search Area
        q = StringVar()
        button2 = Button(wrapper1, text="Recommend for purchase")
        button2.pack(side=RIGHT, padx=10)
        entry = Entry(wrapper1, textvariable=q)
        entry.pack(side=RIGHT, padx=6)
        label = lb(wrapper1, text="Search")
        label.pack(side=RIGHT, padx=10)

        # Table Area
        # flag, result = bs.Book.get_all()
        flag, result = bks.top_searched_titles()
        self.__ResultPurchaseTable = Treeview(wrapper2, columns=(1, 2, 3, 4), show="headings", height="10")
        self.__ResultPurchaseTable.pack(side=LEFT)

        self.__ResultPurchaseTable.heading(1, text="Title")
        self.__ResultPurchaseTable.heading(2, text="Genre")
        self.__ResultPurchaseTable.heading(3, text="Author")
        self.__ResultPurchaseTable.heading(4, text="Counts")
        self.__ResultPurchaseTable.column(1, minwidth=0, width=500)
        self.__ResultPurchaseTable.column(2, minwidth=0, width=200, )
        self.__ResultPurchaseTable.column(3, minwidth=0, width=200, )
        self.__ResultPurchaseTable.column(4, minwidth=0, width=50, )
        # Add Vertival scroll bar
        self.__add_verticalscrollar(wrapper2, self.__ResultPurchaseTable)

        # Add some table style
        MainGUI.add_table_style(self.__ResultPurchaseTable)

        # Fetch Data from DB and populate in frame
        if flag:
            self.__update_book_view(self.__ResultPurchaseTable, dataframe=result)

        separator = Separator(frame, orient='horizontal')
        separator.pack(fill='x', pady=10)
        button = Button(wrapper1, text="x", command=self.__plotDiagram(frame, 10))
        button.pack(padx=10)

    def __plotDiagram(self, frame, size):
        """
        Plots charts to enable librarian recommend for purchase
        :param frame:
        :param size:
        :return:
        """
        # Plot Pie chat and load in canvas
        canvas2 = FigureCanvasTkAgg(bks.plot_top_genre(), master=frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side=LEFT)
        # Plot Bar chart and load in canvas
        canvas = FigureCanvasTkAgg(bks.plot_top_authors(10), master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=LEFT)

        # plt.show()

    def __plot_cover_image(self, frame):
        image_id = np.random.randint(1000, 1010)
        canvas = FigureCanvasTkAgg(db.readBlobData(image_id), master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=LEFT)

    @staticmethod
    def add_table_style(table):
        """
        Designs stripped table rows
        :param table: Treeview to be styles
        :return: None
        """
        style = Style()
        style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
        style.map('Treeview', background=[('selected', '#4db8ff')])
        table.tag_configure('oddrow', background="white")
        table.tag_configure('evenrow', background="#ccebff")

    def __update_book_view(self, table, dataframe=None, array=None):
        """
        Updates the Treeview elements and populates table dynamically
        :param table:
        :param dataframe: iteratable records
        :param array:iteratable records
        :return: None
        """
        books = []
        if dataframe is not None:
            # Shorten values not to exceed 75 characters
            for row in dataframe.values.tolist():
                book = []
                for val in row:
                    book.append(textwrap.shorten(str(val), 75))
                books.append(book)
            # Load data in table

        if array is not None:
            books = array

        count = 0
        for rows in books:
            if count % 2:
                table.insert('', 'end', values=rows, tags='evenrow')
            else:
                table.insert('', 'end', values=rows, tags='oddrow')
            count += 1

    def __add_checkout_view(self):
        """
        Method to trigger multicheck view to display
        :return: Treeview
        """
        self.__ResultCheckoutTable.pack(side=BOTTOM)
        self.__ResultCheckoutTable.heading(1, text="Book ID")
        self.__ResultCheckoutTable.heading(2, text="Title")
        self.__ResultCheckoutTable.column(1, minwidth=0, width=100)
        self.__ResultCheckoutTable.column(2, minwidth=0, width=500, stretch=YES)
        # self.__add_verticalscrollar(self.frame2, self.__ResultCheckoutTable)
        MainGUI.add_table_style(self.__ResultCheckoutTable)
        return self.__ResultCheckoutTable

    def __checkoutFields(self, frame, member_id, email):
        """
        Event handler for book checkout
        :param frame:
        :param member_id:
        :param email:
        :return: None
        """
        lf = LabelFrame(frame, text="Checkout Details", labelanchor='w', relief=RIDGE)
        lf.pack(fill="both", expand="no", padx=20, pady=15)
        label2 = Label(lf, text="MemberID")
        label2.pack(side=LEFT, padx=10)
        entry2 = Entry(lf, textvariable=member_id)
        entry2.pack(side=LEFT, padx=10)
        label3 = Label(lf, text="Email")
        label3.pack(side=LEFT, padx=5)
        entry3 = Entry(lf, textvariable=email)
        entry3.pack(side=LEFT, padx=10)
        button = Button(lf, text="Checkout",
                        command=lambda: self.__checkout_book(member_id, self.checkout_books, email))
        button.pack(padx=10)

    def __add_to_checkout(self, event):
        """
        Adds selected book to a list of books to be checked out. Allows for multibook checkout
        :param event: callback event
        :return:
        """
        row = self.__ResultLoanTable.identify_row(event.y)
        item = self.__ResultLoanTable.item(self.__ResultLoanTable.focus())
        self.checkout_books.append(item['values'])
        self.__ResultCheckoutTable.delete(*self.__ResultCheckoutTable.get_children())
        self.__update_book_view(self.__add_checkout_view(), array=self.checkout_books)
        print(self.checkout_books)

    def fetch_for_checkout(self, book_var):
        """
        Fetch books to be checked out
        :param book_var: bookid value
        :return:
        """
        self.__ResultLoanTable.delete(*self.__ResultLoanTable.get_children())
        valid, message = is_valid_number(book_var.get())
        if not valid:
            messagebox.showinfo("Invalid BookID", message)
        else:
            flag, message, result = ck.verify_checkout(book_var.get())
            if flag and len(result) > 0:
                self.__message_label.config(fg="#fc9803")
                self.__message_label.config(text=f"{message}")
                self.__update_book_view(self.__ResultLoanTable, dataframe=result)
                self.__loanCountlabel.config(text=f"{len(result)} records found")
            elif flag and len(result) <= 0:
                self.__message_label.config(fg="red")
                self.__message_label.config(text=f"{message}")
            else:
                self.__message_label.config(text=f"{message}")
                # self.__message_label.pack_forget()

    def __bookDisplayPanel(self):
        """

        :return:
        """
        bookid = StringVar()
        self.__bookdisplaywrapper = LabelFrame(self.__mainWin, text="Book display", relief=RIDGE)
        self.__bookdisplaywrapper.grid(row=0, column=12, padx=20, pady=15, sticky="w")
        self.__bookdisplaylabel = lb(self.__bookdisplaywrapper,image=self.__plot_cover_image(self.__bookdisplaywrapper))
        self.__bookdisplaylabel.pack(side=LEFT, padx=20, pady=15)

    def __add_verticalscrollar(self, wrapper, treeview):
        yscrollbar = Scrollbar(wrapper, orient="vertical", command=treeview.yview)
        yscrollbar.pack(side=RIGHT, fill="y")
        treeview.configure(yscrollcommand=yscrollbar.set)

    def search_book_by_title(self, title_var):
        """
        Return a list of books when given a book name
        :param title_var: StringVar
        :return: None
        """
        if title_var.get() == "":
            validate_search_field()
        else:
            self.__ResultBooksTable.delete(*self.__ResultBooksTable.get_children())
            flag, result = bs.Book.get_by_title(title_var.get())
            if flag:
                self.__update_book_view(self.__ResultBooksTable, dataframe=result)
                self.__bookCountLabel.configure(text=f"{len(result)} records found")

    def reset_books(self):
        """
        Resets the Search table review to it's original state
        :return: None
        """
        self.__ResultBooksTable.delete(*self.__ResultBooksTable.get_children())
        flag, result = bs.Book.get_all()
        if flag:
            self.__update_book_view(self.__ResultBooksTable, dataframe=result)
            self.__bookCountLabel.configure(text=f"{len(result)} records found")

    def reset_checkout_table(self):
        """
        Resets the list of availbale books for loan in the CheckoutFrame to it's original state
        :return: Nonee
        """
        flag, result = bs.Book.get_available_books()
        self.__ResultLoanTable.delete(*self.__ResultLoanTable.get_children())
        self.__message_label.config(text=f"")
        self.__update_book_view(self.__ResultLoanTable, dataframe=result)
        self.__loanCountlabel.config(text=f"{len(result)} records found")

    def __checkout_book(self, member_id, checkout_books, email):
        """

        :param member_id:
        :param checkout_books:
        :param email:
        :return:
        """

        valid_number, message = is_valid_number(member_id.get())
        valid_email, message2 = is_valid_email(email.get())
        if not valid_number:
            validate_search_field(message)
        elif not valid_email:
            validate_search_field(message2)
        elif len(self.checkout_books) <= 0:
            validate_search_field("Please first select a book you would like to checkout. ")
        else:
            for book in checkout_books:
                ck.checkout(member_id=member_id.get(), bookid=book[0])
            self.__ResultCheckoutTable.delete(*self.__ResultCheckoutTable.get_children())
            success_dialog("Book has been checked out Successfully")
            # Send reciept as email
            self.__send_reciept(member_id=member_id.get(), email=email.get(), checkout_books=checkout_books)

    def __send_reciept(self, member_id, email, checkout_books):
        """
        Sends a receipt to the borrows as an email
        :param member_id: String
        :param email: String
        :param checkout_books: List
        :return: Boolean
        """
        assert isinstance(checkout_books, list)
        emails = [email]
        message_body = f"<h1> Receipt </h1> <br>" \
                       f"<h3>Thank you <b>{member_id}</b> for using the Library application. " \
                       f"Here is a list of books borrowed</h3> <br>"
        signed_out_books = array2htmltable(checkout_books)
        receipt = message_body + signed_out_books
        send_email(to_emails=emails, html=receipt)
        return True

    def __add_return_book_table(self):
        self.__ResultReturnTable.pack()
        self.__ResultReturnTable.heading(1, text="Book ID")
        self.__ResultReturnTable.heading(2, text="Title")
        self.__ResultReturnTable.heading(3, text="Member")
        self.__ResultReturnTable.heading(4, text="Checkout Date")
        self.__ResultReturnTable.column(1, minwidth=0, width=100)
        self.__ResultReturnTable.column(2, minwidth=0, width=500, stretch=YES)
        self.__ResultReturnTable.column(3, minwidth=0, width=100)
        self.__ResultReturnTable.column(4, minwidth=0, width=200)
        MainGUI.add_table_style(self.__ResultReturnTable)
        return self.__ResultReturnTable

    def __show_returned_book(self, event, bookid):

        valid_number, message = is_valid_number(bookid.get())
        if not valid_number:
            validate_search_field(message)
            self.__ResultReturnTable.pack_forget()
            return
        self.__ResultReturnTable.delete(*self.__ResultReturnTable.get_children())
        flag, message, result = br.return_book(bookid=bookid.get())
        if flag == "booked":
            # show error dialog
            self.__return_message_label.configure(text=message, foreground="red")
            # messagebox.showinfo("Error", message)
        else:
            self.__update_book_view(self.__add_return_book_table(), dataframe=result)
            self.__return_message_label.configure(text=message, foreground="green")
            print(flag, message)



def donothing():
    print("Do nothing")
    messagebox.showinfo("Under Construction " \
                        , """ this function has not been implemented yet""")


def success_dialog(message):
    print("Success")
    messagebox.showinfo("Success ", message)


def validate_search_field(message):
    messagebox.showinfo("Invalid input", message)


def send_email(text="Python Email Tutorial", subject="Library Checkout Receipt",
               from_email="Librarian <neze.privatedev@gmail.com>",to_emails=None, html=None):
    """
    Sends an email to a list of receipents
    :param text: body of email (text based email)
    :param subject: email subject
    :param from_email: sender email
    :param to_emails: (list) receipent email
    :param html: html text bosy
    :return: None
    """

    username = "neze.privatedev@gmail.com"
    password = "rnwzxqjsgmrrwqwe"
    smptp_host = "smtp.gmail.com"
    smtp_port = 587
    assert isinstance(to_emails, list)

    msg = mPAth("alternative")
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)
    msg["Subject"] = subject

    txt_path = MIMEText(text, "plain")
    msg.attach(txt_path)
    if html != None:
    # html_text = "<h1> This is working</h1>"
        html_body=MIMEText(html, "html")
    msg.attach(html_body)
    msg_str = msg.as_string()
    # login to smptp server
    server = s.SMTP(smptp_host, smtp_port)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(from_email, to_emails, msg_str)
    server.quit()


def array2htmltable(data):
    # Beginning of Array to HTML Table from src [1]
    q = "<table>\n"
    for i in [(data[0:1], 'th'), (data[1:], 'td')]:
        q += "\n".join(
            [
                "<tr>%s</tr>" % str(_mm)
                for _mm in [
                    "".join(
                        [
                            "<%s>%s</%s>" % (i[1], str(_q), i[1])
                            for _q in _m
                        ]
                    ) for _m in i[0]
                ]
            ])+"\n"
    q += "</table>"
    return q
    # end of src [1]
    # src [1] - https://gist.github.com/aizquier/ef229826754626ffc4b8b6e49c599b68


def showDataModel(win):

    dot_code = """
    digraph "Library.db" {

        splines  = ortho;
        fontname = "Inconsolata";

        node [colorscheme = ylgnbu4];
        edge [colorscheme = dark28, dir = both];

        available_books       [shape = record, label = "{ available_books(view) |  BookID : integer\l  title : text\l }"];
        book_images           [shape = record, label = "{ book_images |  id : integer\l  photo : blob\l }"];
        book_loans            [shape = record, label = "{ book_loans |  bookid : integer\l  member_id : integer\l  checkout_date : varchar(12)\l  return_date : varchar(12)\l  created_date : varchar(12)\l  modified_date : varchar(12)\l  status_id : integer\l| id : integer\l }"];
        book_reservations     [shape = record, label = "{ book_reservations |  bookid : integer\l  member_id : integer\l| id : integer\l }"];
        book_transaction_logs [shape = record, label = "{ book_transaction_logs |  bookid : integer\l  member_id : integer\l  action_id : integer\l  created_date : date\l| id : integer\l }"];
        books                 [shape = record, label = "{ books |  title : text\l  author : text\l  purchase_price : integer\l  genre : text\l  purchase_date : text\l| BookID : integer\l }"];
        loaned_books          [shape = record, label = "{ loaned_books(view) |  BookID : integer\l  title : text\l }"];
        log_actions           [shape = record, label = "{ log_actions |  name : text\l| id : integer\l }"];
        status                [shape = record, label = "{ status |  name : text\l| id : integer\l }"];

        book_loans            -> books                 [color = "#595959", style = solid , arrowtail = crow    , arrowhead = none  , taillabel = "∞", label = "bookid:BookID", headlabel = "1"];
        book_loans            -> status                [color = "#595959", style = solid , arrowtail = crow    , arrowhead = none  , taillabel = "∞", label = "status_id:id", headlabel = "1"];
        book_reservations     -> books                 [color = "#595959", style = solid , arrowtail = crow    , arrowhead = none  , taillabel = "∞", label = "bookid:BookID", headlabel = "1"];
        book_transaction_logs -> books                 [color = "#595959", style = solid , arrowtail = crow    , arrowhead = none  , taillabel = "∞", label = "bookid:BookID", headlabel = "1"];
        book_transaction_logs -> log_actions           [color = "#595959", style = solid , arrowtail = crow    , arrowhead = none  , taillabel = "∞", label = "action_id:id", headlabel = "1"];

    }
    """

    top = Toplevel(win)
    top.geometry("1020x780")
    top.title("DB Schema")
    # Label(top, text="Hello World!", font=('Mistral 18 bold')).place(x=150, y=80)

    src = Source(source=dot_code, format='png')
    fd = tempfile.mktemp()
    src.render(fd, view=False)

    x = plt.imread(fd + ".png")
    x.shape
    fig = plt.figure()
    plt.imshow(x)
    plt.axis('off')
    # plt.show()

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas.draw()
    canvas.get_tk_widget().pack(side=LEFT)

    toolbar = NavigationToolbar2Tk(canvas, top)
    toolbar.update()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)


def is_valid_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    flag = False
    message = ""
    if re.search(regex, email):
        flag = True
        message = "Valid Email"
    else:
        message = "Invalid Email"
    return flag, message


def is_valid_number(number):
    regex = '^([0-9]{4})$'
    flag = False
    message = ""
    if re.search(regex, number):
        flag = True
        message = "Valid ID Number provided"
    else:
        message = "Invalid Number provided"
    return flag, message


###############################
####------MAIN----------#######
###############################


def main():
        global userWS, window
        window = Tk()
        mGUI=MainGUI(window)
        userWS=workspace(mGUI.getWorkspaceUI())
        window.mainloop()


if __name__ == '__main__':
    main()

