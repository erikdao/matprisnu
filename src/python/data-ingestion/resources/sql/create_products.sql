--
-- Create Product tables
--
CREATE TABLE IF NOT EXISTS coop_products (
    "pkeys" SERIAL PRIMARY KEY,
    "scrapped_date" date,
	"updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    "id" VARCHAR(255) NOT NULL,
    "type" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "ean" VARCHAR(255) NOT NULL,
    "imageUrl" TEXT,
    "description" TEXT,
    
);