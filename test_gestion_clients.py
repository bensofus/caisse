import sqlite3
from gestion_clients import (
    initialiser_clients,
    ajouter_client,
    modifier_client,
    supprimer_client,
    rechercher_client,
)


def test_gestion_clients():
    conn = sqlite3.connect("test_appli.db")
    initialiser_clients(conn)

    # Test ajout de clients
    ajouter_client(conn, "Jean Dupont", "123 Rue A", "jean.dupont@example.com", "1234567890", "MF123", "Bon client")
    assert rechercher_client(conn, "nom", "Jean Dupont") is not None

    # Test ajout avec valeurs par défaut
    ajouter_client(conn, "Marie Curie")
    assert rechercher_client(conn, "nom", "Marie Curie") is not None

    # Test modification de client
    client = rechercher_client(conn, "nom", "Jean Dupont")
    modifier_client(conn, client[0], email="jean.new@example.com")
    assert rechercher_client(conn, "email", "jean.new@example.com") is not None

    # Test suppression de client
    client_id = client[0]
    supprimer_client(conn, client_id)
    assert rechercher_client(conn, "id", client_id) is None

    # Test cas limites
    try:
        ajouter_client(conn, "Dupont", email="malforme")
    except ValueError as e:
        assert str(e) == "Format de l'email invalide."

    try:
        ajouter_client(conn, "Dupont", telephone="abc123")
    except ValueError as e:
        assert str(e) == "Le numéro de téléphone doit contenir uniquement des chiffres."

    print("Tous les tests ont réussi.")
    conn.close()


if __name__ == "__main__":
    test_gestion_clients()
