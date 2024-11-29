import sqlite3
from gestion_clients import (
    initialiser_clients,
    ajouter_client,
    modifier_client,
    supprimer_client,
    rechercher_client,
)


def exemple_utilisation():
    conn = sqlite3.connect("appli.db")
    initialiser_clients(conn)

    # Ajouter un client
    ajouter_client(conn, "Alice Martin", "456 Avenue B", "alice.martin@example.com", "9876543210", "MF456", "Nouveau client")

    # Modifier un client
    client = rechercher_client(conn, "nom", "Alice Martin")
    if client:
        print("Client avant modifié :", client)
        modifier_client(conn, client[0], remarque="Client VIP")
        print("Client apres modifié :", client)

    # Rechercher un client
    client = rechercher_client(conn, "email", "alice.martin@example.com")
    if client:
        print("Client trouvé :", client)

    # Supprimer un client
    if client:
        #supprimer_client(conn, client[0])
        print("rien")

    conn.close()


if __name__ == "__main__":
    exemple_utilisation()
