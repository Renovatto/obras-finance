import sqlite3
import os

db_path = "database.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Banco de dados {db_path} não encontrado. Nenhuma migração necessária.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna 'comentarios' existe
        cursor.execute("PRAGMA table_info(lancamentos_financeiros);")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'comentarios' in columns:
            print("Renomeando coluna 'comentarios' para 'notas'...")
            cursor.execute("ALTER TABLE lancamentos_financeiros RENAME COLUMN comentarios TO notas;")
            conn.commit()
            print("Migração concluída com sucesso.")
        elif 'notas' in columns:
            print("A coluna 'notas' já existe. Migração já realizada anteriormente.")
        else:
            print("Coluna 'comentarios' não encontrada e 'notas' também não. Verifique a estrutura da tabela.")
        
        conn.close()
    except Exception as e:
        print(f"Erro durante a migração: {e}")

if __name__ == "__main__":
    migrate()
