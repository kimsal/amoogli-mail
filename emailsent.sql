CREATE TABLE emailsent (
    id integer NOT NULL,
    subject character varying(500),
    description text,
    reply_to character varying(500),
    sending_email character varying(500),
    sending_name character varying(500),
    published_at timestamp without time zone DEFAULT now(),
    user_id integer
);
CREATE SEQUENCE user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE ONLY emailsent
    ADD CONSTRAINT emailsent_pkey PRIMARY KEY (id);

ALTER TABLE ONLY emailsent
    ADD CONSTRAINT emailsent_user_member_id_fkey FOREIGN KEY (user_member_id) REFERENCES emailsent(id);