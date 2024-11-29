import sqlite3
from gestion_caisse import (
    initialiser_vente,
    initialiser_detail_vente,
    creer_vente,
    modifier_etat_vente,
    rechercher_vente,
    rapport_journalier,
)


def exemple_utilisation():
    conn = sqlite3.connect("appli.db")

    # Initialisation des tables
    initialiser_vente(conn)
    initialiser_detail_vente(conn)

    # Ajouter une vente
    articles = [
        {"article_id": 1, "quantite": 2, "remise": 5},
        {"article_id": 3, "quantite": 1, "remise": 0},
    ]
    doc_num = creer_vente(conn, 1, articles, "carte", client_id=2)
    print(f"Vente créée avec le numéro : {doc_num}")

    # Recherche d'une vente
    vente = rechercher_vente(conn, "doc_num", doc_num)
    if vente:
        print("Vente trouvée :", vente)
    else:
        print("Aucune vente trouvée.")

    # Modifier l'état de la vente
    vente_id = vente[0][0]  # ID de la vente
    modifier_etat_vente(conn, vente_id, 2)  # Archiver la vente
    print(f"Vente {doc_num} passée à l'état 'Archivé'.")

    # Rapport journalier
    rapport = rapport_journalier(conn, "2024-11-28")
    print("Rapport journalier :", rapport)

    conn.close()


if __name__ == "__main__":
    exemple_utilisation()
