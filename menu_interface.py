import tkinter as tk
from tkinter import ttk
from gestion_articles_interface import GestionArticles


class MenuInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de la Caisse")
        self.root.geometry("800x600")

        # Barre de statut en bas
        self.status_bar = tk.Label(self.root, text="Prêt", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Frame principale pour les boutons
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Boutons pour les fonctionnalités principales
        self.add_button(main_frame, "Gestion des articles", self.gestion_articles)
        self.add_button(main_frame, "Gestion des clients", self.gestion_clients)
        self.add_button(main_frame, "Créer une vente", self.creer_vente)
        self.add_button(main_frame, "Rapport journalier", self.rapport_journalier)
        self.add_button(main_frame, "Paramètres", self.parametres)

    def add_button(self, parent, text, command):
        """
        Ajoute un bouton dans le parent avec le texte et la commande donnés.
        """
        btn = tk.Button(parent, text=text, width=25, height=2, command=command)
        btn.pack(pady=10)

    # Fonctions de placeholder pour les boutons
    def gestion_articles(self):
        """
        Ouvre la fenêtre de gestion des articles.
        """
        articles_window = tk.Toplevel(self.root)  # Crée une nouvelle fenêtre
        GestionArticles(articles_window)         # Passe la fenêtre à la classe GestionArticles
        self.update_status("Fenêtre de gestion des articles ouverte.")

    def gestion_clients(self):
        self.update_status("Gestion des clients ouverte.")

    def creer_vente(self):
        self.update_status("Création d'une vente ouverte.")

    def rapport_journalier(self):
        self.update_status("Rapport journalier généré.")

    def parametres(self):
        self.update_status("Paramètres ouverts.")

    def update_status(self, message):
        """
        Met à jour le texte de la barre de statut.
        """
        self.status_bar.config(text=message)


if __name__ == "__main__":
    root = tk.Tk()
    app = MenuInterface(root)
    root.mainloop()
