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
        self.con = psycopg2.connect(host=self.host, port=self.port, dbname=self.dbname, user=self.user, password=self.password)
    # Get query result, fetch "limit" rows, get all rows as default
    def query(self, query, limit=-1):
        cur = self.con.cursor()
        cur.execute(f"{query}")
        if limit == -1 :
            res = cur.fetchall()
        else:
            res = cur.fetchmany(limit)
        cur.close()
        return res
    
    # Get database schema, {table:columns}
    def get_db_schema(self):
        cur = self.con.cursor()
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
                    "nullable": col[3]
                } for col in columns
            ]
        # Marshall to JSON
        res = json.dumps(schema)
        cur.close()
        return res
    # Get Foreign Keys
    def get_foregin_keys(self):
        cur = self.con.cursor()
        cur.execute("""SELECT
                        tc.constraint_name,
                        tc.table_name AS child_table,
                        kcu.column_name AS child_column,
                        ccu.table_name AS parent_table,
                        ccu.column_name AS parent_column
                    FROM
                        information_schema.table_constraints AS tc
                    JOIN
                        information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                    JOIN
                        information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                    WHERE
                        tc.constraint_type = 'FOREIGN KEY'""")
        fks = cur.fetchall()
        fk_schema = {}
        for fk in fks:
            fk_schema[fk[0]] = {
                "child_table": fk[1],
                "child_column": fk[2],
                "parent_table": fk[3],
                "parent_column": fk[4]
                }
        res = json.dumps(fk_schema)
        cur.close()
        return res
    
    # Get user defined types
    def get_db_types(self):
        cur = self.con.cursor()
        cur.execute("""
                    SELECT pg_type.typname, pg_enum.enumlabel
                    FROM pg_type 
                    JOIN pg_enum ON pg_enum.enumtypid = pg_type.oid;""")
        types = cur.fetchall()
        dict_types = {}
        for t in types:
            if t[0] in dict_types:
                dict_types[t[0]].append(t[1])
            else:
                dict_types[t[0]] = []
                dict_types[t[0]].append(t[1])
        # Marshall to JSON
        res = json.dumps(dict_types,ensure_ascii = False)
        cur.close()
        return res
            
        
    # Insert Data
    def insert_data(self, table, *data):
        cur = self.con.cursor()
        match table:
            case "certificate":
                cur.execute(f"""INSERT INTO {table} 
                            ( id, name ) values 
                            ('{data[0]}','{data[1]}') ON CONFLICT(id) DO NOTHING""".replace('\n',''))
            case "jobcategory":
                cur.execute(f"""INSERT INTO {table} 
                            ( id, name ) values 
                            ('{data[0]}','{data[1]}') ON CONFLICT(id) DO NOTHING""".replace('\n',''))
            case "pe":
                cur.execute(f"""INSERT INTO {table} 
                            ( id, BloodType, ExamDate, ExamLocation, Height, Chest, Weight, BpHigh, BpLow, 
                            VisionL, VisionR, PhyGrade) values 
                            ('{data[0]}','{data[1]}','{data[2]}','{data[3]}',{data[4]},{data[5]},{data[6]},{data[7]},{data[8]},{data[9]},
                            {data[10]},{data[11]})  ON CONFLICT(id) DO NOTHING""".replace('\n',''))
            case "personalinformation":
                cur.execute(f"""INSERT INTO {table} 
                            ( id, name, residentidf, residentidb, address1, address2, address3, address4, parentsfather, 
                            parentsmother, marry, child, religion, academicability, jobname, jobyear, certificate) values 
                            ('{data[0]}','{data[1]}','{data[2]}','{data[3]}','{data[4]}','{data[5]}','{data[6]}','{data[7]}',{data[8]},{data[9]},{data[10]},
                            {data[11]},'{data[12]}','{data[13]}','{data[14]}',{data[15]},'{data[16]}')  ON CONFLICT(id) DO NOTHING""".replace('\n',''))
            case "soldierinformation":
                cur.execute(f"""INSERT INTO {table} 
                            ( id, endate, durationday, rank, specialty, affiliation, discipline ) values
                            ('{data[0]}','{data[1]}',{data[2]},'{data[3]}','{data[4]}','{data[5]}',array{data[6]}) ON CONFLICT(id) DO NOTHING""".replace('\n',''))
            case "specialty":
                cur.execute(f"""INSERT INTO {table}
                            ( id, classname, classcode, specialtyname ) values 
                            ('{data[0]}','{data[1]}',{data[2]},'{data[3]}')""".replace('\n',''))
            case "units":
                cur.execute(f"""INSERT INTO {table} 
                            ( id, commander, subordinateunit, organization, num, name ) values 
                            ('{data[0]}','{data[1]}',array{data[2]},'{data[3]}',{data[4]},'{data[5]}') ON CONFLICT(id) DO NOTHING""".replace('\n',''))
        self.con.commit()
        cur.close()
    
    def close(self):
            self.con.close()