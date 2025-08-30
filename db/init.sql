CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    creator TEXT NULL,
    time_created timestamp default current_timestamp,
    time_updated timestamp
);

-- Prevent Timestamp from being manually updated

CREATE OR REPLACE FUNCTION stop_change_on_timestamp()
RETURNS trigger AS
$$
BEGIN
  NEW.time_created := OLD.time_created;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_timestamp_changes
BEFORE UPDATE
ON notes
FOR EACH ROW
EXECUTE PROCEDURE stop_change_on_timestamp();
