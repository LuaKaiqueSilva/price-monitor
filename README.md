README.md

# 📈 Price Monitor

A Python application for monitoring product prices from Brazilian e-commerce stores.

---

## Demo

<p align="center">
  <img src="assets/gifs/Demo.gif" alt="Price Monitor Demo" width="900">
</p>

## Overview

Price Monitor is a desktop application built with Python that allows users to monitor product prices over time.

The application automatically collects product information from supported online stores, stores historical prices in a local SQLite database, and provides an interactive dashboard to visualize price trends and monitor changes.

The project was designed following a layered architecture with repositories, services, and scraper abstractions, making it easy to extend with support for new stores.

---

## ✨ Features

- Monitor products from supported online stores
- Automatic price updates
- Historical price tracking
- Interactive price charts
- Search products by name
- Sort products by price, name, or creation date
- Dashboard with summary metrics
- Configurable automatic refresh
- SQLite database for local persistence
- Extensible scraper architecture

## 🛠 Tech Stack

| Category | Technologies |
|----------|--------------|
| Language | Python 3.12 |
| Dashboard | Streamlit |
| Database | SQLite |
| Visualization | Plotly |
| Data Analysis | Pandas |
| Web Scraping | Requests, BeautifulSoup4 |
| Code Quality | Black, Ruff |

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/SEU-USUARIO/price-monitor.git
cd price-monitor
```
Create a virtual environment:
```bash
python -m venv .venv
```
Activate it:

Linux/macOS:
```bash
source .venv/bin/activate
```
Windows:
```bash
.venv\Scripts\activate
```
Install the dependencies:
```bash
pip install -r requirements.txt
```
## 🚀 Usage

Launch the dashboard:

```bash
streamlit run src/price_monitor/dashboard/app.py
```
Then open your browser at:

http://localhost:8501

Paste a supported product URL, click Add Product, and start monitoring prices.

## 📁 Project Structure

```text
src/price_monitor
├── dashboard/          # Streamlit interface
├── database/           # SQLite connection and repositories
├── models/             # Domain models
├── scrapers/           # Store scrapers
├── services/           # Business logic
└── exceptions.py       # Custom exceptions
```


---

## 🏗 Architecture

```md
## 🏗 Architecture

The project follows a layered architecture:

- **Dashboard** – User interface built with Streamlit.
- **Service Layer** – Coordinates business logic.
- **Repositories** – Handle persistence in SQLite.
- **Scrapers** – Extract product information from supported stores.
- **Models** – Domain entities shared across the application.

This architecture makes the project easy to extend with new e-commerce stores and additional dashboard features.
```

---

## 🗺 Roadmap

```md
## 🗺 Roadmap

### Version 1.1

- [ ] Playwright support
- [ ] Additional store scrapers
- [ ] Export price history to CSV
- [ ] Price alerts

### Version 2.0

- [ ] Multi-store comparison
- [ ] REST API
- [ ] Docker support
- [ ] Email notifications
- [ ] User accounts
```

---

## 📄 License

```md
## 📄 License

This project is licensed under the MIT License.
See the LICENSE file for details.
```

---
