import sqlite3

def initialiser_parametres(conn):
    """
    Initialise la table des paramètres si elle n'existe pas et ajoute les valeurs par défaut.
    """
    try:
        cursor = conn.cursor()
        # Vérifie si la table existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parametres (
                cle TEXT PRIMARY KEY,
                valeur TEXT
            )
        """)
        # Ajouter les valeurs par défaut si elles n'existent pas
        defauts = {
            'sequence_facture': '192',
            'sequence_bl': '30',
            'tva_default': '19',
            'timbre_fiscal': '1',
            'theme_sombre': 'true'
        }
        for cle, valeur in defauts.items():
            cursor.execute("INSERT OR IGNORE INTO parametres (cle, valeur) VALUES (?, ?)", (cle, valeur))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'initialisation des paramètres : {e}")

def lire_parametre(conn, cle):
    """
    Lit la valeur d'un paramètre donné.
    :param conn: Connexion SQLite
    :param cle: Clé du paramètre
    :return: Valeur du paramètre ou None si la clé n'existe pas
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT valeur FROM parametres WHERE cle = ?", (cle,))
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Erreur lors de la lecture du paramètre '{cle}' : {e}")
        return None

def modifier_parametre(conn, cle, valeur):
    """
    Modifie la valeur d'un paramètre existant.
    :param conn: Connexion SQLite
    :param cle: Clé du paramètre
    :param valeur: Nouvelle valeur
    """
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE parametres SET valeur = ? WHERE cle = ?", (valeur, cle))
        if cursor.rowcount == 0:
            raise KeyError(f"La clé '{cle}' n'existe pas.")
        conn.commit()
    except KeyError as e:
        print(e)
    except sqlite3.Error as e:
        print(f"Erreur lors de la modification du paramètre '{cle}' : {e}")

def ajouter_parametre(conn, cle, valeur):
    """
    Ajoute un nouveau paramètre si la clé n'existe pas déjà.
    :param conn: Connexion SQLite
    :param cle: Clé du paramètre
    :param valeur: Valeur du paramètre
    """
    try:
        if lire_parametre(conn, cle) is not None:
            raise KeyError(f"Le paramètre '{cle}' existe déjà.")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO parametres (cle, valeur) VALUES (?, ?)", (cle, valeur))
        conn.commit()
    except KeyError as e:
        print(e)
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout du paramètre '{cle}' : {e}")

def incremente_sequence(conn, cle, prefixe=""):
    """
    Incrémente la valeur d'une séquence et retourne le numéro complet avec préfixe.
    :param conn: Connexion SQLite
    :param cle: Clé de la séquence
    :param prefixe: Préfixe à ajouter
    :return: Numéro incrémenté avec préfixe
    """
    try:
        valeur = lire_parametre(conn, cle)
        if valeur is None:
            valeur = 0
            ajouter_parametre(conn, cle, str(valeur))
        nouvelle_valeur = int(valeur) + 1
        modifier_parametre(conn, cle, str(nouvelle_valeur))
        return f"{prefixe}{nouvelle_valeur}"
    except sqlite3.Error as e:
        print(f"Erreur lors de l'incrémentation de la séquence '{cle}' : {e}")
        return None
