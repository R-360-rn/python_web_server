from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, parse_qsl
from jsonschema import validate as jsonschema_validate
import datetime
import sqlite3
import json

db_name = 'users.db'
sql_create_table = '''CREATE TABLE if not exists persons (
                id integer primary key autoincrement, 
                name text mandatory, 
                address text(100), 
                salary float, 
                age integer mandatory);'''

def create_db(db_name):
    try:
        open(db_name)
    except IOError:
        print("DB not found. Creating...")
        sqlite3.connect(db_name)
        print('DB created')

def create_table(db_name, sql_statement):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    try:
        cur.execute(sql_statement)
        cur.close()
    except Exception as e :
        print(e)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlparse(self.path).path == '/':
            self.do_calc()
        elif urlparse(self.path).path == '/users/':
            self.do_get_user()
        else:
            self.do_notfound()

    def do_POST(self):
        if urlparse(self.path).path == '/users/':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            try:
                json_data = json.loads(data)
                if self.validate_format(json_data):
                    print('JSON format is valid, continuing...')
                    if self.validate_name(json_data):
                        print('Adding new DB entry...')
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        json_data['id'] = self.db_insert(json_data)
                        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                        result = json.dumps({'status': 'ok', 'result': json_data, 'date': date}, indent=2)
                        self.send_response_only(200)
                        self.end_headers()
                        self.wfile.write(bytes(result, 'utf-8'))
                        print('Done')
                    else:
                        self.error_message_format = '\n{\n"status": "error", \n"reason": "The name %s already in database."\n}\n' %(json_data['name'])
                        self.send_error(400, explain='Name already in DB\n')
                else:
                    self.error_message_format = '\n{\n"status": "error", \n"reason": "Invalid JSON data given"\n}\n'
                    self.send_error(400, explain='Invalid JSON data.\n')
            except Exception as e:
                self.error_message_format = '\n{\n"status": "error", \n"reason": "%s"\n}\n' %(e)
                self.send_error(400, explain='Something went wrong.\n')
        else:
            self.do_notfound()

    def do_calc(self):
        self.error_content_type = 'application/json'
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        try:
            params = parse_qs(urlparse(self.path).query, strict_parsing=True, encoding='utf-8', max_num_fields=3)
            calculation = eval(str(params['a'][0] + params['op'][0] + params['b'][0]))
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            result = json.dumps({'status': 'ok', 'date': date, 'result': calculation}, indent=2)
            self.send_response_only(200,result)
            self.end_headers()
            self.wfile.write(bytes(result, 'utf-8'))
        except ValueError:
            self.error_message_format = '\n{\n"status": "error", \n"reason": "Incorrect parameters count"\n}\n'
            self.send_error(400, explain='Incorrect parameters count. Expected 3.\n')
        except SyntaxError:
            self.error_message_format = '\n{\n"status": "error", \n"reason": "incorrect syntax"\n}\n'
            self.send_error(400, explain='Syntax incorrect. The right syntax is a=5&b=10&op=*. E.g 5 * 10\n')
        except KeyError as e:
            self.error_message_format = '\n{\n"status": "error", \n"reason": "%s not found in query string"\n}\n' %(e)
            self.send_error(400, explain='The right syntax is a, op, b. E.g 5 + 10\n')
        except NameError as e:
            self.error_message_format = '\n{\n"status": "error", \n"reason": "%s"\n}\n' %(e)
            self.send_error(400, explain='Incorrect parameters count. Expected 3.\n')

    def do_notfound(self):
        self.error_content_type = 'application/json'
        self.error_message_format = '\n{\n"status": "error", \n"reason": "Not found"\n}\n'
        self.send_error(404, explain='Path not found\n')

    def do_get_user(self):
        self.error_content_type = 'application/json'
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        try:
            params = parse_qs(urlparse(self.path).query, strict_parsing=True, encoding='utf-8', max_num_fields=2)
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            userdata = self.db_select(params)
            result = json.dumps({'status': 'ok', 'result': userdata, 'date': date}, indent=2)
            #result = '{\n"status": "ok", \n"result": %s, \n"date": %s\n}\n' %(json.dumps(userdata,indent=2), date)
            self.end_headers()
            self.wfile.write(bytes(result, 'utf-8'))
        except Exception as e:
            self.error_message_format = '\n{\n"status": "error", \n"reason": "%s"\n}\n' %(e)
            self.send_error(400, explain='Something went wrong...\n')

    def validate_format(self, json_data):
        try:
            schema = {
                "type" : "object",
                "properties" : {
                    "name" : {"type" : "string"},
                    "address" : {"type" : "string"},
                    "age" : {"type" : "number"},
                    "salary" : {"type" : "number"},
                }
            }
            if jsonschema_validate(json_data, schema) == None:
                print(jsonschema_validate(json_data, schema))
                return True
            else:
                return False
        except Exception:
            return False

    def validate_name(self, properties):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("select count(*) from persons where name=:name", {"name": properties['name']})
        result = cursor.fetchall()
        cursor.close()
        if result[0][0] != 0:
            return False
        else:
            return True

    def db_insert(self, data_to_insert):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO persons(name, address, salary, age) VALUES (?, ?, ?, ?)", list(data_to_insert.values()))
        connection.commit()
        cursor.close()
        return cursor.lastrowid

    def db_select(self, data_to_select):
        connection = sqlite3.connect('users.db')
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        if len(data_to_select) == 2:
            cursor.execute("SELECT * FROM persons WHERE name=? AND id=?", 
                [data_to_select['name'], data_to_select['id']])
        elif len(data_to_select) == 1 and 'id' in data_to_select.keys():
            cursor.execute("SELECT * FROM persons WHERE id=?", data_to_select['id'])
        elif len(data_to_select) == 1 and 'name' in data_to_select.keys():
            cursor.execute("SELECT * FROM persons WHERE id=?", data_to_select['name'])
        values = cursor.fetchone()
        names = values.keys()
        result = dict(zip(names,values))
        cursor.close()
        return result

create_db(db_name)
create_table(db_name, sql_create_table)

with HTTPServer(('', 8000), handler) as server:
    server.serve_forever()
