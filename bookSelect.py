############################
# COP 501 Coursework
# Author - F218341
############################
"""
Module to handles book selection criterias to guide librarian which top books are searched.
It fetches records from the book_transaction_logs

Functions
---------
    top_searched_titles
    top_searched_authors
    top_searched_genre
    plot_top_genre
    plot_top_authors
    plot_as_subplot

"""
import database as db
import matplotlib.pyplot as plt
import numpy as np

def top_searched_titles():
    """
    Fetches top searched (loaned or reserved) books.
    :return: Tuple (type: boolean, dataframe)
    """
    query_string = db.SQLStatements().build_query('book_transaction_logs', 'top_searched_titles')
    flag, result = db.Database().run_sql_statement(sql_statement=query_string)
    return flag, result


def top_search_authors():
    """
    Fetches top search authors
    :return: Tuple (type: boolean, dataframe)
    """
    query_string = db.SQLStatements().build_query('book_transaction_logs', 'top_search_authors')
    flag, result = db.Database().run_sql_statement(sql_statement=query_string)
    return flag, result


def top_search_genre():
    """
    Fetches top searched genre
    :return: Tuple (type: boolean, dataframe)
    """
    query_string = db.SQLStatements().build_query('book_transaction_logs', 'top_search_genre')
    flag, result = db.Database().run_sql_statement(sql_statement=query_string)
    return flag, result


def plot_top_genre():
    """
    Plots to the top searched genre
    :return: Figure
    """
    flag, genre = top_search_genre()
    fig = plt.figure(figsize=[4.5, 4.8])
    plt.pie(genre.counts, labels=genre.genre, autopct='%1.2f%%')
    plt.tight_layout()
    # plt.show()
    return fig


def plot_top_authors(size):
    """

    :param size: (int) number of records you desire
    :return: Figure
    """
    flag, authors = top_search_authors()
    top_10_authors = authors.head(size)
    colors = plt.get_cmap('Blues')(np.linspace(0.7, 0.3, len(top_10_authors)))
    fig = plt.figure()
    plt.bar(top_10_authors.author, top_10_authors.counts, width=1, edgecolor="white", linewidth=0.7, color=colors)
    plt.title(f'Top {size} authors', color='red')
    plt.xticks(rotation=90)
    plt.tight_layout()
    # plt.show()
    return fig

def plot_as_subplot(size):
    """

    :param size: (int) number of records you desire
    :return: Figure
    """
    # Get data from transaction table
    flag, genre = top_search_genre()
    flag2, authors = top_search_authors()
    top_10_authors = authors.head(size)

    pie_colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(genre)))
    bar_colors = plt.get_cmap('Blues')(np.linspace(0.7, 0.3, len(top_10_authors)))
    # plot
    fig = plt.figure()
    plt.subplot(2, 1, 1)
    plt.pie(genre.counts, labels=genre.genre, autopct='%1.2f%%', explode=np.linspace(0,1,num=len(genre)), colors=pie_colors,
           wedgeprops={"linewidth": 1, "edgecolor": "white"})

    plt.subplot(2, 1, 2)
    plt.bar(top_10_authors.author, top_10_authors.counts, width=1, edgecolor="white", linewidth=0.7, color=bar_colors)
    plt.title(f'Top {size} authors', color='red')
    plt.xticks(rotation=90)
    plt.tight_layout()
    # plt.show()
    return fig


def main():
    """
    Test method
    :return: None
    """
    print("="*20)
    print(top_search_authors())
    print("=" * 20)
    print(top_searched_titles())
    print("=" * 20)
    assert isinstance(plot_top_genre(), plt.Figure)
    assert isinstance(plot_top_authors(10), plt.Figure)
    assert isinstance(plot_top_genre(), plt.Figure)
    assert isinstance(plot_as_subplot(10), plt.Figure)


if __name__ == '__main__':
    main()
