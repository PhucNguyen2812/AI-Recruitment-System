--
-- PostgreSQL database dump
--

\restrict 3dkp2WOWgm50vmABfF9XOy7lTKg0nfvRCbwrlVbM2LnQj9TSdLBf1kvDjfVP80x

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

-- Started on 2026-03-19 22:29:13

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
-- TOC entry 5 (class 2615 OID 20748)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 5013 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


--
-- TOC entry 872 (class 1247 OID 20770)
-- Name: trangthaichiendich; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.trangthaichiendich AS ENUM (
    'dang_mo',
    'da_dong'
);


ALTER TYPE public.trangthaichiendich OWNER TO postgres;

--
-- TOC entry 869 (class 1247 OID 20764)
-- Name: trangthaicongviec; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.trangthaicongviec AS ENUM (
    'dang_mo',
    'da_dong'
);


ALTER TYPE public.trangthaicongviec OWNER TO postgres;

--
-- TOC entry 866 (class 1247 OID 20756)
-- Name: trangthaidon; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.trangthaidon AS ENUM (
    'dang_cho',
    'da_nhan',
    'khong_phu_hop'
);


ALTER TYPE public.trangthaidon OWNER TO postgres;

--
-- TOC entry 863 (class 1247 OID 20750)
-- Name: vaitro; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.vaitro AS ENUM (
    'quan_tri_vien',
    'nhan_su'
);


ALTER TYPE public.vaitro OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 227 (class 1259 OID 20923)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 20831)
-- Name: chien_dich; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chien_dich (
    id uuid NOT NULL,
    tieu_de character varying(255) NOT NULL,
    mo_ta text,
    ngay_bat_dau timestamp with time zone NOT NULL,
    ngay_ket_thuc timestamp with time zone NOT NULL,
    trang_thai public.trangthaichiendich NOT NULL,
    creator_id uuid NOT NULL,
    ngay_tao timestamp with time zone
);


ALTER TABLE public.chien_dich OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 20849)
-- Name: cong_viec; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cong_viec (
    id uuid NOT NULL,
    tieu_de character varying(255) NOT NULL,
    id_vi_tri uuid NOT NULL,
    campaign_id uuid NOT NULL,
    creator_id uuid NOT NULL,
    mo_ta text,
    yeu_cau text,
    trang_thai public.trangthaicongviec NOT NULL,
    ahp_weights json,
    ngay_tao timestamp with time zone
);


ALTER TABLE public.cong_viec OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 20898)
-- Name: don_ung_tuyen; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.don_ung_tuyen (
    id uuid NOT NULL,
    id_ung_vien uuid NOT NULL,
    id_cong_viec uuid NOT NULL,
    duong_dan_cv character varying(500),
    ma_hash_cv character varying(32) NOT NULL,
    diem_rf integer,
    diem_ahp double precision,
    trang_thai public.trangthaidon NOT NULL,
    ngay_nop timestamp with time zone
);


ALTER TABLE public.don_ung_tuyen OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 20953)
-- Name: ket_qua_xep_hang; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ket_qua_xep_hang (
    id uuid NOT NULL,
    id_chien_dich uuid NOT NULL,
    id_cong_viec uuid NOT NULL,
    ho_ten character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    so_dien_thoai character varying(20),
    hang integer NOT NULL,
    diem_ahp double precision NOT NULL,
    nhom character varying(20) NOT NULL,
    diem_chi_tiet json,
    ten_cong_viec character varying(255),
    ten_chien_dich character varying(255),
    ngay_luu timestamp with time zone
);


ALTER TABLE public.ket_qua_xep_hang OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 20775)
-- Name: nguoi_dung; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nguoi_dung (
    id uuid NOT NULL,
    email character varying(255) NOT NULL,
    mat_khau_ma_hoa character varying(255) NOT NULL,
    vai_tro public.vaitro NOT NULL,
    phien_dang_nhap character varying(255),
    ngay_tao timestamp with time zone
);


ALTER TABLE public.nguoi_dung OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 20816)
-- Name: nhat_ky_he_thong; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nhat_ky_he_thong (
    id integer NOT NULL,
    id_nguoi_dung uuid,
    hanh_dong character varying(100) NOT NULL,
    chi_tiet character varying(2000),
    dia_chi_ip character varying(45),
    ngay_tao timestamp with time zone
);


