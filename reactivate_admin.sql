-- Reactivate admin@nudj.sa account
-- Run this SQL directly in your PostgreSQL database

UPDATE users
SET
    is_active = true,
    failed_login_attempts = 0,
    locked_until = NULL
WHERE
    email = 'admin@nudj.sa';

-- Verify the update
SELECT
    id,
    email,
    name_en,
    role,
    is_active,
    failed_login_attempts,
    locked_until
FROM users
WHERE email = 'admin@nudj.sa';
