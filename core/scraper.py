"""

- Robust phone/address extraction (multiple fallback selectors, direct reading of data-item-id / aria-label attributes rather than the visible text, which varied depending on the layout)

- Additional columns: number of reviews, open/closed status

- Configurable speed (fast / normal / cautious): adjusts wait times to speed up or improve reliability on slow connections
- Smart waits (WebDriverWait) instead of fixed time.sleep wherever possible -> faster on average
"""

import time
import random
import re
import urllib.parse
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, StaleElementReferenceException,
    WebDriverException,
)

DEBUG_DIR = "debug"

SPEED_PROFILES = {
    "rapide":  dict(page_wait=6,  between_min=0.25, between_max=0.6, scroll_pause=0.6),
    "normal":  dict(page_wait=9,  between_min=0.6,  between_max=1.2, scroll_pause=1.0),
    "prudent": dict(page_wait=14, between_min=1.2,  between_max=2.2, scroll_pause=1.6),
}


class GoogleMapsScraper:
    def __init__(self, headless=True, max_results=40, log_callback=None, speed="normal"):
        self.max_results = max_results
        self.log_callback = log_callback or (lambda msg: None)
        self.profile = SPEED_PROFILES.get(speed, SPEED_PROFILES["normal"])
        self.driver = self._init_driver(headless)
        self._stop_requested = False

    def stop(self):
        self._stop_requested = True

    def _log(self, msg):
        self.log_callback(msg)

    # ----------------------------------------------------------------
    def _init_driver(self, headless):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--lang=fr-FR")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2
        })

        try:
            driver = webdriver.Chrome(options=options)
        except WebDriverException as e:
            self._log(
                "❌ Impossible de démarrer Chrome. Vérifie que Google Chrome "
                f"est bien installé sur ce PC. Détail technique : {e}"
            )
            raise
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
        )
        driver.set_page_load_timeout(25)
        return driver

    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass

    def _save_debug(self, name):
        try:
            os.makedirs(DEBUG_DIR, exist_ok=True)
            self.driver.save_screenshot(os.path.join(DEBUG_DIR, f"{name}.png"))
            with open(os.path.join(DEBUG_DIR, f"{name}.html"), "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            self._log(f"Debug sauvegardé dans '{DEBUG_DIR}/' ({name}.png / {name}.html)")
        except Exception as e:
            self._log(f"Impossible de sauvegarder le debug : {e}")

    def _handle_consent(self):
        consent_texts = [
            "Tout accepter", "J'accepte", "Accepter tout", "Accept all",
            "I agree", "Tout refuser sauf l'essentiel",
        ]
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
        except TimeoutException:
            return False
        for text in consent_texts:
            try:
                btn = self.driver.find_element(
                    By.XPATH, f'//button[.//span[contains(text(), "{text}")] or contains(text(), "{text}")]'
                )
                btn.click()
                self._log(f"Popup de consentement fermé ('{text}').")
                time.sleep(1)
                return True
            except NoSuchElementException:
                continue
        return False

    # ------------------------------------------------------------
    def search(self, activity_type: str, region: str, country: str):
        """
        Génère les résultats un par un. `region` = wilaya/état/province,
        `country` = pays (ex: Algérie, France, États-Unis...).
        """
        query = f"{activity_type} {region} {country}"
        self._log(f"Recherche : {query}")

        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/maps/search/{encoded_query}?hl=fr"
        self._log(f"Ouverture de : {url}")

        try:
            self.driver.get(url)
        except TimeoutException:
            pass  
        time.sleep(1.2)

        self._handle_consent()

        feed = None
        for sel in ['//div[@role="feed"]',
                    '//div[contains(@aria-label, "Résultats pour")]',
                    '//div[contains(@aria-label, "Results for")]']:
            try:
                WebDriverWait(self.driver, self.profile["page_wait"]).until(
                    EC.presence_of_element_located((By.XPATH, sel))
                )
                feed = self.driver.find_element(By.XPATH, sel)
                break
            except TimeoutException:
                continue

        if feed is None:
            self._log("❌ Aucun panneau de résultats trouvé (popup non fermé, "
                       "recherche bloquée, ou mise en page Google modifiée).")
            self._save_debug("no_feed_found")
            return

        
        seen_links = []
        seen_set = set()
        stable_rounds = 0

        while len(seen_links) < self.max_results and stable_rounds < 4:
            if self._stop_requested:
                self._log("Arrêt demandé par l'utilisateur.")
                break

            cards = feed.find_elements(By.XPATH, './/a[contains(@href, "/maps/place/")]')
            new_found = 0
            for c in cards:
                href = c.get_attribute("href")
                if href and href not in seen_set:
                    seen_set.add(href)
                    seen_links.append(href)
                    new_found += 1

            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", feed
            )
            time.sleep(self.profile["scroll_pause"])

            stable_rounds = stable_rounds + 1 if new_found == 0 else 0

        if not seen_links:
            self._log("❌ Le panneau de résultats existe mais aucune fiche n'a été détectée.")
            self._save_debug("feed_found_but_no_links")
            return

        self._log(f"{len(seen_links)} fiches détectées, extraction en cours...")
        links = seen_links[: self.max_results]

        for i, link in enumerate(links, start=1):
            if self._stop_requested:
                break
            try:
                data = self._extract_place(link, activity_type, region, country, query)
                if data:
                    tel_status = data["phone"] if data["phone"] else "sans tél."
                    web_status = "AVEC site" if data["has_website"] else "SANS site web"
                    self._log(f"[{i}/{len(links)}] {data['name']} — {tel_status} — {web_status}")
                    yield data
            except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
                self._log(f"[{i}/{len(links)}] Fiche ignorée (erreur d'extraction).")
                continue
            time.sleep(random.uniform(self.profile["between_min"], self.profile["between_max"]))

    # ---------------------------------------
    def _first_match(self, xpaths):
        """Essaie plusieurs XPath dans l'ordre, renvoie le premier élément trouvé ou None."""
        for xp in xpaths:
            try:
                return self.driver.find_element(By.XPATH, xp)
            except NoSuchElementException:
                continue
        return None

    def _extract_phone(self):
        el = self._first_match([
            '//button[starts-with(@data-item-id, "phone:tel:")]',
            '//a[starts-with(@href, "tel:")]',
            '//button[contains(@aria-label, "Téléphone")]',
            '//button[contains(@aria-label, "Phone")]',
        ])
        if el is None:
            return ""
        item_id = el.get_attribute("data-item-id") or ""
        if "phone:tel:" in item_id:
            return item_id.split("phone:tel:")[-1].strip()
        href = el.get_attribute("href") or ""
        if href.startswith("tel:"):
            return href.replace("tel:", "").strip()
        aria = el.get_attribute("aria-label") or ""
        m = re.search(r"[\d][\d\s.\-]{6,}", aria)
        if m:
            return m.group(0).strip()
        text = el.text.strip()
        m = re.search(r"[\d][\d\s.\-]{6,}", text)
        return m.group(0).strip() if m else text

    def _extract_address(self):
        el = self._first_match([
            '//button[starts-with(@data-item-id, "address")]',
            '//button[contains(@aria-label, "Adresse")]',
            '//button[contains(@aria-label, "Address")]',
        ])
        if el is None:
            return ""
        aria = el.get_attribute("aria-label") or ""
        for prefix in ["Adresse : ", "Adresse :", "Address: ", "Address:"]:
            if aria.startswith(prefix):
                return aria[len(prefix):].strip()
        text = el.text.strip()
        return text if text else aria

    def _extract_website(self):
        el = self._first_match([
            '//a[starts-with(@data-item-id, "authority")]',
            '//a[contains(@aria-label, "Site Web")]',
            '//a[contains(@aria-label, "Website")]',
        ])
        if el is None:
            return ""
        return el.get_attribute("href") or ""

    def _extract_category(self, fallback):
        el = self._first_match([
            '//button[contains(@jsaction, "category")]',
            '//button[@jsaction="pane.rating.category"]',
        ])
        if el is None:
            return fallback
        return el.text.strip() or fallback

    def _extract_rating(self):
        el = self._first_match([
            '//div[@jsaction and contains(@aria-label, "étoiles")]',
            '//span[contains(@aria-label, "étoiles")]',
            '//div[contains(@aria-label, "stars")]',
        ])
        if el is None:
            return ""
        aria = el.get_attribute("aria-label") or ""
        m = re.search(r"[\d]+[.,]?[\d]*", aria)
        return m.group(0).replace(",", ".") if m else el.text.strip()

    def _extract_reviews_count(self):
        el = self._first_match([
            '//span[contains(@aria-label, "avis")]',
            '//span[contains(@aria-label, "reviews")]',
            '//button[contains(@aria-label, "avis")]',
        ])
        if el is None:
            return ""
        aria = el.get_attribute("aria-label") or el.text
        m = re.search(r"[\d\s]+", aria)
        return m.group(0).replace(" ", "").strip() if m else ""

    def _extract_status(self):
        el = self._first_match([
            '//span[contains(text(), "Ouvert")]',
            '//span[contains(text(), "Fermé")]',
            '//span[contains(text(), "Open")]',
            '//span[contains(text(), "Closed")]',
        ])
        return el.text.strip() if el is not None else ""

    # ----------------------------------------------------
    def _extract_place(self, url, activity_type, region, country, query):
        try:
            self.driver.get(url)
        except TimeoutException:
            pass
        try:
            WebDriverWait(self.driver, self.profile["page_wait"]).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
        except TimeoutException:
            return None

        name = ""
        try:
            name = self.driver.find_element(By.TAG_NAME, "h1").text.strip()
        except NoSuchElementException:
            pass
        if not name:
            return None

        phone = self._extract_phone()
        address = self._extract_address()
        website_url = self._extract_website()
        category = self._extract_category(activity_type)
        rating = self._extract_rating()
        reviews_count = self._extract_reviews_count()
        status = self._extract_status()

        return {
            "name": name,
            "phone": phone,
            "address": address,
            "category": category,
            "country": country,
            "wilaya": region,
            "has_website": bool(website_url),
            "website_url": website_url,
            "rating": rating,
            "reviews_count": reviews_count,
            "status": status,
            "maps_url": url,
            "search_query": query,
        }
