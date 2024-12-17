import tkinter as tk
from tkinter import messagebox
import sqlite3


class AjouterModifierArticle:
    def __init__(self, root, on_article_saved, mode="ajouter", article_data=None):
        """
        Initialisation de la fenêtre d'ajout/modification d'article.
        :param root: Fenêtre parent (Toplevel).
        :param on_article_saved: Callback pour actualiser la liste après sauvegarde.
        :param mode: Mode de la fenêtre ("ajouter" ou "modifier").
        :param article_data: Dictionnaire contenant les données de l'article (pour la modification).
        """
        self.root = root
        self.root.title("Ajouter un article" if mode == "ajouter" else "Modifier un article")
        self.root.geometry("1500x600")

        self.on_article_saved = on_article_saved
        self.mode = mode
        self.article_data = article_data  # Données existantes (pour le mode "modifier")
        self.fields = {}

        self.create_form()
        if self.mode == "modifier" and self.article_data:
            self.pre_remplir_champs()

    def create_form(self):
        """
        Crée les champs d'entrée pour l'article.
        """
        form_frame = tk.Frame(self.root, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Champs principaux
        fields = [
            ("Nom", "nom", tk.StringVar),
            ("Catégorie", "categorie", tk.StringVar),
            ("Sous-catégorie", "sous_categorie", tk.StringVar),
            ("Description", "description", tk.StringVar),
            ("Stock", "stock", tk.IntVar),
            ("Stock minimum", "stock_minimum", tk.IntVar),
            ("Fournisseur", "fournisseur", tk.StringVar),
            ("Référence fournisseur", "ref_fournisseur", tk.StringVar),
            ("Prix d'achat HT", "prix_achat_ht", tk.DoubleVar),
            ("TVA (%)", "tva", tk.DoubleVar),
            ("Prix de vente HT", "prix_vente_ht", tk.DoubleVar)
        ]

        # Ajouter les champs au formulaire
        for i, (label, key, var_type) in enumerate(fields):
            tk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", pady=5)
            self.fields[key] = var_type()
            entry = tk.Entry(form_frame, textvariable=self.fields[key])
            entry.grid(row=i, column=1, sticky="ew", padx=10)
            # Liaison pour mise à jour des calculs dynamiques
            if key in ["prix_achat_ht", "tva", "prix_vente_ht"]:
                entry.bind("<KeyRelease>", self.update_calculated_fields)

        # Champs calculés (désactivés)
        tk.Label(form_frame, text="Prix moyen pondéré").grid(row=len(fields), column=0, sticky="w", pady=5)
        self.prix_moyen_pondere = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.prix_moyen_pondere, state="disabled").grid(row=len(fields), column=1, sticky="ew", padx=10)

        tk.Label(form_frame, text="Marge brute").grid(row=len(fields) + 1, column=0, sticky="w", pady=5)
        self.marge_brute = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.marge_brute, state="disabled").grid(row=len(fields) + 1, column=1, sticky="ew", padx=10)

        tk.Label(form_frame, text="Prix de vente TTC").grid(row=len(fields) + 2, column=0, sticky="w", pady=5)
        self.prix_vente_ttc = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.prix_vente_ttc, state="disabled").grid(row=len(fields) + 2, column=1, sticky="ew", padx=10)

        # Boutons valider et annuler
        button_frame = tk.Frame(self.root, pady=20)
        button_frame.pack()

        tk.Button(button_frame, text="Valider", command=self.sauvegarder_article).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Annuler", command=self.root.destroy).pack(side=tk.LEFT, padx=10)

    def pre_remplir_champs(self):
        """
        Pré-remplit les champs avec les données existantes pour la modification.
        """
        for key, var in self.fields.items():
            if key in self.article_data:
                var.set(self.article_data[key])
        # Champs calculés
        self.prix_moyen_pondere.set(self.article_data.get("prix_moyen_pondere", 0.0))
        self.marge_brute.set(str(self.article_data.get("marge_brute", 0.0)) + "%")
        self.prix_vente_ttc.set(self.article_data.get("prix_vente_ttc", 0.0))

    def update_calculated_fields(self, event=None):
        """
        Met à jour les champs calculés dynamiquement.
        """
        try:
            prix_achat_ht = float(self.fields["prix_achat_ht"].get())
            prix_vente_ht = float(self.fields["prix_vente_ht"].get())
            tva = float(self.fields["tva"].get())

            self.prix_moyen_pondere.set(f"{round(prix_achat_ht, 3):.3f}")
            self.marge_brute.set(f"{round((prix_vente_ht - prix_achat_ht) / prix_achat_ht * 100, 3):.3f}%")
            self.prix_vente_ttc.set(f"{round(prix_vente_ht * (1 + tva / 100), 3):.3f}")
        except ValueError:
            # Ignore les erreurs si les champs ne sont pas encore valides
            pass

    def sauvegarder_article(self):
        """
        Sauvegarde l'article (ajout ou modification) dans la base de données.
        """
        try:
            # Vérifier les champs obligatoires
            if not self.fields["nom"].get():
                messagebox.showerror("Erreur", "Le champ 'Nom' est obligatoire.")
                return

            # Collecte des données du formulaire
            article = {key: var.get() for key, var in self.fields.items()}
            article.update({
                "prix_moyen_pondere": round(float(self.prix_moyen_pondere.get()), 3) if self.prix_moyen_pondere.get() else 0.0,
                "marge_brute": round(float(self.marge_brute.get().replace("%", "")), 3) if self.marge_brute.get() else 0.0,
                "prix_vente_ttc": round(float(self.prix_vente_ttc.get()), 3) if self.prix_vente_ttc.get() else 0.0
            })

            # Connexion à la base
            conn = sqlite3.connect("appli.db")
            cursor = conn.cursor()

            if self.mode == "ajouter":
                # Requête d'ajout
                cursor.execute("""
                    INSERT INTO articles (nom, categorie, sous_categorie, description, stock, stock_minimum,
                                        fournisseur, ref_fournisseur, prix_achat_ht, tva, prix_vente_ht,
                                        prix_moyen_pondere, marge_brute, prix_vente_ttc)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article["nom"], article.get("categorie"), article.get("sous_categorie"), article.get("description"),
                    article.get("stock", 0), article.get("stock_minimum", 0), article.get("fournisseur"),
                    article.get("ref_fournisseur"), round(article.get("prix_achat_ht", 0.0), 3),
                    round(article.get("tva", 0.0), 3), round(article.get("prix_vente_ht", 0.0), 3),
                    article.get("prix_moyen_pondere", 0.0), article.get("marge_brute", 0.0),
                    article.get("prix_vente_ttc", 0.0)
                ))
            else:
                # Requête de modification
                cursor.execute("""
                    UPDATE articles SET
                        nom = ?, categorie = ?, sous_categorie = ?, description = ?, stock = ?, stock_minimum = ?,
                        fournisseur = ?, ref_fournisseur = ?, prix_achat_ht = ?, tva = ?, prix_vente_ht = ?,
                        prix_moyen_pondere = ?, marge_brute = ?, prix_vente_ttc = ?
                    WHERE id = ?
                """, (
                    article["nom"], article.get("categorie"), article.get("sous_categorie"), article.get("description"),
                    article.get("stock", 0), article.get("stock_minimum", 0), article.get("fournisseur"),
                    article.get("ref_fournisseur"), round(article.get("prix_achat_ht", 0.0), 3),
                    round(article.get("tva", 0.0), 3), round(article.get("prix_vente_ht", 0.0), 3),
                    article.get("prix_moyen_pondere", 0.0), article.get("marge_brute", 0.0),
                    article.get("prix_vente_ttc", 0.0), self.article_data["id"]
                ))

            # Sauvegarder et fermer
            conn.commit()
            conn.close()
            messagebox.showinfo("Succès", "Article sauvegardé avec succès.")
            self.on_article_saved()
            self.root.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder l'article : {e}")