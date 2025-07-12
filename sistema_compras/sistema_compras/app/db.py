import os
import mysql.connector

def get_connection():
    """
    Retorna apenas a conexão com o banco de dados.
    O cursor deve ser criado no código onde a conexão é usada,
    permitindo flexibilidade (com ou sem dictionary=True).
    """
    ambiente = os.environ.get("AMBIENTE", "LOCAL")

    if ambiente == "SERVIDOR":
        host = 'srvdb-dev'  # ou 192.168.140.4
        port = 3306
    else:
        host = '160.20.22.99'
        port = 3360

    conn = mysql.connector.connect(
        host=host,
        port=port,
        user='aluno32',
        password='A+IByOSdL98=',
        database='fasiclin'
    )

    return conn
