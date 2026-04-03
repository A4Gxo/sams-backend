--
-- PostgreSQL database dump
--

\restrict cNaWEUxTXTmDsOhFsbeFdNZG8Bwl8g1f0usWbideLVL4KXET62OzFuSSoX6hmYb

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2026-04-03 11:42:44

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5084 (class 0 OID 24661)
-- Dependencies: 229
-- Data for Name: attendance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendance (attendance_id, session_id, student_id, present, marked_by, marked_at) FROM stdin;
1	901	501	t	\N	2026-03-26 11:25:47.957404
2	902	501	t	\N	2026-03-26 11:25:47.957404
3	903	501	t	\N	2026-03-26 11:25:47.957404
9	905	502	t	\N	2026-03-26 11:25:47.957404
14	7	501	t	\N	2026-03-26 23:10:00.701916
15	8	501	t	\N	2026-03-26 23:27:12.188338
16	9	501	t	\N	2026-03-26 23:44:15.342644
5	901	503	t	\N	2026-03-26 11:25:47.957404
17	901	505	t	\N	2026-03-27 08:53:59.729973
18	10	501	t	\N	2026-03-27 19:08:51.037235
19	11	501	t	\N	2026-03-27 19:11:21.683583
20	14	501	t	\N	2026-03-28 11:50:10.723656
23	17	501	t	\N	2026-03-28 12:44:06.549238
24	18	501	f	\N	2026-03-28 12:44:44.339379
25	19	501	t	\N	2026-03-28 12:44:45.361532
26	21	501	t	\N	2026-03-28 12:55:29.444494
27	22	501	t	\N	2026-03-28 13:17:54.905678
28	23	501	t	\N	2026-03-28 14:45:53.197901
29	24	501	t	\N	2026-03-28 14:57:43.869015
30	25	501	t	\N	2026-03-28 15:05:55.585838
31	26	501	t	\N	2026-03-28 15:06:24.65586
32	27	501	t	\N	2026-03-28 15:07:34.946159
6	902	503	t	\N	2026-03-26 11:25:47.957404
7	903	503	t	\N	2026-03-26 11:25:47.957404
8	904	503	t	\N	2026-03-26 11:25:47.957404
33	906	503	t	\N	2026-03-28 16:03:34.554978
21	14	503	t	\N	2026-03-28 11:51:24.188742
34	8	503	t	\N	2026-03-28 20:49:13.283401
35	10	503	t	\N	2026-03-28 20:49:17.714569
36	20	503	t	\N	2026-03-28 20:49:20.687472
22	14	505	t	\N	2026-03-28 11:51:26.139366
39	31	502	t	\N	2026-03-31 14:36:54.303172
41	30	503	t	\N	2026-03-31 14:40:37.398936
42	30	505	t	\N	2026-03-31 14:40:38.351258
40	30	501	t	\N	2026-03-31 14:40:35.550029
43	33	501	t	\N	2026-03-31 16:36:52.399272
4	904	501	t	\N	2026-03-26 11:25:47.957404
76	906	501	t	\N	2026-03-31 17:14:18.674413
77	66	501	t	\N	2026-04-01 09:09:24.019073
78	903	505	t	\N	2026-04-01 17:46:55.213243
\.


--
-- TOC entry 5088 (class 0 OID 24707)
-- Dependencies: 233
-- Data for Name: attendance_audit; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendance_audit (audit_id, attendance_id, action, changed_by, changed_at, details) FROM stdin;
\.


