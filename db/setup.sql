-- Initialize a new local database. Run once.
BEGIN;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    pswd_hash VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL DEFAULT 'basic',
    permission VARCHAR(255) NOT NULL DEFAULT 'ok',
    wordle_streak INTEGER NOT NULL DEFAULT 0,
    spelling_bee_streak INTEGER NOT NULL DEFAULT 0,
    last_login_wordle DATE,
    last_login_spelling_bee DATE
);

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    type VARCHAR(255) NOT NULL CHECK (type IN ('wordle', 'spelling_bee')),
    day_to_play INTEGER NOT NULL CHECK (day_to_play BETWEEN 1 AND 7),
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (type, day_to_play)
);

CREATE TABLE game_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    status VARCHAR(255) NOT NULL DEFAULT 'not_started'
        CHECK (status IN ('in_progress', 'not_started', 'finished')),
    won BOOLEAN NOT NULL DEFAULT FALSE,
    state TEXT,
    UNIQUE (user_id, game_id)
);

-- Flask uses ISO weekday numbers. Puzzle content lives in the Python modules.
INSERT INTO games (type, day_to_play)
SELECT game_type, day
FROM (VALUES ('wordle'), ('spelling_bee')) AS game_types(game_type)
CROSS JOIN generate_series(1, 7) AS weekdays(day);

COMMIT;
