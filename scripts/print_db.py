#!/usr/bin/env python
import sqlite3
from pathlib import Path

db=Path('centro_control/centro_control.db')
if not db.exists():
	print('DB no encontrada:', db)
	raise SystemExit(0)
conn=sqlite3.connect(str(db))
conn.row_factory=sqlite3.Row
cur=conn.cursor()
print('\nÚltimos uploads:')
for r in cur.execute('SELECT id,nombre_original,nombre_guardado,tipo,filas,columnas,errores,timestamp FROM upload_history ORDER BY id DESC LIMIT 10'):
	print(dict(r))
print('\nÚltimos logs de ejecución:')
for r in cur.execute("SELECT id,upload_id,returncode,timestamp,substr(stdout,1,200) as stdout,substr(stderr,1,200) as stderr FROM execution_log ORDER BY id DESC LIMIT 10"):
	d=dict(r)
	print(d)
print('\nÚltimas alertas:')
for r in cur.execute('SELECT id,upload_id,tipo_alerta,mensaje,valor,comparado_con,timestamp,ack FROM alerts ORDER BY id DESC LIMIT 10'):
	print(dict(r))
conn.close()
