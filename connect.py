import psycopg2
import os

# 環境変数から接続情報を取得する
conn_info = {
    'dbname': os.environ.get('DB_NAME', 'postgres'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'password': os.environ.get('DB_PASSWORD', 'hayato8810'),
    'port': os.environ.get('DB_PORT', 5433)
}

def get_db_connection():
    try:
        # データベース接続
        conn = psycopg2.connect(**conn_info)
        return conn
    except psycopg2.DatabaseError as e:
        print(f"データベース接続エラー: {e}")
        return None

def create_tables():
    # テーブルを作成するSQLコマンド

    commands = (
        """
        CREATE TYPE exercise_type AS ENUM ('BP', 'SQ', 'DL');
        """,
        """
        CREATE TABLE IF NOT EXISTS Users (
            user_id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            password VARCHAR(100)
        );
        """,
        """ 
        CREATE TABLE IF NOT EXISTS Recorder (
            record_id SERIAL PRIMARY KEY,
            user_id INT REFERENCES Users (user_id),
            date DATE,
            exercise exercise_type,
            weight INT,
            rep INT,
            set INT
        );
        """
    )

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # 各コマンドを実行
        for command in commands:
            cur.execute(command)
        # コミット変更
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


