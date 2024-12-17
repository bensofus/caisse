import tkinter as tk
from tkinter import ttk, messagebox
from ajout_article_interface import AjouterModifierArticle
import sqlite3


class GestionArticles:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Articles")
        self.root.geometry("1500x600")

        # Tableau pour afficher les articles
        self.article_table = ttk.Treeview(self.root, columns=(
            "id", "nom", "categorie", "sous_categorie", "description", "stock",
            "stock_minimum", "fournisseur", "ref_fournisseur", "prix_achat_ht",
            "prix_moyen_pondere", "marge_brute", "prix_vente_ht",
            "prix_vente_ttc", "tva"
        ), show="headings", height=15)

        # Configuration des colonnes
        for col in self.article_table["columns"]:
            self.article_table.heading(col, text=col.replace("_", " ").capitalize())
            self.article_table.column(col, width=100)

        self.article_table.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Frame pour les boutons
        button_frame = tk.Frame(self.root, pady=10)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(button_frame, text="Ajouter", command=self.ajouter_article).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Modifier", command=self.modifier_article).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Supprimer", command=self.supprimer_article).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Rechercher", command=self.rechercher_article).pack(side=tk.LEFT, padx=10)
        # Initialisation des attributs de tri
        self.colonne_tri = "id"  # Tri par défaut
        self.ordre_tri = "ASC"   # Ordre par défaut

        # Associer le tri dynamique
        for col in ["id", "nom", "categorie", "sous_categorie", "description", "stock",
            "stock_minimum", "fournisseur", "ref_fournisseur", "prix_achat_ht",
            "prix_moyen_pondere", "marge_brute", "prix_vente_ht",
            "prix_vente_ttc", "tva"]:
            self.article_table.heading(col, text=col.capitalize(),
                                        command=lambda c=col: self.afficher_articles_avec_tri(c))

        self.afficher_articles()

    def ajouter_article(self):
        """
        Ouvre une fenêtre pour ajouter un nouvel article.
        """
        def refresh_table():
            """
            Rafraîchit automatiquement le tableau principal après ajout.
            """
            self.afficher_articles()

        # Ouvre une fenêtre pour ajouter un article
        ajouter_window = tk.Toplevel(self.root)
        AjouterModifierArticle(ajouter_window, refresh_table, mode="ajouter")
    
    def afficher_articles_avec_tri(self, colonne):
        """
        Charge et affiche tous les articles triés par une colonne spécifique.
        """
        self.ordre_tri = "DESC" if self.colonne_tri == colonne and self.ordre_tri == "ASC" else "ASC"
        self.colonne_tri = colonne
        self.afficher_articles()



    def modifier_article(self):
        """
        Ouvre une fenêtre pour modifier un article sélectionné.
        """
        selected = self.article_table.focus()  # Récupère l'article sélectionné
        if not selected:
            messagebox.showwarning("Modifier", "Veuillez sélectionner un article.")
            return

        # Récupérer les données de l'article sélectionné
        item_values = self.article_table.item(selected, "values")
        article_data = {
            "id": item_values[0],
            "nom": item_values[1],
            "categorie": item_values[2],
            "sous_categorie": item_values[3],
            "description": item_values[4],
            "stock": item_values[5],
            "stock_minimum": item_values[6],
            "fournisseur": item_values[7],
            "ref_fournisseur": item_values[8],
            "prix_achat_ht": item_values[9],
            "prix_moyen_pondere": item_values[10],
            "marge_brute": item_values[11],
            "prix_vente_ht": item_values[12],
            "prix_vente_ttc": item_values[13],
            "tva": item_values[14]
        }
        def refresh_table():
            """
            Rafraîchit automatiquement le tableau principal après modification.
            """
            self.afficher_articles()
        # Ouvre une fenêtre pour modifier l'article
        modifier_window = tk.Toplevel(self.root)
        AjouterModifierArticle(modifier_window, refresh_table, mode="modifier", article_data=article_data)


    def supprimer_article(self):
        """
        Supprimer un article sélectionné.
        """
        selected = self.article_table.focus()
        if not selected:
            messagebox.showwarning("Supprimer", "Veuillez sélectionner un article.")
            return
        confirm = messagebox.askyesno("Supprimer", "Êtes-vous sûr de vouloir supprimer cet article ?")
        if confirm:
            # Placeholder pour la suppression
            messagebox.showinfo("Supprimer", "Fonctionnalité Supprimer un article à implémenter.")

    def rechercher_article(self):
        """
        Rechercher un article par nom.
        """
        search_window = tk.Toplevel(self.root)
        search_window.title("Rechercher un article")
        search_window.geometry("400x200")

        tk.Label(search_window, text="Nom de l'article :").pack(pady=10)
        search_entry = tk.Entry(search_window, width=30)
        search_entry.pack()

        def effectuer_recherche():
            terme = search_entry.get()
            if not terme:
                messagebox.showwarning("Rechercher", "Veuillez entrer un nom.")
                return
            # Placeholder pour la recherche dans la base
            messagebox.showinfo("Rechercher", f"Recherche pour : {terme}")
            search_window.destroy()

        tk.Button(search_window, text="Rechercher", command=effectuer_recherche).pack(pady=20)

    def afficher_resultats(self, articles):
        """
        Affiche les articles dans le tableau.
        """
        for row in self.article_table.get_children():
            self.article_table.delete(row)
        for article in articles:
            self.article_table.insert("", tk.END, values=article)
    
    def afficher_articles(self):
        """
        Charge et affiche tous les articles depuis la base de données dans le tableau.
        """
        try:
            # Connexion à la base de données
            conn = sqlite3.connect("appli.db")
            cursor = conn.cursor()
            query = f"""
                SELECT id, nom, categorie, sous_categorie, description, stock, stock_minimum, fournisseur, ref_fournisseur,
                    prix_achat_ht, prix_moyen_pondere, marge_brute, prix_vente_ht, prix_vente_ttc, tva
                FROM articles
                ORDER BY {self.colonne_tri} {self.ordre_tri}
            """
            cursor.execute(query)
            articles = cursor.fetchall()
            conn.close()

            # Efface le tableau existant
            for row in self.article_table.get_children():
                self.article_table.delete(row)

            # Ajoute les nouveaux articles avec les champs arrondis et le signe '%'
            for article in articles:
                article_list = list(article)  # Convertit le tuple en liste pour modification
                # Arrondi des champs monétaires
                if article_list[9] is not None:  # prix_achat_ht
                    article_list[9] = f"{article_list[9]:.3f}"
                if article_list[10] is not None:  # prix_moyen_pondere
                    article_list[10] = f"{article_list[10]:.3f}"
                if article_list[11] is not None:  # marge_brute
                    article_list[11] = f"{article_list[11]:.1f}%"  # Affiche avec 1 décimale et %
                if article_list[12] is not None:  # prix_vente_ht
                    article_list[12] = f"{article_list[12]:.3f}"
                if article_list[13] is not None:  # prix_vente_ttc
                    article_list[13] = f"{article_list[13]:.3f}"
                # Ajout au tableau
                self.article_table.insert("", tk.END, values=article_list)

        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Impossible de charger les articles : {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GestionArticles(root)
    root.mainloop()
