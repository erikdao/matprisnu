# matprisnu

Source code for [matprisnu](https://matprisnu.se) -- The website that recommends groceries with best prices in supermarkets across Sweden.

---

MatPrisNu is a set of services and jobs that are responsible for collecting groceries data from multiple supermarkets across Sweden, analyzes, compares and recommends items with best prices


## Development Logs

**April 29, 2023**
- Restart the development of the project. Right now the main task is to ingest the scrapped data (in JSON files) into PostgreSQL for more in-depth analysis.

**April 20, 2023**
- Stores and categories data are ingested from JSON to PostgreSQL. Next step is to make sense of the products data. Initial analysis so that, even within Coop, each product item might have slightly different schema, making it more complicated to unify products.

**April 19, 2023**
- Started development of the `data-ingestion` package. It loads scrapped data (e.g., from JSON files or MongoDB database), transforms the schemas and save the results to PostgreSQL database for further analytics.