# Roadmap

This roadmap separates improvements to the current local app from larger future features. Store page changes can affect scraper reliability at any time.

## Completed foundation

- Add offline tests for price parsing, store selection, persistence, service workflows, and the dashboard demo.
- Log scraper and product-update failures with useful context.
- Add an in-memory demo mode that previews charts without writing to SQLite.
- Retry temporary store failures and explain HTTP 403 access blocks.
- Export a product's price history to an Excel-friendly CSV file.
- Set a target price and highlight it in the dashboard when reached.

## Next

- Improve scraper resilience when stores change their page markup or block requests.
- Pichau pages are rendered in a visible Chromium window because direct HTTP and headless Chromium requests receive HTTP 403; the scraper reads the Pix price selector and metadata.

## Later

- Add support for more stores and compare the same product across stores.
- Consider a REST API or scheduled background worker if the app moves beyond local use.

Features are prioritized based on user value and project scope; this list is not a release commitment.
