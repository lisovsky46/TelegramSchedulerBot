from datetime import datetime
import psycopg

from settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_SSL_MODE, DB_USER

class db_chat:

    chat_id:int
    name:str
    joined_time:datetime
    members_count:int

    def __init__(self, chat_id, name, joined_time, members_count) -> None:
        self.chat_id = int(chat_id)
        self.name = name
        self.joined_time = joined_time
        self.members_count = members_count


class bot_db:

    def try_create(self):
        self.execute_from_file('db_create.sql')

    def execute_from_file(self, filename):
        fd = open(filename, 'r')
        sqlFile = fd.read()
        fd.close()

        sqlCommands = sqlFile.split(';')

        for command in sqlCommands:
            self.cursor.execute(command)
            self.db.commit()

    def connect(self):
        self.db = psycopg.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, sslmode=DB_SSL_MODE)
        self.cursor:psycopg.cursor = self.db.cursor()

    # def create():
    #     'CREATE TABLE "default".chats (chat_id serial PRIMARY KEY, name VARCHAR ( 50 ) NOT NULL, TIMESTAMP NOT NULL )'

    def add_chat(self, id, name, members_count):
        self.cursor.execute('INSERT INTO "public".chats(chat_id, name, joined_time, members_count) VALUES (%s, %s, %s, %s)', (id, name, datetime.now(), members_count))
        self.db.commit()

    def delete_chat(self, id):
        self.cursor.execute('DELETE FROM "public".polls WHERE chat_id = %s', (str(id),))
        self.cursor.execute('DELETE FROM "public".chats WHERE chat_id = %s', (str(id),))
        self.db.commit()

    def update_user_count(self, id, count):
        self.cursor.execute('UPDATE public.chats SET members_count = %s WHERE chat_id = %s', (count, str(id)))
        self.db.commit()

    def add_poll(self, chat_id, poll_id):
        self.cursor.execute('INSERT INTO "public".polls(poll_id, chat_id) VALUES (%s, %s)', (poll_id, chat_id))
        self.db.commit()

    def get_all_chats(self) -> list:
        self.cursor.execute('SELECT * FROM "public".chats;')
        for row in self.cursor.fetchall():
            yield db_chat(row[1], row[2], row[3], row[4])

    def get_all_polls(self):
        self.cursor.execute('SELECT * FROM "public".polls;')
        for row in self.cursor.fetchall():
            yield (row[1], row[2])
            # yield {row[1] : row[2]}

        