"""
Main PyQt5 Interface:

- Form: Area -> Country -> Wilaya/Region (cascade) + Activity Type
- Speed ​​setting (fast / normal / cautious)
- Search / Stop button
- Status bar + progress log
- Enhanced results table (name, phone, address, category, country, wilaya, website, rating, reviews, status)
- Filter "Display only without website"
- CSV export
"""

import csv
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QCheckBox, QTextEdit, QFileDialog, QMessageBox, QHeaderView,
    QProgressBar, QSpinBox
)
from PyQt5.QtCore import QThread, pyqtSignal

from core.database import Database
from core.scraper import GoogleMapsScraper
from core.locations import ZONES, get_countries, get_regions


class ScraperWorker(QThread):
    result_found = pyqtSignal(dict)
    log_message = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, activity_type, region, country, max_results, headless, speed):
        super().__init__()
        self.activity_type = activity_type
        self.region = region
        self.country = country
        self.max_results = max_results
        self.headless = headless
        self.speed = speed
        self.scraper = None

    def run(self):
        count = 0
        try:
            self.scraper = GoogleMapsScraper(
                headless=self.headless,
                max_results=self.max_results,
                log_callback=self.log_message.emit,
                speed=self.speed,
            )
            for data in self.scraper.search(self.activity_type, self.region, self.country):
                self.result_found.emit(data)
                count += 1
        except Exception as e:
            self.log_message.emit(f"Erreur : {e}")
        finally:
            if self.scraper:
                self.scraper.close()
            self.finished_signal.emit(count)

    def stop(self):
        if self.scraper:
            self.scraper.stop()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Maps Lead Scraper Companies without a website")
        self.resize(1300, 750)

        self.db = Database("results.db")
        self.worker = None

        self._build_ui()
        self._load_from_db()

    # -----------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        row1 = QHBoxLayout()

        self.zone_combo = QComboBox()
        self.zone_combo.addItems(ZONES)
        self.zone_combo.currentTextChanged.connect(self._on_zone_changed)

        self.country_combo = QComboBox()
        self.country_combo.currentTextChanged.connect(self._on_country_changed)

        self.region_combo = QComboBox()
        self.region_combo.setEditable(True)

        row1.addWidget(QLabel("Zone :"))
        row1.addWidget(self.zone_combo)
        row1.addWidget(QLabel("Pays :"))
        row1.addWidget(self.country_combo)
        row1.addWidget(QLabel("Wilaya / Région / État :"))
        row1.addWidget(self.region_combo)
        main_layout.addLayout(row1)

        row2 = QHBoxLayout()

        self.activity_input = QLineEdit()
        self.activity_input.setPlaceholderText("Ex: hôtel, restaurant, pharmacie, boutique...")

        self.max_results_spin = QSpinBox()
        self.max_results_spin.setRange(5, 200)
        self.max_results_spin.setValue(40)

        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["rapide", "normal", "prudent"])
        self.speed_combo.setCurrentText("normal")
        self.speed_combo.setToolTip(
            "rapide = plus vite mais plus de risque de blocage Google\n"
            "prudent = plus lent mais plus fiable/qualité de données"
        )

        self.headless_check = QCheckBox("Mode invisible (headless)")
        self.headless_check.setChecked(False)
        self.headless_check.setToolTip(
            "Laisse décoché au début pour voir Chrome travailler et repérer un blocage."
        )

        row2.addWidget(QLabel("Type d'activité :"))
        row2.addWidget(self.activity_input)
        row2.addWidget(QLabel("Max résultats :"))
        row2.addWidget(self.max_results_spin)
        row2.addWidget(QLabel("Vitesse :"))
        row2.addWidget(self.speed_combo)
        row2.addWidget(self.headless_check)
        main_layout.addLayout(row2)

        # --- Boutons ---
        btn_layout = QHBoxLayout()
        self.search_btn = QPushButton("🔍 Rechercher")
        self.search_btn.clicked.connect(self.start_search)
        self.stop_btn = QPushButton("⏹ Arrêter")
        self.stop_btn.clicked.connect(self.stop_search)
        self.stop_btn.setEnabled(False)
        self.export_btn = QPushButton("⬇ Exporter CSV")
        self.export_btn.clicked.connect(self.export_csv)
        self.clear_btn = QPushButton("🗑 Vider la base")
        self.clear_btn.clicked.connect(self.clear_db)

        self.only_no_website_check = QCheckBox("Afficher seulement SANS site web")
        self.only_no_website_check.setChecked(True)
        self.only_no_website_check.stateChanged.connect(self._load_from_db)

        btn_layout.addWidget(self.search_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.only_no_website_check)
        main_layout.addLayout(btn_layout)

        # --- Progress + status ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Prêt.")
        main_layout.addWidget(self.status_label)

        # --- Table résultats (colonnes enrichies) ---
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels(
            ["Nom", "Téléphone", "Adresse", "Catégorie", "Pays", "Wilaya/Région",
             "Site web ?", "Note", "Avis", "Statut"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.table, stretch=3)

        # --- Log ---
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(140)
        main_layout.addWidget(self.log_box, stretch=1)

        # Initialiser les cascades Zone -> Pays -> Wilaya
        self._on_zone_changed(self.zone_combo.currentText())

    # ---------------------------------------------------------------
    def _on_zone_changed(self, zone):
        self.country_combo.blockSignals(True)
        self.country_combo.clear()
        self.country_combo.addItems(get_countries(zone))
        self.country_combo.blockSignals(False)
        self._on_country_changed(self.country_combo.currentText())

    def _on_country_changed(self, country):
        zone = self.zone_combo.currentText()
        self.region_combo.clear()
        self.region_combo.addItems(get_regions(zone, country))

    # --------------------------------------------------------
    def start_search(self):
        country = self.country_combo.currentText().strip()
        region = self.region_combo.currentText().strip()
        activity = self.activity_input.text().strip()

        if not country or not region or not activity:
            QMessageBox.warning(self, "Champs manquants",
                                 "Merci de renseigner le pays, la wilaya/région et le type d'activité.")
            return

        self.log_box.clear()
        self.search_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Recherche en cours : {activity} - {region}, {country} ...")

        self.worker = ScraperWorker(
            activity_type=activity,
            region=region,
            country=country,
            max_results=self.max_results_spin.value(),
            headless=self.headless_check.isChecked(),
            speed=self.speed_combo.currentText(),
        )
        self.worker.result_found.connect(self._on_result_found)
        self.worker.log_message.connect(self._on_log)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()

    def stop_search(self):
        if self.worker:
            self.worker.stop()
            self.status_label.setText("Arrêt en cours...")

    def _on_result_found(self, data):
        self.db.insert_result(data)
        self._load_from_db()

    def _on_log(self, msg):
        self.log_box.append(msg)

    def _on_finished(self, count):
        self.search_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Terminé. {count} fiches traitées. Total en base : {self.db.count()}")

    # --------------------------------------------------------
    def _load_from_db(self):
        only_no_website = self.only_no_website_check.isChecked()
        rows = self.db.get_all_results(only_without_website=only_no_website)

        self.table.setRowCount(0)
        for row in rows:
            (_id, name, phone, address, category, country, wilaya,
             has_website, website_url, rating, reviews_count, status,
             maps_url, scraped_at) = row

            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(name))
            self.table.setItem(r, 1, QTableWidgetItem(phone))
            self.table.setItem(r, 2, QTableWidgetItem(address))
            self.table.setItem(r, 3, QTableWidgetItem(category))
            self.table.setItem(r, 4, QTableWidgetItem(country))
            self.table.setItem(r, 5, QTableWidgetItem(wilaya))
            self.table.setItem(r, 6, QTableWidgetItem("Oui" if has_website else "Non"))
            self.table.setItem(r, 7, QTableWidgetItem(rating or ""))
            self.table.setItem(r, 8, QTableWidgetItem(reviews_count or ""))
            self.table.setItem(r, 9, QTableWidgetItem(status or ""))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exporter en CSV", "resultats.csv", "CSV (*.csv)")
        if not path:
            return
        only_no_website = self.only_no_website_check.isChecked()
        rows = self.db.get_all_results(only_without_website=only_no_website)
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Nom", "Téléphone", "Adresse", "Catégorie", "Pays", "Wilaya/Région",
                              "Site web", "Note", "Avis", "Statut", "Lien Maps", "Date"])
            for row in rows:
                (_id, name, phone, address, category, country, wilaya,
                 has_website, website_url, rating, reviews_count, status,
                 maps_url, scraped_at) = row
                writer.writerow([name, phone, address, category, country, wilaya,
                                  "Oui" if has_website else "Non", rating, reviews_count,
                                  status, maps_url, scraped_at])
        QMessageBox.information(self, "Export terminé", f"Fichier exporté :\n{path}")

    def clear_db(self):
        reply = QMessageBox.question(
            self, "Confirmer", "Voulez-vous vraiment vider toute la base de données ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.delete_all()
            self._load_from_db()
            self.status_label.setText("Base de données vidée.")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(3000)
        event.accept()
