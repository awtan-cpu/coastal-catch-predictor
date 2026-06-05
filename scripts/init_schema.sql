-- Creating the primary catch logs table to record trips and bites
CREATE TABLE catch_logs (
    trip_id SERIAL PRIMARY KEY,
    location VARCHAR(100),
    target_species VARCHAR(50),
    start_time TIMESTAMP,
    bite_time TIMESTAMP,
    time_to_bite_minutes INTEGER,
    event_occurred BOOLEAN
);

-- Setting up the environmental conditions table for continuous weather variables
CREATE TABLE environmental_conditions (
    condition_id SERIAL PRIMARY KEY,
    reading_time TIMESTAMP UNIQUE,
    water_temperature_f NUMERIC(5, 2),
    barometric_pressure_mb NUMERIC(6, 2)
);

-- Establishing the tide predictions table to track water movement
CREATE TABLE tide_predictions (
    tide_id SERIAL PRIMARY KEY,
    prediction_time TIMESTAMP UNIQUE,
    water_level_ft NUMERIC(4, 2),
    tide_type VARCHAR(1)
);