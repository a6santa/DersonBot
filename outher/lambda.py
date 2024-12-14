import json
import mysql.connector
import pandas as pd

def get_mysql_connection():
    """Estabelece conexão com o banco de dados MySQL."""
    return mysql.connector.connect(
        host="AAAAAA",
        user="dms_replication",
        password="AAAAAAA",
        database="salaovip"
    )

def run_query() -> dict:
    """Executa query no banco de dados e retorna os resultados em formato JSON."""
    query = """
        select id, data from reservas limit 10
    """
    try:
        conn = get_mysql_connection()
        # Lendo dados com pandas
        df = pd.read_sql(query, conn)
        
        # Convertendo para JSON
        agendamentos_json = df.to_json(orient='records')
        agendamentos_json = json.loads(agendamentos_json)
        
        return agendamentos_json

    except Exception as e:
        print(f"Erro ao executar query: {str(e)}")
        raise e
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print(run_query())