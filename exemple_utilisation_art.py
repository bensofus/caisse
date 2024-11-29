import sqlite3
from gestion_articles import (
    initialiser_articles,
    ajouter_article,
    rechercher_article,
    verifier_stock
)


def exemple_utilisation():
    conn = sqlite3.connect("appli.db")
    initialiser_articles(conn)

    ajouter_article(conn, "Carnet2", "Papeterie", "A5", "Pages lignées", 50, 5, "Fournisseur Y", "REF456", 10, 2, 3, 6)

    articles = rechercher_article(conn, "categorie", "Papeterie")
    for article in articles:
        print(article)

    alertes = verifier_stock(conn)
    print("Articles en stock critique :", alertes)

    conn.close()


if __name__ == "__main__":
    exemple_utilisation()
