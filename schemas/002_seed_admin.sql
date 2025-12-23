INSERT INTO admins (employee_id, first_name, last_name, email, branch)
VALUES ('123456','Anish','Banerjee','anishbanerjee2003@gmail.com','N24')
ON CONFLICT (employee_id) DO NOTHING;
