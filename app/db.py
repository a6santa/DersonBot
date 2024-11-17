import time

from tinydb import TinyDB, Query


class MessageDatabase:
    """Classe banco de dados"""

    def __init__(self, db_path="db.json", table="_default"):
        """Inicializa o banco de dados com o caminho especificado"""
        self.db = TinyDB(db_path)
        self.table = self.db.table(table)

    def insert(self, value: dict):
        """Inseri um registro unico"""
        self.table.insert(value)

    def register_user(self, user_id):
        """Registra um novo usuário com uma lista vazia de mensagens"""
        self.table.insert({"user_id": user_id, "messages": []})

    def append_message(self, user_id, message):
        """Adiciona uma nova mensagem à lista de mensagens de um usuário"""
        user = Query()
        user_data = self.table.get(user.user_id == user_id)

        if user_data:
            user_data["messages"].append(message)
            self.table.update(
                {"messages": user_data["messages"]}, user.user_id == user_id
            )
        else:
            self.register_user(user_id)
            self.append_message(user_id, message)

    def search_messages(self, user_id):
        """Busca mensagens no banco local com base na coluna e valor especificados"""
        user = Query()
        return self.table.search(user.user_id == user_id)

    def search_thread(self, user_id):
        """Busca mensagens no banco local com base na coluna e valor especificados"""
        user = Query()

        return self.table.search(
            (user.user_id == user_id) & (user.expiron_time > time.time())
        )
