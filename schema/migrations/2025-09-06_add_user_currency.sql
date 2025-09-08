-- Add currency column to users table (idempotent)
-- SQLite syntax compatible; Postgres uses IF NOT EXISTS via DO block if needed

-- SQLite pragma to inspect columns (ignored by Postgres)
-- This migration runner executes SQL files; idempotency depends on runner semantics

ALTER TABLE users ADD COLUMN IF NOT EXISTS currency VARCHAR(3) NOT NULL DEFAULT 'USD';


