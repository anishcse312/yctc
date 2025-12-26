ALTER TABLE admins
ADD COLUMN IF NOT EXISTS branches JSONB DEFAULT '[]';

UPDATE admins
SET branches = CASE
    WHEN branches IS NOT NULL THEN branches
    WHEN branch IS NULL OR branch = '' THEN '[]'::jsonb
    ELSE jsonb_build_array(branch)
END;