ALTER TABLE public.nhat_ky_he_thong OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 20815)
-- Name: nhat_ky_he_thong_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.nhat_ky_he_thong_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nhat_ky_he_thong_id_seq OWNER TO postgres;

--
-- TOC entry 5015 (class 0 OID 0)
-- Dependencies: 221
-- Name: nhat_ky_he_thong_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.nhat_ky_he_thong_id_seq OWNED BY public.nhat_ky_he_thong.id;


--
-- TOC entry 229 (class 1259 OID 20930)
-- Name: nhat_ky_thong_bao; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.nhat_ky_thong_bao (
    id integer NOT NULL,
    id_nguoi_dung uuid NOT NULL,
    noi_dung character varying(2000) NOT NULL,
    da_doc boolean,
    loai character varying(50),
    ngay_tao timestamp with time zone
);


ALTER TABLE public.nhat_ky_thong_bao OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 20929)
-- Name: nhat_ky_thong_bao_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.nhat_ky_thong_bao_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.nhat_ky_thong_bao_id_seq OWNER TO postgres;

--
-- TOC entry 5016 (class 0 OID 0)
-- Dependencies: 228
-- Name: nhat_ky_thong_bao_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.nhat_ky_thong_bao_id_seq OWNED BY public.nhat_ky_thong_bao.id;


--
-- TOC entry 225 (class 1259 OID 20879)
-- Name: ung_vien; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ung_vien (
    id uuid NOT NULL,
    email character varying(255) NOT NULL,
    ho_ten character varying(255) NOT NULL,
    so_dien_thoai character varying(20),
    file_hash character varying(32),
    id_cong_viec uuid,
    ngay_tao timestamp with time zone
);


ALTER TABLE public.ung_vien OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 20787)
-- Name: vi_tri; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vi_tri (
    id uuid NOT NULL,
    ten character varying(255) NOT NULL,
    ma character varying(50) NOT NULL,
    mo_ta text,
    ngay_tao timestamp with time zone
);


ALTER TABLE public.vi_tri OWNER TO postgres;

--
-- TOC entry 4804 (class 2604 OID 20819)
-- Name: nhat_ky_he_thong id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nhat_ky_he_thong ALTER COLUMN id SET DEFAULT nextval('public.nhat_ky_he_thong_id_seq'::regclass);


--
-- TOC entry 4805 (class 2604 OID 20933)
-- Name: nhat_ky_thong_bao id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nhat_ky_thong_bao ALTER COLUMN id SET DEFAULT nextval('public.nhat_ky_thong_bao_id_seq'::regclass);


--
-- TOC entry 5004 (class 0 OID 20923)
-- Dependencies: 227
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
02fb7e3ecdff
\.


--
-- TOC entry 5000 (class 0 OID 20831)
-- Dependencies: 223
-- Data for Name: chien_dich; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chien_dich (id, tieu_de, mo_ta, ngay_bat_dau, ngay_ket_thuc, trang_thai, creator_id, ngay_tao) FROM stdin;
4561eb31-8f3f-4f7f-8e37-a99a25073e1c	Tuyển dụng tháng 3/2026	Đợt tuyển lớn nhất năm	2026-03-13 08:11:08.920152+07	2026-04-12 08:11:08.920155+07	dang_mo	c826fa70-fc93-4036-8765-cb4a1f918403	2026-03-13 08:11:08.924567+07
\.


--
-- TOC entry 5001 (class 0 OID 20849)
-- Dependencies: 224
-- Data for Name: cong_viec; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cong_viec (id, tieu_de, id_vi_tri, campaign_id, creator_id, mo_ta, yeu_cau, trang_thai, ahp_weights, ngay_tao) FROM stdin;
1bea9bf3-b7d9-4f13-aee3-10c3cfc9ec3f	Thực tập sinh Marketing	af5ba717-0509-4811-9c36-b441bc107080	4561eb31-8f3f-4f7f-8e37-a99a25073e1c	c826fa70-fc93-4036-8765-cb4a1f918403	\N	\N	dang_mo	{"ky_thuat": 0.322891, "hoc_van": 0.186421, "ngoai_ngu": 0.245344, "tich_cuc": 0.245344}	2026-03-13 08:11:08.931556+07
b25307dc-ea38-41d1-a575-0570fa878705	Thực tập sinh Lập trình (IT Intern)	206d0df9-b216-482e-ba87-8216c7a5c864	4561eb31-8f3f-4f7f-8e37-a99a25073e1c	c826fa70-fc93-4036-8765-cb4a1f918403	\N	\N	dang_mo	{"weights": {"ky_thuat": 0.466849, "hoc_van": 0.27759, "ngoai_ngu": 0.160267, "tich_cuc": 0.095295}, "matrix": [[1.0, 2.0, 3.0, 4.0], [0.5, 1.0, 2.0, 3.0], [0.3333333333333333, 0.5, 1.0, 2.0], [0.25, 0.3333333333333333, 0.5, 1.0]]}	2026-03-13 08:11:08.931552+07
\.


