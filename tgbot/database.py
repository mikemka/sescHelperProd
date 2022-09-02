import sqlite3


class BotDB:
    def __init__(self, db_file):
        """ Инициализация базы данных """
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """ Проверяем, есть ли юзер в БД """
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def is_teacher(self, user_id):
        """ Является ли юзер учителем """
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ? AND `is_teacher` = 1", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        """ Достаем id юзера в БД по его `user_id` """
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id, form):
        """ Добавляем юзера в БД """
        self.cursor.execute("INSERT INTO `users` (`user_id`, `form`) VALUES (?, ?)", (user_id, form,))
        return self.conn.commit()

    def add_teacher(self, user_id, form):
        """ Добавляем учителя в БД """
        self.cursor.execute("INSERT INTO `users` (`user_id`, `form`, `is_teacher`) VALUES (?, ?, ?)",
                            (user_id, form, True))
        return self.conn.commit()

    def get_user_form(self, user_id):
        """ Получаем класс юзера """
        result = self.cursor.execute("SELECT `form` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def remove_user(self, user_id):
        """ Удаление юзера из БД """
        self.cursor.execute("DELETE from `users` WHERE `id` = ?", (self.get_user_id(user_id),))
        return self.conn.commit()
    
    def get_users(self):
        """ Все пользователи бота """
        result = self.cursor.execute("SELECT `user_id` FROM `users`")
        return result.fetchall()

    def close(self):
        """ Закрываем соединение с БД """
        self.conn.close()
