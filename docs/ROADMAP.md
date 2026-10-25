# Roadmap

This roadmap separates improvements to the current local app from larger future features. Store page changes can affect scraper reliability at any time.

## Next

- Add automated tests for price parsing, store selection, persistence, and service workflows.
- Add structured application logging for scraper and database errors.
- Improve scraper resilience when stores change their page markup or block requests.
- Revisit Pichau support; a product page returned HTTP 403 to the current Requests-based fetcher during validation.
- Add a small sample database or offline demo mode so the dashboard can be previewed without live store pages.

## Later

- Export a product's price history to CSV.
- Add configurable price alerts.
- Add support for more stores and compare the same product across stores.
- Consider a REST API or scheduled background worker if the app moves beyond local use.

Features are prioritized based on user value and project scope; this list is not a release commitment.
