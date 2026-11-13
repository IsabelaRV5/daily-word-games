-- Run after setup.sql and after registering word-games-demo in the app.
BEGIN;
DO $$
DECLARE
    demo_user integer;
    previous_day integer := ((EXTRACT(ISODOW FROM CURRENT_DATE)::integer + 5) % 7) + 1;
    answer text;
BEGIN
    SELECT id INTO STRICT demo_user FROM users WHERE username = 'word-games-demo';
    answer := (ARRAY['KITTY', 'LOVED', 'MUSIC', 'ORATE', 'INDEX', 'VALUE', 'GNOME'])[previous_day];

    INSERT INTO game_sessions (user_id, game_id, status, won, state)
    SELECT demo_user, id, 'finished', true,
        json_build_object(
            'status', 'finished',
            'guesses', json_build_object(answer, ARRAY['correct','correct','correct','correct','correct']),
            'won', true, 'word', answer, 'is_over', true, 'attempts_left', 5
        )::text
    FROM games WHERE type = 'wordle' AND day_to_play = previous_day
    ON CONFLICT (user_id, game_id) DO NOTHING;
END;
$$;
COMMIT;
