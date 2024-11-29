import sqlite3
import re
from datetime import datetime


def initialiser_clients(conn):
    """
    Initialise la table clients si elle n'existe pas.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                adresse TEXT DEFAULT NULL,
                email TEXT UNIQUE DEFAULT NULL,
                telephone TEXT UNIQUE DEFAULT NULL,
                matricule_fiscale TEXT UNIQUE DEFAULT NULL,
                remarque TEXT DEFAULT NULL,
                date_inscription TEXT DEFAULT CURRENT_DATE
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'initialisation de la table clients : {e}")


def valider_email(email):
    """
    Vérifie que l'email est au bon format.
    """
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Format de l'email invalide.")


def valider_telephone(telephone):
    """
    Vérifie que le téléphone contient uniquement des chiffres.
    """
    if telephone and not telephone.isdigit():
        raise ValueError("Le numéro de téléphone doit contenir uniquement des chiffres.")


def ajouter_client(conn, nom, adresse=None, email=None, telephone=None, matricule_fiscale=None, remarque=None):
    """
    Ajoute un nouveau client à la base.
    """
    try:
        valider_email(email)
        valider_telephone(telephone)

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clients (nom, adresse, email, telephone, matricule_fiscale, remarque)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nom, adresse, email, telephone, matricule_fiscale, remarque))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Erreur d'intégrité (email, téléphone ou matricule_fiscale déjà utilisé) : {e}")
    except sqlite3.Error as e:
        print(f"Erreur lors de l'ajout du client : {e}")


def modifier_client(conn, id, nom=None, adresse=None, email=None, telephone=None, matricule_fiscale=None, remarque=None):
    """
    Modifie les informations d'un client existant.
    """
    try:
        if email:
            valider_email(email)
        if telephone:
            valider_telephone(telephone)

        fields = {
            "nom": nom,
            "adresse": adresse,
            "email": email,
            "telephone": telephone,
            "matricule_fiscale": matricule_fiscale,
            "remarque": remarque,
        }
        updates = ", ".join(f"{key} = ?" for key, value in fields.items() if value is not None)
        values = [value for value in fields.values() if value is not None]
        values.append(id)

        cursor = conn.cursor()
        cursor.execute(f"UPDATE clients SET {updates} WHERE id = ?", values)
        if cursor.rowcount == 0:
            raise KeyError(f"Client avec ID {id} introuvable.")
        conn.commit()
    except KeyError as e:
        print(e)
    except sqlite3.Error as e:
        print(f"Erreur lors de la modification du client : {e}")


def supprimer_client(conn, id):
    """
    Supprime un client de la base.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clients WHERE id = ?", (id,))
        if cursor.rowcount == 0:
            raise KeyError(f"Client avec ID {id} introuvable.")
        conn.commit()
    except KeyError as e:
        print(e)
    except sqlite3.Error as e:
        print(f"Erreur lors de la suppression du client : {e}")


def rechercher_client(conn, critere, valeur):
    """
    Recherche un client selon un critère donné.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM clients WHERE {critere} = ?", (valeur,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erreur lors de la recherche du client : {e}")
        return None
