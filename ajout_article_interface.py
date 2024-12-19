import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3


class AjouterModifierArticle:
    def __init__(self, root, on_article_saved, mode="ajouter", article_data=None):
        """
        Initialise la fenêtre pour ajouter ou modifier un article.
        """
        self.root = root
        self.root.title("Ajouter un article" if mode == "ajouter" else "Modifier un article")
        self.root.geometry("1000x1000")

        self.on_article_saved = on_article_saved
        self.mode = mode
        self.article_data = article_data or {}
        self.fields = {}
        self.codes_barres = []

        self.create_form()
        if self.mode == "modifier":
            self.pre_remplir_champs()

    def create_form(self):
        """
        Crée les champs d'entrée pour l'article et configure les widgets.
        """
        form_frame = tk.Frame(self.root, padx=20, pady=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Champs principaux
        self.fields = {
            "nom": tk.StringVar(), "categorie": tk.StringVar(), "sous_categorie": tk.StringVar(),
            "description": tk.StringVar(), "stock": tk.IntVar(), "stock_minimum": tk.IntVar(),
            "fournisseur": tk.StringVar(), "ref_fournisseur": tk.StringVar(),
            "prix_achat_ht": tk.DoubleVar(), "tva": tk.DoubleVar(), "prix_vente_ht": tk.DoubleVar()
        }

        for i, (label, var) in enumerate(self.fields.items()):
            tk.Label(form_frame, text=label.replace("_", " ").capitalize()).grid(row=i, column=0, sticky="w", pady=5)
            tk.Entry(form_frame, textvariable=var).grid(row=i, column=1, sticky="ew", padx=10)

        # Champs calculés
        self.prix_moyen_pondere = self.create_calculated_field(form_frame, "Prix moyen pondéré", len(self.fields))
        self.marge_brute = self.create_calculated_field(form_frame, "Marge brute", len(self.fields) + 1)
        self.prix_vente_ttc = self.create_calculated_field(form_frame, "Prix de vente TTC", len(self.fields) + 2)

        # Zone des codes-barres
        tk.Label(self.root, text="Codes-Barres :").pack(pady=5)
        self.codes_barres_listbox = tk.Listbox(self.root, height=5)
        self.codes_barres_listbox.pack(fill=tk.BOTH, padx=20, pady=5)

        button_frame = tk.Frame(self.root)
        button_frame.pack()
        tk.Button(button_frame, text="Ajouter Code-Barre", command=self.ajouter_code_barre).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Supprimer Code-Barre", command=self.supprimer_code_barre).pack(side=tk.LEFT, padx=5)

        # Boutons d'action
        tk.Button(self.root, text="Valider", command=self.sauvegarder_article).pack(side=tk.RIGHT, padx=10, pady=10)
        tk.Button(self.root, text="Annuler", command=self.root.destroy).pack(side=tk.RIGHT, padx=10, pady=10)

    def create_calculated_field(self, parent, label, row):
        var = tk.StringVar()
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        entry = tk.Entry(parent, textvariable=var, state="disabled")
        entry.grid(row=row, column=1, sticky="ew", padx=10)
        return var

    def pre_remplir_champs(self):
        """
        Pré-remplit les champs avec les données existantes pour la modification,
        recalculant les champs calculés et affichant les codes-barres.
        """
        # Remplissage des champs principaux
        for key, var in self.fields.items():
            if key in self.article_data:
                var.set(self.article_data[key])

        # Conversion sécurisée pour les champs calculés
        try:
            prix_achat_ht = float(self.article_data.get('prix_achat_ht', 0.0))
            prix_vente_ht = float(self.article_data.get('prix_vente_ht', 0.0))
            tva = float(self.article_data.get('tva', 0.0))

            # Recalcul des champs calculés
            self.prix_moyen_pondere.set(f"{prix_achat_ht:.3f}")
            marge_brute = ((prix_vente_ht - prix_achat_ht) / prix_achat_ht * 100) if prix_achat_ht > 0 else 0.0
            self.marge_brute.set(f"{marge_brute:.3f}%")
            prix_ttc = prix_vente_ht * (1 + tva / 100)
            self.prix_vente_ttc.set(f"{prix_ttc:.3f}")
        except (ValueError, ZeroDivisionError):
            # Valeurs par défaut en cas d'erreur
            self.prix_moyen_pondere.set("0.000")
            self.marge_brute.set("0.0%")
            self.prix_vente_ttc.set("0.000")

        # Charger les codes-barres depuis la base de données
        self.charger_codes_barres()


    def charger_codes_barres(self):
        """
        Charge les codes-barres associés à l'article.
        """
        self.codes_barres_listbox.delete(0, tk.END)
        if self.article_data.get("id"):
            try:
                conn = sqlite3.connect("appli.db")
                cursor = conn.cursor()
                cursor.execute("SELECT code_barre FROM code_barres WHERE article_id = ?", (self.article_data["id"],))
                self.codes_barres = [row[0] for row in cursor.fetchall()]
                conn.close()
                for code in self.codes_barres:
                    self.codes_barres_listbox.insert(tk.END, code)
            except sqlite3.Error as e:
                messagebox.showerror("Erreur", f"Erreur chargement codes-barres : {e}")

    def ajouter_code_barre(self):
        code = simpledialog.askstring("Code-Barre", "Entrez un code-barre :")
        if code and code not in self.codes_barres:
            self.codes_barres.append(code)
            self.codes_barres_listbox.insert(tk.END, code)

    def supprimer_code_barre(self):
        selection = self.codes_barres_listbox.curselection()
        if selection:
            self.codes_barres.pop(selection[0])
            self.codes_barres_listbox.delete(selection[0])

    def sauvegarder_article(self):
        """
        Sauvegarde l'article (ajout ou modification) dans la base de données.
        Gère également l'ajout des codes-barres associés.
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
                # Requête d'ajout d'article
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
                article_id = cursor.lastrowid  # Récupérer l'ID de l'article inséré
            else:
                # Requête de modification d'article
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
                article_id = self.article_data["id"]

                # Supprimer les anciens codes-barres associés
                cursor.execute("DELETE FROM code_barres WHERE article_id = ?", (article_id,))

            # Insérer les nouveaux codes-barres
            for code_barre in self.codes_barres:
                cursor.execute("""
                    INSERT INTO code_barres (article_id, code_barre)
                    VALUES (?, ?)
                """, (article_id, code_barre))

            # Sauvegarder et fermer
            conn.commit()
            conn.close()

            messagebox.showinfo("Succès", "Article sauvegardé avec succès avec les codes-barres.")
            self.on_article_saved()
            self.root.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder l'article : {e}")