--
-- TOC entry 5003 (class 0 OID 20898)
-- Dependencies: 226
-- Data for Name: don_ung_tuyen; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.don_ung_tuyen (id, id_ung_vien, id_cong_viec, duong_dan_cv, ma_hash_cv, diem_rf, diem_ahp, trang_thai, ngay_nop) FROM stdin;
446bddb1-ccfe-4253-a63f-f880f80780f6	a6cc80ca-070d-4e5b-8e70-c546478466d0	b25307dc-ea38-41d1-a575-0570fa878705	storage/cvs\\797635cba22f48c8bf3d63cbfe5a7150_CV-NguyenTanKiet-.pdf	e312712628defdc806c8f30dff00d74c	1	6.7405	da_nhan	2026-03-15 02:27:47.320695+07
\.


--
-- TOC entry 5007 (class 0 OID 20953)
-- Dependencies: 230
-- Data for Name: ket_qua_xep_hang; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ket_qua_xep_hang (id, id_chien_dich, id_cong_viec, ho_ten, email, so_dien_thoai, hang, diem_ahp, nhom, diem_chi_tiet, ten_cong_viec, ten_chien_dich, ngay_luu) FROM stdin;
\.


--
-- TOC entry 4996 (class 0 OID 20775)
-- Dependencies: 219
-- Data for Name: nguoi_dung; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nguoi_dung (id, email, mat_khau_ma_hoa, vai_tro, phien_dang_nhap, ngay_tao) FROM stdin;
c826fa70-fc93-4036-8765-cb4a1f918403	admin@company.com	$pbkdf2-sha256$29000$ZyyF0Lr3vjfGmJNyTum9tw$26MkiGm96/zNLH2uOMMKHbFTL8uzW0VJKg4KPKSuzv4	quan_tri_vien	edbd6bc7-6156-4de1-8f37-66d0fb2f54bd	2026-03-13 08:10:15.89319+07
\.


--
-- TOC entry 4999 (class 0 OID 20816)
-- Dependencies: 222
-- Data for Name: nhat_ky_he_thong; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nhat_ky_he_thong (id, id_nguoi_dung, hanh_dong, chi_tiet, dia_chi_ip, ngay_tao) FROM stdin;
\.


--
-- TOC entry 5006 (class 0 OID 20930)
-- Dependencies: 229
-- Data for Name: nhat_ky_thong_bao; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.nhat_ky_thong_bao (id, id_nguoi_dung, noi_dung, da_doc, loai, ngay_tao) FROM stdin;
\.


--
-- TOC entry 5002 (class 0 OID 20879)
-- Dependencies: 225
-- Data for Name: ung_vien; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ung_vien (id, email, ho_ten, so_dien_thoai, file_hash, id_cong_viec, ngay_tao) FROM stdin;
a6cc80ca-070d-4e5b-8e70-c546478466d0	admin@hcmunre.edu.vn	TS. Lê Thị B	\N	\N	b25307dc-ea38-41d1-a575-0570fa878705	2026-03-15 02:27:47.312152+07
\.


--
-- TOC entry 4997 (class 0 OID 20787)
-- Dependencies: 220
-- Data for Name: vi_tri; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vi_tri (id, ten, ma, mo_ta, ngay_tao) FROM stdin;
206d0df9-b216-482e-ba87-8216c7a5c864	Lập trình viên	IT_Intern	Lập trình viên	2026-03-13 08:11:08.916954+07
af5ba717-0509-4811-9c36-b441bc107080	Marketing	Marketing_Intern	NV Marketing	2026-03-13 08:11:08.916958+07
\.


--
-- TOC entry 5017 (class 0 OID 0)
-- Dependencies: 221
-- Name: nhat_ky_he_thong_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.nhat_ky_he_thong_id_seq', 1, false);