--
-- TOC entry 5082 (class 0 OID 24641)
-- Dependencies: 227
-- Data for Name: class_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.class_sessions (session_id, course_id, session_date, created_by, created_at, location_lat, location_lng, otp_code, is_active) FROM stdin;
901	10	2026-03-20	\N	2026-03-26 11:25:30.370492	20.2961	85.8245	X	f
902	10	2026-03-21	\N	2026-03-26 11:25:30.370492	20.2961	85.8245	X	f
903	10	2026-03-22	\N	2026-03-26 11:25:30.370492	20.2961	85.8245	X	f
904	10	2026-03-23	\N	2026-03-26 11:25:30.370492	20.2961	85.8245	X	f
905	20	2026-03-24	\N	2026-03-26 11:25:30.370492	20.2961	85.8245	X	f
906	10	2026-03-26	\N	2026-03-26 11:25:30.370492	20.2961	85.8245	LIVE99	f
1	10	2026-03-26	\N	2026-03-26 12:58:55.027965	20.4771	85.8265	319654	f
2	10	2026-03-26	\N	2026-03-26 16:42:55.527788	20.1644	85.6981	399319	f
3	10	2026-03-26	\N	2026-03-26 19:57:19.362165	20.3173	85.9356	296730	f
4	10	2026-03-26	\N	2026-03-26 19:57:37.488126	20.3173	85.9356	358611	f
5	10	2026-03-26	\N	2026-03-26 20:29:05.192705	20.3173	85.9356	515445	f
6	10	2026-03-26	\N	2026-03-26 20:49:09.691259	20.271478	85.770563	177799	f
7	10	2026-03-26	\N	2026-03-26 22:29:33.140366	20.271478	85.770563	171934	f
8	40	2026-03-26	\N	2026-03-26 23:26:17.663516	20.3173	85.9356	492875	f
9	10	2026-03-26	\N	2026-03-26 23:42:57.679871	20.2588	85.7884	670769	f
10	40	2026-03-27	\N	2026-03-27 19:08:27.883614	20.2588	85.7884	213058	f
11	40	2026-03-27	\N	2026-03-27 19:10:56.226124	20.2588	85.7884	340985	f
12	40	2026-03-27	\N	2026-03-27 19:12:48.695181	20.2588	85.7884	949692	f
14	10	2026-03-28	\N	2026-03-28 11:42:16.842035	20.2588	85.7884	492496	f
15	10	2026-03-28	\N	2026-03-28 11:51:10.675695	20.2588	85.7884	445998	f
17	10	2026-03-28	\N	2026-03-28 12:44:06.498171	0.0	0.0	MANUAL	f
18	10	2026-03-28	\N	2026-03-28 12:44:44.317136	0.0	0.0	MANUAL	f
19	10	2026-03-28	\N	2026-03-28 12:44:45.34346	0.0	0.0	MANUAL	f
13	40	2026-03-27	\N	2026-03-27 19:18:34.066722	20.271478	85.770563	123776	f
20	40	2026-03-28	\N	2026-03-28 12:53:14.817471	20.2588	85.7884	369621	f
22	10	2026-03-28	\N	2026-03-28 13:17:54.867663	0.0	0.0	MANUAL	f
23	10	2026-03-28	\N	2026-03-28 14:45:53.145179	0.0	0.0	MANUAL	f
24	10	2026-03-28	\N	2026-03-28 14:57:43.82688	0.0	0.0	MANUAL	f
25	10	2026-03-28	\N	2026-03-28 15:05:55.57127	0.0	0.0	MANUAL	f
26	10	2026-03-28	\N	2026-03-28 15:06:24.64696	0.0	0.0	MANUAL	f
21	40	2026-03-28	\N	2026-03-28 12:53:33.012984	20.2588	85.7884	474726	f
27	40	2026-03-28	\N	2026-03-28 15:07:17.850001	20.2588	85.7884	282117	f
16	10	2026-03-28	\N	2026-03-28 11:52:04.633842	20.2588	85.7884	834512	f
28	10	2026-03-28	\N	2026-03-28 21:36:17.86817	20.2588	85.7884	641335	f
29	10	2026-03-28	\N	2026-03-28 21:36:35.763963	20.2588	85.7884	530347	f
30	10	2026-03-31	\N	2026-03-31 14:29:03.413221	20.276941	85.775574	238833	f
32	10	2026-03-31	\N	2026-03-31 16:34:30.442471	20.262	85.7564	258187	f
66	30	2026-04-01	\N	2026-04-01 09:08:45.331302	20.2588	85.7884	876513	f
31	20	2026-03-31	\N	2026-03-31 14:36:01.469666	20.276607917808217	85.7758042477169	888790	f
33	10	2026-03-31	\N	2026-03-31 16:36:42.140141	20.262	85.7564	119766	f
\.


