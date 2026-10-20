-- BioSIM Lab - esquema de la tabla de experimentos guardados.
-- Ejecutar UNA vez en Supabase: SQL Editor -> New query -> pegar -> Run.
CREATE TABLE IF NOT EXISTS saved_experiments (
    experiment_id    VARCHAR(64) PRIMARY KEY,
    name             VARCHAR(256) NOT NULL,
    created_at       TIMESTAMPTZ DEFAULT now(),
    initial_sequence TEXT NOT NULL DEFAULT '',
    working_copy     TEXT,
    mutation_applied JSONB DEFAULT '{}'::jsonb,
    altered_sequence TEXT,
    detection_result JSONB DEFAULT '{}'::jsonb,
    repair_applied   JSONB DEFAULT '{}'::jsonb,
    final_sequence   TEXT,
    diff_result      JSONB DEFAULT '{}'::jsonb,
    status           VARCHAR(64) DEFAULT 'completed',
    notes            TEXT,
    code_version     VARCHAR(64) DEFAULT 'v1.1-phase1-closed'
);
CREATE INDEX IF NOT EXISTS ix_saved_experiments_created_at ON saved_experiments (created_at DESC);
