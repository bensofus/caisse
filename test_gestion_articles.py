import sqlite3
from gestion_articles import (
    initialiser_articles,
    ajouter_article,
    modifier_article,
    supprimer_article,
    rechercher_article,
    verifier_stock
)


def test_gestion_articles():
    conn = sqlite3.connect("appli.db")
    initialiser_articles(conn)

    # Ajouter un article
    ajouter_article(conn, "Stylo", "Papeterie", "Stylo à bille", "Bleu, 0.5mm", 100, 10, "Fournisseur X", "REF123", 20, 1, 2, 5)
    assert len(rechercher_article(conn, "nom", "Stylo")) > 0

    # Modifier un article
    article = rechercher_article(conn, "nom", "Stylo")[0]
    modifier_article(conn, article[0], stock=5)
    assert rechercher_article(conn, "nom", "Stylo")[0][5] == 5

    # Vérification du stock critique
    alertes = verifier_stock(conn)
    assert len(alertes) > 0

    # Supprimer un article
    supprimer_article(conn, article[0])
    assert len(rechercher_article(conn, "nom", "Stylo")) == 0

    print("Tous les tests ont réussi.")
    conn.close()


if __name__ == "__main__":
    test_gestion_articles()