--
-- TOC entry 5080 (class 0 OID 24627)
-- Dependencies: 225
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.courses (course_id, course_code, course_name, faculty_id, department_id) FROM stdin;
10	CS101	Machine Learning	101	1
30	EC301	Microprocessors	103	3
40	CS102	Data Structures	101	1
50	IT203	Web Development	102	2
20	IT202	Database Systems	2	2
\.


--
-- TOC entry 5092 (class 0 OID 24826)
-- Dependencies: 238
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.departments (department_id, department_name) FROM stdin;
1	Computer Science
2	Information Technology
3	Electronics
4	Mechanical
\.


--
-- TOC entry 5094 (class 0 OID 24857)
-- Dependencies: 240
-- Data for Name: enrollments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.enrollments (enrollment_id, student_id, course_id, enrollment_date) FROM stdin;
1	501	10	2026-01-01
2	501	40	2026-01-01
3	502	20	2026-01-01
4	502	50	2026-01-01
5	503	10	2026-01-01
6	503	40	2026-01-01
7	504	30	2026-01-01
8	505	10	2026-01-01
9	501	20	2026-03-31
10	501	30	2026-04-01
\.


--
-- TOC entry 5078 (class 0 OID 24613)
-- Dependencies: 223
-- Data for Name: faculty; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.faculty (faculty_id, user_id, first_name, last_name, department_id) FROM stdin;
101	2	Alan	Turing	1
102	3	Grace	Hopper	2
103	4	Nikola	Tesla	3
1	11	External	Guest	1
2	12	Debi 	Mishra	2
\.


--
-- TOC entry 5086 (class 0 OID 24686)
-- Dependencies: 231
-- Data for Name: monthly_attendance_summary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.monthly_attendance_summary (summary_id, student_id, course_id, year, month, total_classes, present_count, percentage, eligible, last_updated) FROM stdin;
\.


--
-- TOC entry 5090 (class 0 OID 24804)
-- Dependencies: 236
-- Data for Name: semester_attendance_summary; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.semester_attendance_summary (semester_summary_id, student_id, course_id, semester_name, year, total_classes, total_present, percentage, eligible, last_updated) FROM stdin;
\.


--
-- TOC entry 5076 (class 0 OID 24591)
-- Dependencies: 221
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students (student_id, user_id, roll_no, first_name, last_name, year_of_study, department_id) FROM stdin;
502	6	IT-2026-05	Sanket	Kumar	2	2
503	7	CS-2026-02	Amit	Sharma	3	1
505	9	ME-2026-12	Rahul	Verma	4	4
501	5	CS-2026-01	Gyanaranjan	Moharana	3	1
1	10	EXT-10	External	Guest	1	1
504	8	EC-2026-09	Priya	Dash	1	3
2	13	EXT-13	External	Guest	\N	1
\.