--
-- TOC entry 5018 (class 0 OID 0)
-- Dependencies: 228
-- Name: nhat_ky_thong_bao_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.nhat_ky_thong_bao_id_seq', 1, false);


--
-- TOC entry 4832 (class 2606 OID 20928)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 4815 (class 2606 OID 20843)
-- Name: chien_dich chien_dich_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chien_dich
    ADD CONSTRAINT chien_dich_pkey PRIMARY KEY (id);


--
-- TOC entry 4817 (class 2606 OID 20861)
-- Name: cong_viec cong_viec_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cong_viec
    ADD CONSTRAINT cong_viec_pkey PRIMARY KEY (id);


--
-- TOC entry 4827 (class 2606 OID 20909)
-- Name: don_ung_tuyen don_ung_tuyen_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.don_ung_tuyen
    ADD CONSTRAINT don_ung_tuyen_pkey PRIMARY KEY (id);


--
-- TOC entry 4838 (class 2606 OID 20967)
-- Name: ket_qua_xep_hang ket_qua_xep_hang_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ket_qua_xep_hang
    ADD CONSTRAINT ket_qua_xep_hang_pkey PRIMARY KEY (id);


--
-- TOC entry 4808 (class 2606 OID 20785)
-- Name: nguoi_dung nguoi_dung_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nguoi_dung
    ADD CONSTRAINT nguoi_dung_pkey PRIMARY KEY (id);


--
-- TOC entry 4813 (class 2606 OID 20825)
-- Name: nhat_ky_he_thong nhat_ky_he_thong_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nhat_ky_he_thong
    ADD CONSTRAINT nhat_ky_he_thong_pkey PRIMARY KEY (id);


--
-- TOC entry 4834 (class 2606 OID 20940)
-- Name: nhat_ky_thong_bao nhat_ky_thong_bao_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nhat_ky_thong_bao
    ADD CONSTRAINT nhat_ky_thong_bao_pkey PRIMARY KEY (id);


--
-- TOC entry 4823 (class 2606 OID 20888)
-- Name: ung_vien ung_vien_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ung_vien
    ADD CONSTRAINT ung_vien_pkey PRIMARY KEY (id);


--
-- TOC entry 4825 (class 2606 OID 20890)
-- Name: ung_vien unique_candidate_job; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ung_vien
    ADD CONSTRAINT unique_candidate_job UNIQUE (email, id_cong_viec);


--
-- TOC entry 4811 (class 2606 OID 20796)
-- Name: vi_tri vi_tri_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vi_tri
    ADD CONSTRAINT vi_tri_pkey PRIMARY KEY (id);


--
-- TOC entry 4818 (class 1259 OID 20877)
-- Name: ix_cong_viec_campaign_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cong_viec_campaign_id ON public.cong_viec USING btree (campaign_id);


--
-- TOC entry 4819 (class 1259 OID 20878)
-- Name: ix_cong_viec_id_vi_tri; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cong_viec_id_vi_tri ON public.cong_viec USING btree (id_vi_tri);


--
-- TOC entry 4828 (class 1259 OID 20922)
-- Name: ix_don_ung_tuyen_id_cong_viec; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_don_ung_tuyen_id_cong_viec ON public.don_ung_tuyen USING btree (id_cong_viec);


--
-- TOC entry 4829 (class 1259 OID 20920)
-- Name: ix_don_ung_tuyen_job_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_don_ung_tuyen_job_status ON public.don_ung_tuyen USING btree (id_cong_viec, trang_thai);


--
-- TOC entry 4830 (class 1259 OID 20921)
-- Name: ix_don_ung_tuyen_ma_hash_cv; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_don_ung_tuyen_ma_hash_cv ON public.don_ung_tuyen USING btree (ma_hash_cv);


--
-- TOC entry 4835 (class 1259 OID 20974)
-- Name: ix_ket_qua_xep_hang_id_chien_dich; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ket_qua_xep_hang_id_chien_dich ON public.ket_qua_xep_hang USING btree (id_chien_dich);


--
-- TOC entry 4836 (class 1259 OID 20973)
-- Name: ix_ket_qua_xep_hang_id_cong_viec; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ket_qua_xep_hang_id_cong_viec ON public.ket_qua_xep_hang USING btree (id_cong_viec);


