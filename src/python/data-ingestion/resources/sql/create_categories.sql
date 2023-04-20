--
-- Create Category tables
---
CREATE TABLE IF NOT EXISTS coop_categories (
    "pkey" SERIAL PRIMARY KEY,
    "scrapped_date" DATE,
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "id" INTEGER NOT NULL,
    "level" INTEGER,
    "name" VARCHAR(255),
    "parent" INTEGER,
    "escapedName" VARCHAR(255),
    "hasChildren" BOOLEAN
);
