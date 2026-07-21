# Product Requirements Document

**Project:** Price Monitor

**Version:** 0.1.0

**Status:** Draft

**Author:** Luã Kaique da Silva

**Last Updated:** 2026-07-20

---

# 1. Product Vision

Price Monitor is an open-source application designed to automate the monitoring of product prices across multiple online stores.

The system continuously collects price information, stores historical records, and presents meaningful insights through an intuitive dashboard, helping users make informed purchasing decisions.

The project is built with a strong focus on software engineering principles, emphasizing modularity, maintainability, scalability, and extensibility. Its architecture is designed to support new stores, additional data sources, and future features without requiring significant changes to the existing codebase.

Beyond solving a practical problem, Price Monitor also serves as a reference implementation of modern Python software development practices, demonstrating clean architecture, modular design, testing, documentation, and open-source collaboration.

---

# 2. Design Principles

The project is guided by the following engineering principles:

- Simplicity before complexity.
- Modular and maintainable architecture.
- Separation of concerns.
- Extensibility through well-defined interfaces.
- Readable and well-documented code.
- Incremental development through small, testable iterations.
- Open-source first.

---

# 3. Problem Statement

Monitoring product prices across multiple online stores is a repetitive, time-consuming, and inefficient process.

Individuals, technology enthusiasts, and small businesses often need to manually visit several websites to compare prices and identify the best purchasing opportunities. Likewise, small businesses and resellers regularly monitor competitors' prices to remain competitive in rapidly changing markets. This manual workflow is error-prone, difficult to maintain over long periods, and provides little visibility into historical price trends.

Although various commercial services and browser extensions offer partial solutions, they are frequently limited by subscription costs, restricted customization, lack of transparency, or support for only a small number of online stores. Conversely, many open-source alternatives focus solely on web scraping, without providing a scalable architecture, historical data analysis, or a user-friendly interface.

As a result, users lack an accessible, extensible, and open-source solution capable of continuously collecting, storing, and analyzing product price data in a reliable and organized manner.

### Value Proposition

Price Monitor provides an accessible, transparent, and extensible platform for automated price monitoring, combining reliable data collection, historical analysis, and modern software engineering practices in a single open-source application.

---

# 4. Proposed Solution

Price Monitor solves the problem by providing a modular platform capable of monitoring product prices from supported online stores.

Users simply register the URL of a product they wish to monitor. The system automatically identifies the corresponding scraper, retrieves the latest product information, stores historical price records, and presents the collected data through an interactive dashboard.

The architecture has been intentionally designed to separate business logic, infrastructure, and presentation, making the project easy to maintain and extend. New online stores can be supported by implementing additional scraper modules without requiring significant modifications to the existing codebase.

The first version (MVP) focuses on delivering a reliable and complete foundation while intentionally postponing advanced features to future releases.

---

# 5. Objectives

### Primary Objectives

The primary objectives of Price Monitor are:

- Automate the collection of product prices from supported online stores.
- Eliminate the need for repetitive manual price checking.
- Store historical price data in a structured and reliable database.
- Provide intuitive visualizations that help users understand price evolution over time.
- Deliver a clean and user-friendly dashboard.

### Secondary Objectives

In addition to solving the immediate problem of price monitoring, the project also aims to:

- Provide a modular architecture that simplifies the addition of new online stores.
- Serve as a reference project for modern Python software engineering practices.
- Encourage open-source collaboration.
- Maintain high standards of code quality, documentation, and testing.
- Support future expansion without requiring major architectural refactoring.

---

# 6. Project Scope

The first version of Price Monitor (MVP) is intentionally limited to a small but complete feature set that demonstrates the core functionality of the application and the quality of its software architecture.

The primary goal of the MVP is to provide a reliable, maintainable, and extensible foundation while delivering a fully functional product that solves the main problem of manual price monitoring.

Features that do not directly contribute to this goal are intentionally postponed to future releases.

### 6.1 In Scope (MVP)

The MVP will include the following features:

