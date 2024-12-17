import sqlite3


def initialiser_articles(conn):
    """
    Initialise la table articles si elle n'existe pas.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                categorie TEXT DEFAULT NULL,
                sous_categorie TEXT DEFAULT NULL,
                description TEXT DEFAULT NULL,
                stock INTEGER DEFAULT 0,
                stock_minimum INTEGER DEFAULT 0,
                fournisseur TEXT DEFAULT NULL,
                ref_fournisseur TEXT DEFAULT NULL,
                tva REAL DEFAULT 0,
                prix_achat_ht REAL DEFAULT 0,
                prix_moyen_pondere REAL DEFAULT 0,
                marge_brute REAL DEFAULT 0,
                prix_vente_min REAL DEFAULT 0,
                prix_vente_ht REAL DEFAULT 0,
                prix_vente_ttc REAL DEFAULT 0
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'initialisation de la table articles : {e}")


def calculer_prix_vente_ttc(prix_vente_ht, tva):
    """
    Calcule le prix de vente TTC.
    """
    return round(prix_vente_ht * (1 + tva / 100), 3)


def calculer_marge_brute(prix_vente_ht, prix_achat_ht):
    """
    Calcule la marge brute.
    """
    if prix_achat_ht == 0:
        return 0.0
    return round(((prix_vente_ht - prix_achat_ht) / prix_achat_ht * 100), 3)


def ajouter_article(conn, nom, categorie=None, sous_categorie=None, description=None, stock=0,
                    stock_minimum=0, fournisseur=None, ref_fournisseur=None, tva=0, prix_achat_ht=0,
                    prix_vente_min=0, prix_vente_ht=0):
    """
    Ajoute un article avec les calculs automatisés pour les champs dérivés.
    """
    try:
        prix_achat_ht = round(prix_achat_ht, 3)
        prix_vente_ht = round(prix_vente_ht, 3)
        tva = round(tva, 3)
        prix_vente_ttc = calculer_prix_vente_ttc(prix_vente_ht, tva)
        marge_brute = calculer_marge_brute(prix_vente_ht, prix_achat_ht)
        prix_moyen_pondere = prix_achat_ht

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO articles (
                nom, categorie, sous_categorie, description, stock, stock_minimum, fournisseur, 
                ref_fournisseur, tva, prix_achat_ht, prix_moyen_pondere, marge_brute, 
                prix_vente_min, prix_vente_ht, prix_vente_ttc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nom, categorie, sous_categorie, description, stock, stock_minimum, fournisseur,
              ref_fournisseur, tva, prix_achat_ht, prix_moyen_pondere, marge_brute,
              round(prix_vente_min, 3), prix_vente_ht, prix_vente_ttc))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Erreur d'intégrité (nom déjà utilisé) : {e}")
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout de l'article : {e}")


def modifier_article(conn, id, **kwargs):
    """
    Modifie les champs d'un article et met à jour les calculs automatisés si nécessaire.
    """
    try:
        # Arrondir les valeurs monétaires si elles sont fournies
        if "prix_achat_ht" in kwargs and kwargs["prix_achat_ht"] is not None:
            kwargs["prix_achat_ht"] = round(kwargs["prix_achat_ht"], 3)
        if "prix_vente_ht" in kwargs and kwargs["prix_vente_ht"] is not None:
            kwargs["prix_vente_ht"] = round(kwargs["prix_vente_ht"], 3)
        if "tva" in kwargs and kwargs["tva"] is not None:
            kwargs["tva"] = round(kwargs["tva"], 3)

        fields = {
            "nom": kwargs.get("nom"),
            "categorie": kwargs.get("categorie"),
            "sous_categorie": kwargs.get("sous_categorie"),
            "description": kwargs.get("description"),
            "stock": kwargs.get("stock"),
            "stock_minimum": kwargs.get("stock_minimum"),
            "fournisseur": kwargs.get("fournisseur"),
            "ref_fournisseur": kwargs.get("ref_fournisseur"),
            "tva": kwargs.get("tva"),
            "prix_achat_ht": kwargs.get("prix_achat_ht"),
            "prix_vente_min": kwargs.get("prix_vente_min"),
            "prix_vente_ht": kwargs.get("prix_vente_ht"),
        }

        cursor = conn.cursor()
        updates = ", ".join(f"{key} = ?" for key, value in fields.items() if value is not None)
        values = [value for value in fields.values() if value is not None]
        values.append(id)

        cursor.execute(f"UPDATE articles SET {updates} WHERE id = ?", values)

        # Recalculer les champs dérivés
        cursor.execute("SELECT prix_achat_ht, prix_vente_ht, tva FROM articles WHERE id = ?", (id,))
        article = cursor.fetchone()
        if article:
            prix_achat_ht, prix_vente_ht, tva = article
            prix_moyen_pondere = prix_achat_ht
            marge_brute = calculer_marge_brute(prix_vente_ht, prix_moyen_pondere)
            prix_vente_ttc = calculer_prix_vente_ttc(prix_vente_ht, tva)

            cursor.execute("""
                UPDATE articles SET prix_moyen_pondere = ?, marge_brute = ?, prix_vente_ttc = ?
                WHERE id = ?
            """, (prix_moyen_pondere, marge_brute, prix_vente_ttc, id))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de la modification de l'article : {e}")