--
-- TOC entry 4806 (class 1259 OID 20786)
-- Name: ix_nguoi_dung_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_nguoi_dung_email ON public.nguoi_dung USING btree (email);


--
-- TOC entry 4820 (class 1259 OID 20897)
-- Name: ix_ung_vien_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ung_vien_email ON public.ung_vien USING btree (email);


--
-- TOC entry 4821 (class 1259 OID 20896)
-- Name: ix_ung_vien_file_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ung_vien_file_hash ON public.ung_vien USING btree (file_hash);


--
-- TOC entry 4809 (class 1259 OID 20797)
-- Name: ix_vi_tri_ma; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_vi_tri_ma ON public.vi_tri USING btree (ma);


--
-- TOC entry 4840 (class 2606 OID 20844)
-- Name: chien_dich chien_dich_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chien_dich
    ADD CONSTRAINT chien_dich_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.nguoi_dung(id);


--
-- TOC entry 4841 (class 2606 OID 20867)
-- Name: cong_viec cong_viec_campaign_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cong_viec
    ADD CONSTRAINT cong_viec_campaign_id_fkey FOREIGN KEY (campaign_id) REFERENCES public.chien_dich(id) ON DELETE CASCADE;


--
-- TOC entry 4842 (class 2606 OID 20872)
-- Name: cong_viec cong_viec_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cong_viec
    ADD CONSTRAINT cong_viec_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.nguoi_dung(id);


--
-- TOC entry 4843 (class 2606 OID 20862)
-- Name: cong_viec cong_viec_id_vi_tri_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cong_viec
    ADD CONSTRAINT cong_viec_id_vi_tri_fkey FOREIGN KEY (id_vi_tri) REFERENCES public.vi_tri(id);


--
-- TOC entry 4845 (class 2606 OID 20915)
-- Name: don_ung_tuyen don_ung_tuyen_id_cong_viec_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.don_ung_tuyen
    ADD CONSTRAINT don_ung_tuyen_id_cong_viec_fkey FOREIGN KEY (id_cong_viec) REFERENCES public.cong_viec(id) ON DELETE CASCADE;


--
-- TOC entry 4846 (class 2606 OID 20910)
-- Name: don_ung_tuyen don_ung_tuyen_id_ung_vien_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.don_ung_tuyen
    ADD CONSTRAINT don_ung_tuyen_id_ung_vien_fkey FOREIGN KEY (id_ung_vien) REFERENCES public.ung_vien(id) ON DELETE CASCADE;


--
-- TOC entry 4848 (class 2606 OID 20968)
-- Name: ket_qua_xep_hang ket_qua_xep_hang_id_chien_dich_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ket_qua_xep_hang
    ADD CONSTRAINT ket_qua_xep_hang_id_chien_dich_fkey FOREIGN KEY (id_chien_dich) REFERENCES public.chien_dich(id);


--
-- TOC entry 4839 (class 2606 OID 20826)
-- Name: nhat_ky_he_thong nhat_ky_he_thong_id_nguoi_dung_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nhat_ky_he_thong
    ADD CONSTRAINT nhat_ky_he_thong_id_nguoi_dung_fkey FOREIGN KEY (id_nguoi_dung) REFERENCES public.nguoi_dung(id) ON DELETE SET NULL;


--
-- TOC entry 4847 (class 2606 OID 20941)
-- Name: nhat_ky_thong_bao nhat_ky_thong_bao_id_nguoi_dung_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.nhat_ky_thong_bao
    ADD CONSTRAINT nhat_ky_thong_bao_id_nguoi_dung_fkey FOREIGN KEY (id_nguoi_dung) REFERENCES public.nguoi_dung(id) ON DELETE CASCADE;


--
-- TOC entry 4844 (class 2606 OID 20891)
-- Name: ung_vien ung_vien_id_cong_viec_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ung_vien
    ADD CONSTRAINT ung_vien_id_cong_viec_fkey FOREIGN KEY (id_cong_viec) REFERENCES public.cong_viec(id) ON DELETE CASCADE;


--
-- TOC entry 5014 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


-- Completed on 2026-03-19 22:29:13

--
-- PostgreSQL database dump complete
--

\unrestrict 3dkp2WOWgm50vmABfF9XOy7lTKg0nfvRCbwrlVbM2LnQj9TSdLBf1kvDjfVP80x

