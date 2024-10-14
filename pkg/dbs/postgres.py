import psycopg2
import sql
import json


class PSQL:
    # init
    def __init__(self, host, port, dbname, user, password):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
    # Get query result, fetch "limit" rows, get all rows as default
    def query(self, query, limit=-1):
        con = psycopg2.connect(host=self.host, port=self.port, dbname=self.dbname, user=self.user, password=self.password)
        cur = con.cursor()
        cur.execute(f"{query}")
        if limit == -1 :
            res = cur.fetchall()
        else:
            res = cur.fetchmany(limit)
        cur.close()
        con.close()
        return res
    # Get database schema, {table:columns}
    def get_db_schema(self):
        con = psycopg2.connect(host=self.host, port=self.port, dbname=self.dbname, user=self.user, password=self.password)
        cur = con.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()

        schema = {}

        for table in tables:
            table_name = table[0]
            
            # Get column information
            cur.execute(f"SELECT column_name, data_type, character_maximum_length, is_nullable FROM information_schema.columns WHERE table_name = '{table_name}'")
                
            columns = cur.fetchall()
            
            schema[table_name] = [
                {
                    "name": col[0],
                    "type": col[1],
                    "max_length": col[2],
                    "nullable": col[3]
                } for col in columns
            ]
        # Marshall to JSON
        res = json.dumps(schema)
        return res