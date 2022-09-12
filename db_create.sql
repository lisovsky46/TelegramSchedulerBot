
CREATE TABLE IF NOT EXISTS public.chats
(
    id serial NOT NULL,
    chat_id character varying(50) COLLATE pg_catalog."default" NOT NULL,
    name character varying(50) COLLATE pg_catalog."default" NOT NULL,
    joined_time timestamp with time zone NOT NULL,
    members_count integer NOT NULL DEFAULT 0,
    CONSTRAINT chats_pkey PRIMARY KEY (id),
    CONSTRAINT chats_chat_id_key UNIQUE (chat_id)
);

CREATE TABLE IF NOT EXISTS public.polls
(
    id serial NOT NULL,
    poll_id character varying COLLATE pg_catalog."default" NOT NULL,
    chat_id character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT polls_pkey PRIMARY KEY (id),
    CONSTRAINT polls_poll_id_key UNIQUE (poll_id),
    CONSTRAINT chat_id FOREIGN KEY (chat_id)
        REFERENCES public.chats (chat_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);
