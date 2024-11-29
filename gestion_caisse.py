import sqlite3
from datetime import datetime


def initialiser_vente(conn):
    """
    Initialise la table DAT pour les entêtes des ventes.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DAT (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_type INTEGER NOT NULL, -- 1: Facture, 2: BL, 3: Devis
            doc_num TEXT UNIQUE NOT NULL,
            doc_date TEXT NOT NULL,
            doc_heure TEXT NOT NULL,
            client_id INTEGER DEFAULT NULL,
            mode_paiement TEXT NOT NULL, -- ex: cash, carte, cheque
            tot_htva REAL NOT NULL,
            tot_tva REAL NOT NULL,
            tot_ttc REAL NOT NULL,
            timbre_fiscal REAL NOT NULL,
            etat INTEGER DEFAULT 0, -- 0: Normal, 1: Validé, 2: Archivé, 9: Effacé
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)
    conn.commit()


def initialiser_detail_vente(conn):
    """
    Initialise la table DES pour les détails des ventes.
    """
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DES (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER NOT NULL,
            article_id INTEGER NOT NULL,
            quantite INTEGER NOT NULL,
            prix_unitaire_ht REAL NOT NULL,
            remise REAL DEFAULT 0,
            prix_total_ht REAL NOT NULL,
            prix_total_ttc REAL NOT NULL,
            FOREIGN KEY (doc_id) REFERENCES DAT(id),
            FOREIGN KEY (article_id) REFERENCES articles(id)
        )
    """)
    conn.commit()


def creer_vente(conn, doc_type, articles, mode_paiement, client_id=None):
    """
    Crée une nouvelle vente avec calculs automatiques et mise à jour des stocks.

    :param conn: Connexion à la base SQLite.
    :param doc_type: Type de document (1 = facture, 2 = BL, 3 = devis).
    :param articles: Liste de dictionnaires représentant les articles (article_id, quantite, remise).
    :param mode_paiement: Mode de paiement (ex. : cash, carte).
    :param client_id: Identifiant du client (facultatif).
    :return: Numéro de document généré.
    """
    cursor = conn.cursor()

    # Mapper le doc_type aux clés de séquences dans parametres
    key_mapping = {1: "sequence_facture", 2: "sequence_bl", 3: "sequence_devis"}
    key = key_mapping.get(doc_type, None)

    if not key:
        raise ValueError(f"Type de document inconnu : {doc_type}")

    # Récupérer la séquence actuelle
    cursor.execute("SELECT valeur FROM parametres WHERE cle = ?", (key,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"La clé '{key}' est introuvable dans la table parametres.")

    sequence = int(result[0])
    doc_num = f"{doc_type}-{sequence + 1}"

    # Mettre à jour la séquence
    cursor.execute("UPDATE parametres SET valeur = ? WHERE cle = ?", (sequence + 1, key))

    # Calcul des totaux
    tot_htva, tot_tva, tot_ttc = 0, 0, 0
    for article in articles:
        article_id = article["article_id"]
        quantite = article["quantite"]
        remise = article.get("remise", 0)

        # Récupérer les informations de l'article
        cursor.execute("SELECT prix_vente_ht, tva FROM articles WHERE id = ?", (article_id,))
        result = cursor.fetchone()
        if not result:
            raise ValueError(f"L'article ID {article_id} est introuvable.")

        prix_unitaire_ht, tva = result
        prix_total_ht = quantite * prix_unitaire_ht * (1 - remise / 100)
        prix_total_ttc = prix_total_ht * (1 + tva / 100)

        tot_htva += prix_total_ht
        tot_tva += prix_total_ht * tva / 100
        tot_ttc += prix_total_ttc

        # Mise à jour du stock
        cursor.execute("UPDATE articles SET stock = stock - ? WHERE id = ?", (quantite, article_id))

        # Ajouter dans DES (détails)
        cursor.execute("""
            INSERT INTO DES (doc_id, article_id, quantite, prix_unitaire_ht, remise, prix_total_ht, prix_total_ttc)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (None, article_id, quantite, prix_unitaire_ht, remise, prix_total_ht, prix_total_ttc))

    # Ajouter dans DAT (entête)
    cursor.execute("""
        INSERT INTO DAT (doc_type, doc_num, doc_date, doc_heure, client_id, mode_paiement, 
                         tot_htva, tot_tva, tot_ttc, timbre_fiscal, etat)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (doc_type, doc_num, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"),
          client_id, mode_paiement, tot_htva, tot_tva, tot_ttc, 1))  # Timbre fiscal = 1 dinar

    # Obtenir l'ID de la vente pour relier les détails
    vente_id = cursor.lastrowid

    # Mise à jour du doc_id dans DES
    cursor.execute("UPDATE DES SET doc_id = ? WHERE doc_id IS NULL", (vente_id,))

    conn.commit()

    return doc_num

def modifier_etat_vente(conn, doc_id, nouvel_etat):
    """
    Modifie l'état d'une vente.
    """
    cursor = conn.cursor()
    cursor.execute("UPDATE DAT SET etat = ? WHERE id = ?", (nouvel_etat, doc_id))
    conn.commit()


def rechercher_vente(conn, critere, valeur):
    """
    Recherche une vente selon un critère.
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM DAT WHERE {critere} = ? AND etat != 9", (valeur,))
    return cursor.fetchall()


def rapport_journalier(conn, date):
    """
    Génère un rapport des ventes pour une date donnée.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT doc_type, SUM(tot_ttc) AS total_ttc, SUM(tot_tva) AS total_tva, SUM(timbre_fiscal) AS total_timbre
        FROM DAT WHERE doc_date = ? AND etat IN (0, 1) GROUP BY doc_type
    """, (date,))
    return cursor.fetchall()

