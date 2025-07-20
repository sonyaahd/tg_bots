--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

-- Started on 2025-07-16 01:47:11

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
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- TOC entry 4921 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 33064)
-- Name: priemka; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.priemka (
    id integer NOT NULL,
    date_received timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    material_id integer,
    quantity integer
);


ALTER TABLE public.priemka OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 33063)
-- Name: priemka_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.priemka_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.priemka_id_seq OWNER TO postgres;

--
-- TOC entry 4922 (class 0 OID 0)
-- Dependencies: 219
-- Name: priemka_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.priemka_id_seq OWNED BY public.priemka.id;


--
-- TOC entry 218 (class 1259 OID 33057)
-- Name: sklad; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sklad (
    material_id integer NOT NULL,
    name character varying(255) NOT NULL,
    quantity integer
);


ALTER TABLE public.sklad OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 33056)
-- Name: sklad_material_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sklad_material_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sklad_material_id_seq OWNER TO postgres;

--
-- TOC entry 4923 (class 0 OID 0)
-- Dependencies: 217
-- Name: sklad_material_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sklad_material_id_seq OWNED BY public.sklad.material_id;


--
-- TOC entry 222 (class 1259 OID 33077)
-- Name: vidacha; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vidacha (
    id integer NOT NULL,
    date_issued timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    material_id integer,
    room integer,
    employee_name character varying(255) NOT NULL,
    quantity integer NOT NULL
);


ALTER TABLE public.vidacha OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 33076)
-- Name: vidacha_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vidacha_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vidacha_id_seq OWNER TO postgres;

--
-- TOC entry 4924 (class 0 OID 0)
-- Dependencies: 221
-- Name: vidacha_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vidacha_id_seq OWNED BY public.vidacha.id;


--
-- TOC entry 4753 (class 2604 OID 33067)
-- Name: priemka id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.priemka ALTER COLUMN id SET DEFAULT nextval('public.priemka_id_seq'::regclass);


--
-- TOC entry 4752 (class 2604 OID 33060)
-- Name: sklad material_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sklad ALTER COLUMN material_id SET DEFAULT nextval('public.sklad_material_id_seq'::regclass);


--
-- TOC entry 4755 (class 2604 OID 33080)
-- Name: vidacha id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vidacha ALTER COLUMN id SET DEFAULT nextval('public.vidacha_id_seq'::regclass);


--
-- TOC entry 4913 (class 0 OID 33064)
-- Dependencies: 220
-- Data for Name: priemka; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.priemka (id, date_received, material_id, quantity) FROM stdin;
2	2025-07-14 00:00:00	9	120000
4	2025-07-16 00:00:00	26	100
\.


--
-- TOC entry 4911 (class 0 OID 33057)
-- Dependencies: 218
-- Data for Name: sklad; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sklad (material_id, name, quantity) FROM stdin;
1	Кабель Exegate EX284915RUS	5000
4	Клавиатура ExeGate EX286177RUS	30000
5	Комплект кл+мышь Exegate EX286204RUS	10000
7	Батарея аккумуляторная WBR HR 1234WF2	6000
2	Модуль памяти HP 32Gb 728629-B21	4000
8	Батарея аккумуляторная WBR HR 1234WF2	5000
3	Модуль памяти HP 8GB 500662-B21	3935
9	Батарейка Robiton Standard LR03 1,5V	120000
11	Кабель ExeGate EX284893RUS	2000
12	Фотобарабан Xerox 108R01417 голубой	1000
13	Фотобарабан Xerox 108R01418 пурпурный	1000
14	Фотобарабан Xerox 108R01419 желтый	1000
16	Драм-картридж GalaPrint GP-113R00779	10000
17	Картридж TrendArt TA_CE343A пурпурный	4000
18	Картридж Trendart TrA_CF283X-CRG737	5000
19	Картридж Trendart TrA_CF283X-CRG737	7000
20	Тонер-картридж Булат DFRXVL7025050	19000
21	Комплект роликов АПД HP100 L2718A	1000
22	Термоузел Булат AMHPLJ1132010	6000
23	Фильтр ExeGate SP-6-5B p/n EX119395RUS	5000
24	Фильтр сетев ExeGate SP-6-3B EX119393RUS	5000
25	Фильтр сетевой ExeGate SP-6-1.8B	5000
26	Кабель Exegate EX284915RUS	100
15	Фотобарабан Xerox 108R01420 черный	970
\.