--
-- TOC entry 5074 (class 0 OID 24578)
-- Dependencies: 219
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, username, password_hash, role, created_at, is_approved, institution) FROM stdin;
1	admin@sams.com	$2a$06$864OL6IWjNs/PC40tUXnLO.AMdP0f.eU4/AmTH4zGfbdS6zzFr6Cm	admin	2026-03-26 11:24:04.68726	t	\N
2	alan.turing@sams.com	$2a$06$OiTZ86u.pPBQTl6RE/UUI.KCdbqSm8kfxU6bRvVQydoeGmID8rzvG	faculty	2026-03-26 11:24:04.68726	t	\N
3	grace.hopper@sams.com	$2a$06$hIpmYKvBnfUpXtFfFrXwge0ONh2Gg3CU7L/hGuWHZDO6t8UyOufg6	faculty	2026-03-26 11:24:04.68726	t	\N
4	nikola.tesla@sams.com	$2a$06$.ipqaOWOC48VZJph1ljaxOTfCMvwvBmaSRuofVK7SYrGyy5c8oI1y	faculty	2026-03-26 11:24:04.68726	t	\N
5	gyana@sams.com	$2a$06$IGRdHYc5NaWPEpbiYGYftOi2CGeKL3ZK8UwDS52hCSUfzSGhyNSkO	student	2026-03-26 11:24:04.68726	t	\N
6	sanket@sams.com	$2a$06$unhcyDv9xoqySLdssx5pJeF5fV8kvtKfJLRDpT7O.vAGwoHaPQwEW	student	2026-03-26 11:24:04.68726	t	\N
7	amit@sams.com	$2a$06$92zxKis8BX1ioWLBIyC.lOAdRQ64B0W7AQdeBaJK.X1ZyJhGMZEXu	student	2026-03-26 11:24:04.68726	t	\N
8	priya@sams.com	$2a$06$l4KDCd5NMB0QlKh59XHo2u6SJk/axamZSOFi038tmz5FU1uv/5zPi	student	2026-03-26 11:24:04.68726	t	\N
9	rahul@sams.com	$2a$06$6.RSLAoGghGmKUDEQ0.lIOHveAJKPuU2wE9z8F9GC4u.7NYn.YjdO	student	2026-03-26 11:24:04.68726	t	\N
10	guest.user@gmail.com	$2a$06$s9TknOhIPFjTBh6ceIR.reo4S2wICgl9yHXIqIGvtC021TspHky.u	external_student	2026-03-26 11:24:04.68726	t	\N
11	speaker.mike@gmail.com	$2a$06$BF1MFcW7ucdHNoQJGKgupOD1oQEAkURvHMGjnHWO3nv5Dtr1NuC9m	external_faculty	2026-03-26 11:24:04.68726	t	\N
12	dpmishra@sams.com	$2a$06$WODq7X6sJ57v4dmI2pWASuFo.BKFtt6L0I679c3/eYD4GJYr8f5xa	faculty	2026-03-31 22:15:53.602985	t	\N
13	abhi@sams.com	$2a$06$yAK28VzbmooRJkZvK7jMReu0sSLFuhsrYhAELOeG7CnO8l2OxyQ0O	external_student	2026-04-01 21:39:19.281756	t	MIT
\.


--
-- TOC entry 5114 (class 0 OID 0)
-- Dependencies: 228
-- Name: attendance_attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendance_attendance_id_seq', 78, true);


--
-- TOC entry 5115 (class 0 OID 0)
-- Dependencies: 232
-- Name: attendance_audit_audit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendance_audit_audit_id_seq', 1, false);


--
-- TOC entry 5116 (class 0 OID 0)
-- Dependencies: 226
-- Name: class_sessions_session_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.class_sessions_session_id_seq', 66, true);


--
-- TOC entry 5117 (class 0 OID 0)
-- Dependencies: 224
-- Name: courses_course_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.courses_course_id_seq', 1, false);


--
-- TOC entry 5118 (class 0 OID 0)
-- Dependencies: 237
-- Name: departments_department_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.departments_department_id_seq', 1, false);


--
-- TOC entry 5119 (class 0 OID 0)
-- Dependencies: 239
-- Name: enrollments_enrollment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.enrollments_enrollment_id_seq', 10, true);


--
-- TOC entry 5120 (class 0 OID 0)
-- Dependencies: 222
-- Name: faculty_faculty_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.faculty_faculty_id_seq', 2, true);


--
-- TOC entry 5121 (class 0 OID 0)
-- Dependencies: 230
-- Name: monthly_attendance_summary_summary_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.monthly_attendance_summary_summary_id_seq', 1, false);


--
-- TOC entry 5122 (class 0 OID 0)
-- Dependencies: 235
-- Name: semester_attendance_summary_semester_summary_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.semester_attendance_summary_semester_summary_id_seq', 1, false);


--
-- TOC entry 5123 (class 0 OID 0)
-- Dependencies: 220
-- Name: students_student_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_student_id_seq', 2, true);


--
-- TOC entry 5124 (class 0 OID 0)
-- Dependencies: 218
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 13, true);


-- Completed on 2026-04-03 11:42:45

--
-- PostgreSQL database dump complete
--

\unrestrict cNaWEUxTXTmDsOhFsbeFdNZG8Bwl8g1f0usWbideLVL4KXET62OzFuSSoX6hmYb

