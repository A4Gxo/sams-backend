-- Clean the database first to prevent duplicate errors
TRUNCATE TABLE public.users CASCADE;
TRUNCATE TABLE public.departments CASCADE;

-- 1. Insert Departments
INSERT INTO public.departments (department_id, department_name) VALUES
(1, 'Computer Science'),
(2, 'Information Technology'),
(3, 'Electronics'),
(4, 'Mechanical');

-- 2. Insert Users
INSERT INTO public.users (user_id, username, password_hash, role, created_at, is_approved, institution) VALUES
(1, 'admin@sams.com', '$2a$06$864OL6IWjNs/PC40tUXnLO.AMdP0f.eU4/AmTH4zGfbdS6zzFr6Cm', 'admin', '2026-03-26 11:24:04.68726', true, NULL),
(2, 'alan.turing@sams.com', '$2a$06$OiTZ86u.pPBQTl6RE/UUI.KCdbqSm8kfxU6bRvVQydoeGmID8rzvG', 'faculty', '2026-03-26 11:24:04.68726', true, NULL),
(3, 'grace.hopper@sams.com', '$2a$06$hIpmYKvBnfUpXtFfFrXwge0ONh2Gg3CU7L/hGuWHZDO6t8UyOufg6', 'faculty', '2026-03-26 11:24:04.68726', true, NULL),
(4, 'nikola.tesla@sams.com', '$2a$06$.ipqaOWOC48VZJph1ljaxOTfCMvwvBmaSRuofVK7SYrGyy5c8oI1y', 'faculty', '2026-03-26 11:24:04.68726', true, NULL),
(5, 'gyana@sams.com', '$2a$06$IGRdHYc5NaWPEpbiYGYftOi2CGeKL3ZK8UwDS52hCSUfzSGhyNSkO', 'student', '2026-03-26 11:24:04.68726', true, NULL),
(6, 'sanket@sams.com', '$2a$06$unhcyDv9xoqySLdssx5pJeF5fV8kvtKfJLRDpT7O.vAGwoHaPQwEW', 'student', '2026-03-26 11:24:04.68726', true, NULL),
(7, 'amit@sams.com', '$2a$06$92zxKis8BX1ioWLBIyC.lOAdRQ64B0W7AQdeBaJK.X1ZyJhGMZEXu', 'student', '2026-03-26 11:24:04.68726', true, NULL),
(8, 'priya@sams.com', '$2a$06$l4KDCd5NMB0QlKh59XHo2u6SJk/axamZSOFi038tmz5FU1uv/5zPi', 'student', '2026-03-26 11:24:04.68726', true, NULL),
(9, 'rahul@sams.com', '$2a$06$6.RSLAoGghGmKUDEQ0.lIOHveAJKPuU2wE9z8F9GC4u.7NYn.YjdO', 'student', '2026-03-26 11:24:04.68726', true, NULL),
(10, 'guest.user@gmail.com', '$2a$06$s9TknOhIPFjTBh6ceIR.reo4S2wICgl9yHXIqIGvtC021TspHky.u', 'external_student', '2026-03-26 11:24:04.68726', true, NULL),
(11, 'speaker.mike@gmail.com', '$2a$06$BF1MFcW7ucdHNoQJGKgupOD1oQEAkURvHMGjnHWO3nv5Dtr1NuC9m', 'external_faculty', '2026-03-26 11:24:04.68726', true, NULL),
(12, 'dpmishra@sams.com', '$2a$06$WODq7X6sJ57v4dmI2pWASuFo.BKFtt6L0I679c3/eYD4GJYr8f5xa', 'faculty', '2026-03-31 22:15:53.602985', true, NULL),
(13, 'abhi@sams.com', '$2a$06$yAK28VzbmooRJkZvK7jMReu0sSLFuhsrYhAELOeG7CnO8l2OxyQ0O', 'external_student', '2026-04-01 21:39:19.281756', true, 'MIT');

-- 3. Insert Faculty
INSERT INTO public.faculty (faculty_id, user_id, first_name, last_name, department_id) VALUES
(101, 2, 'Alan', 'Turing', 1),
(102, 3, 'Grace', 'Hopper', 2),
(103, 4, 'Nikola', 'Tesla', 3),
(1, 11, 'External', 'Guest', 1),
(2, 12, 'Debi', 'Mishra', 2);

-- 4. Insert Students
INSERT INTO public.students (student_id, user_id, roll_no, first_name, last_name, year_of_study, department_id) VALUES
(502, 6, 'IT-2026-05', 'Sanket', 'Kumar', 2, 2),
(503, 7, 'CS-2026-02', 'Amit', 'Sharma', 3, 1),
(505, 9, 'ME-2026-12', 'Rahul', 'Verma', 4, 4),
(501, 5, 'CS-2026-01', 'Gyanaranjan', 'Moharana', 3, 1),
(1, 10, 'EXT-10', 'External', 'Guest', 1, 1),
(504, 8, 'EC-2026-09', 'Priya', 'Dash', 1, 3),
(2, 13, 'EXT-13', 'External', 'Guest', NULL, 1);

INSERT INTO public.courses (course_id, course_code, course_name, faculty_id, department_id) VALUES
(10, 'CS101', 'Machine Learning', 101, 1),
(30, 'EC301', 'Microprocessors', 103, 3),
(40, 'CS102', 'Data Structures', 101, 1),
(50, 'IT203', 'Web Development', 102, 2),
(20, 'IT202', 'Database Systems', 2, 2);

-- 7. Insert Enrollments (Putting students into the courses!)
INSERT INTO public.enrollments (enrollment_id, student_id, course_id, enrollment_date) VALUES
(1, 501, 10, '2026-01-01'),
(2, 501, 40, '2026-01-01'),
(3, 502, 20, '2026-01-01'),
(4, 502, 50, '2026-01-01'),
(5, 503, 10, '2026-01-01'),
(6, 503, 40, '2026-01-01'),
(7, 504, 30, '2026-01-01'),
(8, 505, 10, '2026-01-01'),
(9, 501, 20, '2026-03-31'),
(10, 501, 30, '2026-04-01');

-- 5. Fix Sequence Counters so new users don't cause ID crashes
SELECT pg_catalog.setval('public.users_user_id_seq', 14, true);
SELECT pg_catalog.setval('public.courses_course_id_seq', 60, true);
SELECT pg_catalog.setval('public.enrollments_enrollment_id_seq', 11, true);