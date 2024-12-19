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

        # Variable pour inclure les articles supprimés
        self.inclure_supprimes = tk.IntVar(value=0)

        # Frame pour les options supplémentaires
        options_frame = tk.Frame(self.root, pady=5)
        options_frame.pack(side=tk.TOP, fill=tk.X)

        # Case à cocher pour inclure les articles supprimés
        tk.Checkbutton(
            options_frame,
            text="Inclure les articles supprimés",
            variable=self.inclure_supprimes,
            command=self.afficher_articles
        ).pack(side=tk.LEFT, padx=10)


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
        self.configurer_tableau()
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
    
    def configurer_tableau(self):
        """
        Configure les colonnes du tableau avec des alignements différents pour les valeurs numériques et textuelles.
        """
        numeric_columns = {"id","stock", "stock_minimum", "prix_achat_ht", "prix_moyen_pondere",
                        "marge_brute", "prix_vente_ht", "prix_vente_ttc", "tva"}

        for col in self.article_table["columns"]:
            self.article_table.heading(col, text=col.replace("_", " ").capitalize())

            if col in numeric_columns:
                # Alignement à droite pour les valeurs numériques
                self.article_table.column(col, anchor="e", width=100)
            else:
                # Alignement à gauche pour les textes
                self.article_table.column(col, anchor="w", width=150)
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
        Marque un article comme supprimé au lieu de le supprimer physiquement.
        """
        selected = self.article_table.focus()
        if not selected:
            messagebox.showwarning("Supprimer", "Veuillez sélectionner un article.")
            return

        confirm = messagebox.askyesno("Supprimer", "Êtes-vous sûr de vouloir supprimer cet article ?")
        if confirm:
            item_values = self.article_table.item(selected, "values")
            article_id = item_values[0]  # Récupère l'ID de l'article
            try:
                conn = sqlite3.connect("appli.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE articles SET etat = 1 WHERE id = ?", (article_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Succès", "L'article a été marqué comme supprimé.")
                self.afficher_articles()  # Actualise le tableau
            except sqlite3.Error as e:
                messagebox.showerror("Erreur", f"Impossible de supprimer l'article : {e}")


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
        Inclut un filtre pour afficher ou exclure les articles marqués comme supprimés.
        """
        try:
            # Connexion à la base de données
            conn = sqlite3.connect("appli.db")
            cursor = conn.cursor()

            # Construire la requête SQL en fonction de la case à cocher "inclure_supprimes"
            if self.inclure_supprimes.get() == 1:
                query = f"""
                    SELECT id, nom, categorie, sous_categorie, description, stock, stock_minimum, fournisseur, 
                        ref_fournisseur, prix_achat_ht, prix_moyen_pondere, marge_brute, prix_vente_ht, 
                        prix_vente_ttc, tva
                    FROM articles
                    ORDER BY {self.colonne_tri} {self.ordre_tri}
                """
            else:
                query = f"""
                    SELECT id, nom, categorie, sous_categorie, description, stock, stock_minimum, fournisseur, 
                        ref_fournisseur, prix_achat_ht, prix_moyen_pondere, marge_brute, prix_vente_ht, 
                        prix_vente_ttc, tva
                    FROM articles
                    WHERE etat = 0
                    ORDER BY {self.colonne_tri} {self.ordre_tri}
                """

            # Exécuter la requête et récupérer les résultats
            cursor.execute(query)
            articles = cursor.fetchall()
            conn.close()

            # Effacer les lignes existantes dans le tableau
            for row in self.article_table.get_children():
                self.article_table.delete(row)

            # Ajouter les articles dans le tableau avec les formats appropriés
            for article in articles:
                article_list = list(article)  # Convertir en liste pour modification
                # Arrondi des champs numériques et ajout du signe '%' pour marge_brute
                if article_list[9] is not None:  # prix_achat_ht
                    article_list[9] = f"{article_list[9]:.3f}"
                if article_list[10] is not None:  # prix_moyen_pondere
                    article_list[10] = f"{article_list[10]:.3f}"
                if article_list[11] is not None:  # marge_brute
                    article_list[11] = f"{article_list[11]:.1f}%"
                if article_list[12] is not None:  # prix_vente_ht
                    article_list[12] = f"{article_list[12]:.3f}"
                if article_list[13] is not None:  # prix_vente_ttc
                    article_list[13] = f"{article_list[13]:.3f}"
                
                # Insérer les données dans le tableau
                self.article_table.insert("", tk.END, values=article_list)

        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Impossible de charger les articles : {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GestionArticles(root)
    root.mainloop()