- Register products using direct product URLs.
- Support one or more online stores through modular scraper implementations.
- Automatically identify the appropriate scraper based on the provided URL.
- Retrieve the current product price on demand.
- Store product information and historical prices in a local SQLite database.
- Display monitored products in an interactive Streamlit dashboard.
- Display the latest recorded price for each product.
- Display historical price evolution through interactive charts.
- Record application logs for debugging purposes.
- Include basic automated tests for the application's core functionality.

### 6.2 Out of Scope

The following features are intentionally excluded from the MVP:

- Product search across multiple stores.
- Automatic product discovery.
- Scheduled background monitoring.
- Price alerts (Email, Telegram, Discord, etc.).
- User accounts and authentication.
- Cloud synchronization.
- REST API.
- Docker deployment.
- Machine learning or price prediction.
- Mobile application.
- Multi-user support.
- Data export (CSV, Excel, PDF).
- Browser extension.

### 6.3 Future Versions

Future releases may introduce additional capabilities, including:

- Product-based monitoring instead of URL-based monitoring.
- Support for additional online stores.
- Scheduled automatic price updates.
- Price notification system.
- Product comparison across multiple stores.
- Advanced analytics and statistics.
- Data export features.
- PostgreSQL support.
- REST API.
- Docker support.
- Plugin system for third-party scrapers.

### 6.4 MVP Completion Criteria

The MVP will be considered complete when users are able to:

- Register a product using its URL.
- Successfully retrieve the current product price.
- Store historical price information.
- Visualize price history through the dashboard.
- Update prices manually.
- Run the application following the project's documentation.

---

# 7. Functional Requirements

### FR-001 — Register Product

The system shall allow users to register a product by providing its direct URL.

### FR-002 — URL Validation

The system shall validate whether the provided URL belongs to a supported online store.

### FR-003 — Scraper Selection

The system shall automatically select the appropriate scraper implementation based on the product URL.

### FR-004 — Price Collection

The system shall retrieve the current product information and price from the target webpage.

### FR-005 — Data Persistence

The system shall store product information and historical price data in a SQLite database.

### FR-006 — Manual Update

The system shall allow users to manually update the price of any monitored product.

### FR-007 — Product Dashboard

The system shall display all monitored products in an interactive dashboard.

### FR-008 — Price History

The system shall display the historical price evolution of each monitored product through interactive charts.

### FR-009 — Logging

The system shall record scraping errors and relevant application events using a logging system.

### FR-010 — Modular Architecture

The system shall allow new scraper implementations to be added without modifying existing scraper modules.

---

# 8. Non-Functional Requirements

### NFR-001

The application shall be developed using Python 3.11 or newer.

### NFR-002

The application shall follow the PEP 8 style guide.

### NFR-003

The codebase shall use type hints where appropriate.

### NFR-004

The application shall run on Windows and Linux.

### NFR-005

The project shall include automated tests for its core functionality.

### NFR-006

The project shall include clear installation and usage documentation.

### NFR-007

The application shall be designed using a modular architecture with clear separation of responsibilities.

---

# 9. User Stories

### US-001

As a consumer, I want to monitor a product by its URL so that I can avoid checking prices manually every day.

### US-002

As a consumer, I want to view the historical price of a product so that I can identify the best time to buy.

### US-003

As a consumer, I want to update a product's price with a single click so that I can keep the information current.

### US-004

As a developer, I want to add support for new online stores without modifying the existing scraping logic.

### US-005

As a contributor, I want the project to be well documented so that I can understand and contribute easily.

---

# 10. Assumptions

The project assumes that supported online stores allow public access to product pages and that the required product information can be extracted reliably through web scraping.

It is also assumed that users have basic knowledge of running Python applications and can install the project following the provided documentation.

---

# 11. Risks

Potential risks include changes in website structures that may break scraper implementations, anti-bot protection mechanisms, and differences in HTML layouts between supported online stores.

The modular architecture mitigates these risks by isolating scraping logic into independent components, reducing the impact of future maintenance.