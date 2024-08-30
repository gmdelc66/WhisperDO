import sqlite3

# Ruta al archivo de la base de datos en el contenedor
db_path = '/app/backend/data/webui.db'

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Consultar las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Consultar datos de una tabla específica
# Cambia 'your_table_name' al nombre real de la tabla que deseas consultar
cursor.execute("SELECT * FROM your_table_name")
rows = cursor.fetchall()
print("Rows:", rows)

# Cerrar la conexión
conn.close()
