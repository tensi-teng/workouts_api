
-- Schema for FitLife
DROP TABLE IF EXISTS gestures;
DROP TABLE IF EXISTS checklist_items;
DROP TABLE IF EXISTS workouts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS public_workouts;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    reg_number VARCHAR(20) UNIQUE NOT NULL,
    Email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workouts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    description TEXT,
    equipment TEXT, 
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE checklist_items (
    id SERIAL PRIMARY KEY,
    task VARCHAR(255) NOT NULL,
    done BOOLEAN DEFAULT FALSE,
    workout_id INTEGER REFERENCES workouts(id) ON DELETE CASCADE
);

CREATE TABLE gestures (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    action VARCHAR(200),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

-- Public API table
CREATE TABLE public_workouts (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50),
    name VARCHAR(100),
    muscles TEXT[],
    equipment TEXT,
    instructions TEXT,
    level VARCHAR(20)
);
