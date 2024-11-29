import sqlite3
from gestion_caisse import (
    initialiser_vente,
    initialiser_detail_vente,
    creer_vente,
    modifier_etat_vente,
    rechercher_vente,
    rapport_journalier,
)


def test_gestion_caisse():
    conn = sqlite3.connect("appli.db")

    # Initialisation des tables
    initialiser_vente(conn)
    initialiser_detail_vente(conn)

    # Création d'une vente
    articles = [
        {"article_id": 1, "quantite": 2, "remise": 10},
        {"article_id": 2, "quantite": 1},
    ]
    doc_num = creer_vente(conn, 1, articles, "cash", client_id=1)  # 1 = facture
    assert doc_num is not None, "La création de la vente a échoué."

    # Recherche de la vente
    vente = rechercher_vente(conn, "doc_num", doc_num)
    assert len(vente) > 0, "La vente n'a pas été trouvée."

    # Modification de l'état
    vente_id = vente[0][0]  # ID de la vente
    modifier_etat_vente(conn, vente_id, 1)  # Passer à l'état validé
    vente_validée = rechercher_vente(conn, "id", vente_id)
    assert vente_validée[0][-1] == 1, "L'état de la vente n'a pas été modifié correctement."

    # Génération d'un rapport journalier
    rapport = rapport_journalier(conn, "2024-11-28")
    assert len(rapport) > 0, "Le rapport journalier est vide."

    print("Tous les tests ont réussi.")
    conn.close()


if __name__ == "__main__":
    test_gestion_caisse()
