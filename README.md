# matprisnu

Source code for [matprisnu](https://matprisnu.se) -- The website that recommends groceries with best prices in supermarkets across Sweden.

---

MatPrisNu is a set of services and jobs that are responsible for collecting groceries data from multiple supermarkets across Sweden, analyzes, compares and recommends items with best prices


## Development Logs

**April 19, 2023**
- Started development of the `data-ingestion` package. It loads scrapped data (e.g., from JSON files or MongoDB database), transforms the schemas and save the results to PostgreSQL database for further analytics.