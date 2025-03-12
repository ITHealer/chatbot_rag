import uuid
import logging
import psycopg2
from datetime import datetime
from src.repository.abstr_repository import Repository


class UserRepository(Repository):
    def is_exist_user(self, username) -> bool:
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """SELECT * FROM users WHERE username = %s"""
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result:
                return True
            return False
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_user_by_username(self, username) -> dict:
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """SELECT id, username, full_name, first_name, last_name, role, enabled FROM users where username = %s"""
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result:
                return dict(zip(("id", "username", "full_name", "first_name", "last_name", "role", "enabled"), result))
            return None
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_all(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """SELECT id, username, password, full_name, first_name, last_name, role, enabled FROM users"""
            cursor.execute(sql)
            result = cursor.fetchall()
            users = {}
            for r in result:
                users[r[1]] = dict(
                    zip(("id", "username", "password", "full_name", "first_name", "last_name", "role", "enabled"),
                        r))
            return users
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    # def create_user(self, username, password, email, full_name='', first_name='', last_name=''):

    #     conn = self.create_connection()
    #     cursor = conn.cursor()
    #     try:
    #         sql = """INSERT INTO users  
    #                  (id, username, password, email, full_name, first_name, last_name, role, enabled, created) 
    #                  VALUES (%s, %s, %s, %s, %s, %s, %s, 'USER', 1, %s)"""

    #         # Execute SQL statement
    #         user_id = str(uuid.uuid4())
    #         created_at = datetime.now()
    #         cursor.execute(sql, (user_id, username, password, email, full_name, first_name, last_name, created_at))

    #         # Commit the transaction
    #         conn.commit()
    #         return username
    #     except (Exception, psycopg2.Error) as error:
    #         logging.error(error)
    #         raise ValueError(error)
    #     finally:
    #         if conn:
    #             cursor.close()
    #             conn.close()
    
    def create_user(self, username, password, email, full_name='', first_name='', last_name='', role='USER'):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO users  
                    (id, username, password, email, full_name, first_name, last_name, role, enabled, created) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, %s)"""

            # Execute SQL statement
            user_id = str(uuid.uuid4())
            created_at = datetime.now()
            cursor.execute(sql, (user_id, username, password, email, full_name, first_name, last_name, role, created_at))

            # Commit the transaction
            conn.commit()
            return username
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_user_role(self, username) -> str:
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """SELECT role FROM users WHERE username = %s"""
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def change_password(self, username, new_hashed_password):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """UPDATE users 
                     SET password = %s
                     WHERE username = %s"""

            # Execute SQL statement
            cursor.execute(sql, (new_hashed_password, username))

            # Commit the transaction
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def is_exist_session(self, session_id) -> bool:
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """SELECT * FROM chat_sessions WHERE id = %s"""
            cursor.execute(sql, (session_id,))
            result = cursor.fetchone()
            if result:
                return True
            return False
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def create_session(self, user_id):

        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """INSERT INTO chat_sessions  
                     (id, title, start_date, end_date, state, user_id, final_answer, duration, quantity_rating, total_rating, avg_rating) 
                     VALUES (%s, %s, %s, NULL, NULL, %s, NULL, NULL, NULL, NULL, NULL)"""

            # Generate timestamp for created_at and updated_at
            timestamp = datetime.now()

            # Execute SQL statement
            session_id = str(uuid.uuid4())
            created_at = datetime.now()
            cursor.execute(sql, (session_id, '', created_at, user_id))

            # Commit the transaction
            conn.commit()
            return session_id
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()

    def edit_session(self, session_id, new_title):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """UPDATE chat_sessions 
                     SET title = %s
                     WHERE id = %s"""

            # Execute SQL statement
            cursor.execute(sql, (new_title, session_id))

            # Commit the transaction
            conn.commit()
            return True
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()


    def delete_session(self, session_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            sql = """DELETE FROM messages WHERE session_id = %s"""
            cursor.execute(sql, (session_id,))
            sql = """DELETE FROM chat_sessions WHERE id = %s"""
            cursor.execute(sql, (session_id,))

            # Commit the transaction
            conn.commit()
            return True
        except (Exception, psycopg2.Error) as error:
            logging.error(error)
            raise ValueError(error)
        finally:
            if conn:
                cursor.close()
                conn.close()


    def get_sessions_from_user(self, user_id, limit=10):
        conn = self.create_connection()
        cursor = conn.cursor()
        try:
            select_query = """SELECT id, title
                              FROM chat_sessions
                              WHERE user_id = %s 
                              ORDER BY start_date DESC
                              LIMIT %s"""
            cursor.execute(select_query, (user_id, limit))
            result = cursor.fetchall()
            return [dict(zip(('id', 'title'), r)) for r in result]

        except (Exception, psycopg2.Error) as error:
            logging.error("Error:", error)
        finally:
            if conn:
                cursor.close()
                conn.close()
