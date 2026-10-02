# Google Maps Lead Scraper Find Businesses Without a Website

A desktop application built with **PyQt5** that helps you discover businesses on Google Maps that **do not have a website**. It is designed for web agencies, freelancers, and digital marketers looking for potential clients who could benefit from a professional website.

## Requirements

Before getting started, make sure you have:

* Python 3.9 or later
* Google Chrome installed (the application uses Selenium to automate Chrome)

## Installation

```bash
cd gmaps_scraper_app

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

The application uses **webdriver-manager**, which automatically downloads the correct version of ChromeDriver the first time you run it. No manual installation is required.

## Running the Application

Start the program with:

```bash
python main.py
```

## How to Use

1. Select the city or region you want to search.
2. Enter a business category, such as:

   * Hotel
   * Restaurant
   * Pharmacy
   * Real Estate Agency
   * Gym
   * Dental Clinic
   * Car Dealer
3. Set the maximum number of businesses to scan (40 by default).
4. Click **Search**.
5. Results will appear gradually as they are found.
6. Every record is automatically saved to a local SQLite database (`results.db`), so your data is preserved even if you close the application.
7. Enable or disable **Show Only Businesses Without a Website** to filter the results.
8. Export the results as a CSV file for Excel, Google Sheets, or your CRM.

## Features

* Search businesses by location and category
* Detect whether a business has a website
* Save results automatically to SQLite
* Remove duplicate businesses automatically
* Filter businesses with or without websites
* Export clean CSV files
* Real-time progress log
* Optional headless mode for background execution

## Tips

* For your first run, disable **Headless Mode** so you can watch Chrome work and verify everything is running correctly.
* Google may temporarily slow down or block requests if too many searches are performed in a short period. The scraper already includes random delays to reduce this risk, but avoid running very large batches continuously.
* Duplicate businesses are automatically detected using their name and address.
* Always use this tool responsibly and comply with Google's Terms of Service and the applicable regulations in your country regarding commercial outreach.

## Future Improvements

Planned features include:

* Excel (.xlsx) export with formatting
* Direct integration with WhatsApp Business
* Detection of Facebook, Instagram, and other social media profiles when no website is available
* One-click packaging as a standalone Windows executable (.exe)
* Queue support for searching multiple cities and business categories automatically
* Additional export options for CRM platforms