--
-- TOC entry 4915 (class 0 OID 33077)
-- Dependencies: 222
-- Data for Name: vidacha; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vidacha (id, date_issued, material_id, room, employee_name, quantity) FROM stdin;
2	2025-07-14 17:14:01.736354	3	601	Мария Сергеевна Банан	10
3	2025-07-14 17:22:10.67349	3	601	Антон Павлович Чехов	50
4	2025-07-14 17:50:36.514159	9	605	Ананасов Аркадий Аркадьевич	7
5	2025-07-14 17:51:25.974662	3	123	Можевельникова Марина Николаевна	5
6	2025-01-05 00:00:00	1	601	Иванов И.И.	15
7	2025-01-10 00:00:00	2	601	Иванов И.И.	10
8	2025-01-15 00:00:00	3	602	Петров П.П.	8
9	2025-01-20 00:00:00	7	603	Сидоров С.С.	12
10	2025-01-22 00:00:00	11	604	Михайлова А.А.	20
11	2025-02-01 00:00:00	1	601	Иванов И.И.	18
12	2025-02-04 00:00:00	2	605	Петров П.П.	7
13	2025-02-08 00:00:00	3	606	Сидоров С.С.	14
14	2025-02-12 00:00:00	7	603	Иванов И.И.	6
15	2025-02-18 00:00:00	11	607	Михайлова А.А.	13
16	2025-03-02 00:00:00	4	608	Козлова Е.В.	5
17	2025-03-06 00:00:00	5	609	Петров П.П.	9
18	2025-03-12 00:00:00	1	602	Иванов И.И.	17
19	2025-03-17 00:00:00	2	602	Иванов И.И.	20
20	2025-03-25 00:00:00	7	603	Сидоров С.С.	19
21	2025-04-03 00:00:00	11	610	Петров П.П.	10
22	2025-04-09 00:00:00	12	611	Козлова Е.В.	7
23	2025-04-14 00:00:00	13	612	Сидоров С.С.	6
24	2025-04-21 00:00:00	1	602	Иванов И.И.	15
25	2025-04-28 00:00:00	2	602	Иванов И.И.	13
26	2025-05-05 00:00:00	3	613	Петров П.П.	8
27	2025-05-09 00:00:00	4	614	Михайлова А.А.	11
28	2025-05-14 00:00:00	5	615	Козлова Е.В.	9
29	2025-05-20 00:00:00	7	616	Иванов И.И.	5
30	2025-05-25 00:00:00	11	617	Сидоров С.С.	16
31	2025-06-01 00:00:00	12	618	Петров П.П.	12
32	2025-06-05 00:00:00	13	619	Иванов И.И.	10
33	2025-06-10 00:00:00	1	602	Михайлова А.А.	18
34	2025-06-15 00:00:00	2	602	Козлова Е.В.	14
35	2025-06-20 00:00:00	3	603	Сидоров С.С.	19
36	2025-07-01 00:00:00	7	603	Петров П.П.	11
37	2025-07-03 00:00:00	11	604	Иванов И.И.	6
38	2025-07-05 00:00:00	12	605	Михайлова А.А.	7
39	2025-07-08 00:00:00	13	606	Сидоров С.С.	9
40	2025-07-10 00:00:00	1	602	Иванов И.И.	20
41	2025-07-12 00:00:00	2	602	Иванов И.И.	19
42	2025-07-14 00:00:00	3	602	Иванов И.И.	15
43	2025-07-15 00:00:00	7	603	Сидоров С.С.	13
44	2025-07-15 00:00:00	11	604	Петров П.П.	17
45	2025-07-15 00:00:00	12	605	Козлова Е.В.	18
46	2025-07-15 00:00:00	13	606	Сидоров С.С.	20
47	2025-07-15 00:00:00	5	607	Михайлова А.А.	16
48	2025-07-15 00:00:00	4	608	Петров П.П.	12
49	2025-07-15 00:00:00	14	609	Козлова Е.В.	9
50	2025-07-15 00:00:00	15	610	Иванов И.И.	10
51	2025-07-16 01:28:14.779695	15	606	Андрей Мишкин	30
\.


--
-- TOC entry 4925 (class 0 OID 0)
-- Dependencies: 219
-- Name: priemka_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.priemka_id_seq', 4, true);


--
-- TOC entry 4926 (class 0 OID 0)
-- Dependencies: 217
-- Name: sklad_material_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sklad_material_id_seq', 26, true);


--
-- TOC entry 4927 (class 0 OID 0)
-- Dependencies: 221
-- Name: vidacha_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vidacha_id_seq', 51, true);


--
-- TOC entry 4760 (class 2606 OID 33070)
-- Name: priemka priemka_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.priemka
    ADD CONSTRAINT priemka_pkey PRIMARY KEY (id);


--
-- TOC entry 4758 (class 2606 OID 33062)
-- Name: sklad sklad_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sklad
    ADD CONSTRAINT sklad_pkey PRIMARY KEY (material_id);


--
-- TOC entry 4762 (class 2606 OID 33083)
-- Name: vidacha vidacha_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vidacha
    ADD CONSTRAINT vidacha_pkey PRIMARY KEY (id);


--
-- TOC entry 4763 (class 2606 OID 33071)
-- Name: priemka priemka_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.priemka
    ADD CONSTRAINT priemka_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.sklad(material_id) ON DELETE CASCADE;


--
-- TOC entry 4764 (class 2606 OID 33084)
-- Name: vidacha vidacha_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vidacha
    ADD CONSTRAINT vidacha_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.sklad(material_id) ON DELETE CASCADE;


-- Completed on 2025-07-16 01:47:12

--
-- PostgreSQL database dump complete
--

