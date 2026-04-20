from flask import Flask, render_template, request
import paramiko
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.config['ENV'] = "Development"
app.config['DEBUG'] = True

INSTANCE_IP = "63.33.189.35"
KEY_FILE = "newkey.pem"
REMOTE_CMD = "python3 ~/wiki.py"

# cache config
DB_HOST = "63.33.189.35"
DB_PORT = 7888
DB_NAME = "MYDB"
DB_USER = "root"
DB_PASSWORD = "mypassword"


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def get_from_cache(query):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT result FROM wiki_cache WHERE query = %s",
            (query,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    except Error as e:
        print("Database read error:", e)
        return None

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def save_to_cache(query, result):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT IGNORE INTO wiki_cache (query, result) VALUES (%s, %s)",
            (query, result)
        )
        conn.commit()
        print("Saved to cache:", query)

    except Error as e:
        print("Database write error:", e)

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def run_remote_wiki_search(query, page=1):
    client = None

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        key = paramiko.RSAKey.from_private_key_file(KEY_FILE)
        client.connect(INSTANCE_IP, username="ubuntu", pkey=key)

        command = f'{REMOTE_CMD} "{query}" {page}'
        stdin, stdout, stderr = client.exec_command(command)
        stdin.close()

        result = stdout.read().decode().strip()
        _ = stderr.read()  # consume stderr and ignore warnings

        return result if result else "No results found."

    except Exception as e:
        print("SSH error:", e)
        return "Error retrieving Wikipedia result."

    finally:
        if client:
            client.close()


@app.route('/')
@app.route('/wikiHome')
def wikihome():
    return render_template("wikihome.html", result="", search="", page=1)


@app.route('/searchBar', methods=['GET', 'POST'])
def search():
    query = request.values.get('search', '').strip()
    page = int(request.values.get('page', 1))
    result = ""

    if not query:
        return render_template(
            "wikihome.html",
            search="",
            result="Please enter a search term.",
            page=1
        )

    normalized_query = query.lower()

    # Cache only first page
    if page == 1:
        cached_result = get_from_cache(normalized_query)
    else:
        cached_result = None

    if cached_result:
        print("CACHE HIT:", normalized_query)
        result = cached_result
    else:
        print("CACHE MISS:", normalized_query)
        result = run_remote_wiki_search(query, page)

        if page == 1 and result and result != "Error retrieving Wikipedia result.":
            save_to_cache(normalized_query, result)

    return render_template(
        "wikihome.html",
        search=query,
        result=result,
        page=page
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)