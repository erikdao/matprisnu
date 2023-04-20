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

CREATE TABLE IF NOT EXISTS ica_categories (
    "pkey" SERIAL PRIMARY KEY,
    "scrapped_date" DATE,
    "updated_at" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "id" VARCHAR(255) NOT NULL UNIQUE,
    "name" VARCHAR(255),
    "retailerId" VARCHAR(255),
    "children" VARCHAR(255)[],
    "fullURLPath" VARCHAR(255),
    "storeId" VARCHAR(255)
);