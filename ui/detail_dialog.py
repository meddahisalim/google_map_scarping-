"""
Fenêtre de détail pour une fiche (lead) : affiche toutes les informations,
et propose deux actions :
 - Analyse totale : score d'opportunité + conseils commerciaux
 - Générer lettre : email de prospection personnalisé, prêt à copier/envoyer
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QApplication, QFileDialog, QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtCore import QUrl

from core.analysis import analyser_lead, generer_lettre


class DetailDialog(QDialog):
    def __init__(self, db, result_id, parent=None):
        super().__init__(parent)
        self.db = db
        self.result_id = result_id
        self.data = self._fetch_data()

        self.setWindowTitle(f"Détail — {self.data.get('name', '')}")
        self.resize(700, 650)

        self._build_ui()

    # ------------------------------------------------------------------
    def _fetch_data(self):
        row = self.db.get_by_id(self.result_id)
        if not row:
            return {}
        (_id, name, phone, email, address, category, country, wilaya,
         has_website, website_url, rating, reviews_count, status,
         maps_url, search_query, scraped_at) = row
        return {
            "id": _id, "name": name, "phone": phone, "email": email,
            "address": address, "category": category, "country": country,
            "wilaya": wilaya, "has_website": bool(has_website),
            "website_url": website_url, "rating": rating,
            "reviews_count": reviews_count, "status": status,
            "maps_url": maps_url, "search_query": search_query,
            "scraped_at": scraped_at,
        }

    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel(self.data.get("name", "—"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        subtitle = QLabel(
            f"{self.data.get('category', '')} · {self.data.get('wilaya', '')}, "
            f"{self.data.get('country', '')}"
        )
        subtitle.setStyleSheet("color: gray;")
        layout.addWidget(subtitle)

        # --- Grille d'infos ---
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        grid = QGridLayout(info_frame)

        rows = [
            ("Téléphone", self.data.get("phone") or "—"),
            ("Email", self.data.get("email") or "—"),
            ("Adresse", self.data.get("address") or "—"),
            ("Site web", "Oui" if self.data.get("has_website") else "Non"),
            ("URL du site", self.data.get("website_url") or "—"),
            ("Note", (self.data.get("rating") or "—") + " / 5" if self.data.get("rating") else "—"),
            ("Nombre d'avis", self.data.get("reviews_count") or "—"),
            ("Statut", self.data.get("status") or "—"),
            ("Recherche d'origine", self.data.get("search_query") or "—"),
            ("Date de collecte", self.data.get("scraped_at") or "—"),
        ]
        for i, (label, value) in enumerate(rows):
            lbl = QLabel(f"{label} :")
            lbl.setStyleSheet("font-weight: bold;")
            val = QLabel(str(value))
            val.setWordWrap(True)
            val.setTextInteractionFlags(Qt.TextSelectableByMouse)
            grid.addWidget(lbl, i, 0)
            grid.addWidget(val, i, 1)

        layout.addWidget(info_frame)

        # --- Lien Google Maps cliquable ---
        if self.data.get("maps_url"):
            maps_btn = QPushButton("📍 Ouvrir la fiche Google Maps")
            maps_btn.clicked.connect(
                lambda: QDesktopServices.openUrl(QUrl(self.data["maps_url"]))
            )
            layout.addWidget(maps_btn)

        # --- Boutons d'action ---
        action_row = QHBoxLayout()
        self.analyse_btn = QPushButton("🔍 Analyse totale + conseils")
        self.analyse_btn.clicked.connect(self._show_analysis)
        self.letter_btn = QPushButton("✉️ Générer lettre de prospection")
        self.letter_btn.clicked.connect(self._show_letter)
        action_row.addWidget(self.analyse_btn)
        action_row.addWidget(self.letter_btn)
        layout.addLayout(action_row)

        # --- Champ signataire (pour la lettre) ---
        sign_row = QHBoxLayout()
        sign_row.addWidget(QLabel("Signer la lettre en tant que :"))
        self.signataire_input = QLineEdit("Salim")
        sign_row.addWidget(self.signataire_input)
        layout.addLayout(sign_row)

        # --- Zone de résultat (analyse ou lettre générée) ---
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setPlaceholderText(
            "Clique sur 'Analyse totale' ou 'Générer lettre' pour voir le résultat ici."
        )
        layout.addWidget(self.output_box, stretch=1)

        # --- Copier / Enregistrer (visibles seulement quand il y a du contenu) ---
        output_btn_row = QHBoxLayout()
        self.copy_btn = QPushButton("📋 Copier")
        self.copy_btn.clicked.connect(self._copy_output)
        self.save_btn = QPushButton("💾 Enregistrer en .txt")
        self.save_btn.clicked.connect(self._save_output)
        output_btn_row.addWidget(self.copy_btn)
        output_btn_row.addWidget(self.save_btn)
        layout.addLayout(output_btn_row)

        # --- Retour ---
        back_btn = QPushButton("⬅ Retour")
        back_btn.clicked.connect(self.close)
        layout.addWidget(back_btn)

    # ------------------------------------------------------------------
    def _show_analysis(self):
        text = analyser_lead(self.data)
        self.output_box.setPlainText(text)

    def _show_letter(self):
        signataire = self.signataire_input.text().strip() or "Salim"
        text = generer_lettre(self.data, signataire=signataire)
        self.output_box.setPlainText(text)

    def _copy_output(self):
        text = self.output_box.toPlainText()
        if not text:
            QMessageBox.information(self, "Rien à copier",
                                     "Génère d'abord une analyse ou une lettre.")
            return
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copié", "Le texte a été copié dans le presse-papier.")

    def _save_output(self):
        text = self.output_box.toPlainText()
        if not text:
            QMessageBox.information(self, "Rien à enregistrer",
                                     "Génère d'abord une analyse ou une lettre.")
            return
        safe_name = "".join(c if c.isalnum() else "_" for c in (self.data.get("name") or "lead"))
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer", f"{safe_name}.txt", "Texte (*.txt)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            QMessageBox.information(self, "Enregistré", f"Fichier enregistré :\n{path}")
