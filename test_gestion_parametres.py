import sqlite3
from gestion_parametres import (
    initialiser_parametres,
    lire_parametre,
    modifier_parametre,
    ajouter_parametre,
    incremente_sequence,
)

def test_gestion_parametres():
    # Création de la base de test
    conn = sqlite3.connect("appli.db")
    initialiser_parametres(conn)

    # Test initialisation
    assert lire_parametre(conn, "sequence_facture") == "192"
    assert lire_parametre(conn, "tva_default") == "19"
    
    # Test lecture d'un paramètre inexistant
    assert lire_parametre(conn, "inexistant") is None

    # Test modification d'un paramètre
    modifier_parametre(conn, "sequence_facture", "200")
    assert lire_parametre(conn, "sequence_facture") == "200"

    # Test ajout d'un paramètre
    ajouter_parametre(conn, "nouveau_param", "test")
    assert lire_parametre(conn, "nouveau_param") == "test"

    # Test incrémentation d'une séquence
    assert incremente_sequence(conn, "sequence_facture", "FAC-") == "FAC-201"

    # Test incrémentation d'une séquence inexistante
    assert incremente_sequence(conn, "nouvelle_sequence", "SEQ-") == "SEQ-1"

    print("Tous les tests ont réussi.")

    # Nettoyage
    conn.close()

if __name__ == "__main__":
    test_gestion_parametres()
