from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Tuple

DB_PATH = Path(__file__).resolve().parent / 'centro_control.db'


def get_connection() -> sqlite3.Connection:
	conn = sqlite3.connect(str(DB_PATH), timeout=30)
	conn.row_factory = sqlite3.Row
	return conn


def init_db() -> None:
	DB_PATH.parent.mkdir(parents=True, exist_ok=True)
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		'''
		CREATE TABLE IF NOT EXISTS upload_history (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			nombre_original TEXT,
			nombre_guardado TEXT,
			tipo TEXT,
			filas INTEGER,
			columnas INTEGER,
			errores TEXT,
			timestamp TEXT
		)
		'''
	)
	conn.commit()
	# tabla para logs de ejecución vinculados a una subida
	cur.execute(
		'''
		CREATE TABLE IF NOT EXISTS execution_log (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			upload_id INTEGER,
			stdout TEXT,
			stderr TEXT,
			returncode INTEGER,
			timestamp TEXT,
			FOREIGN KEY(upload_id) REFERENCES upload_history(id)
		)
		'''
	)
	conn.commit()
	conn.close()

	# tabla para auditoría de descargas
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		'''
		CREATE TABLE IF NOT EXISTS download_log (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			upload_id INTEGER,
			filename TEXT,
			client_ip TEXT,
			user_agent TEXT,
			timestamp TEXT,
			FOREIGN KEY(upload_id) REFERENCES upload_history(id)
		)
		'''
	)
	conn.commit()
	conn.close()

	# tabla para alertas generadas automáticamente
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		'''
		CREATE TABLE IF NOT EXISTS alerts (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			upload_id INTEGER,
			tipo_alerta TEXT,
			mensaje TEXT,
			valor TEXT,
			comparado_con TEXT,
			timestamp TEXT,
			ack INTEGER DEFAULT 0,
			FOREIGN KEY(upload_id) REFERENCES upload_history(id)
		)
		'''
	)
	conn.commit()
	conn.close()


def insert_upload(nombre_original: str, nombre_guardado: str, tipo: str | None, filas: int, columnas: int, errores: str | None, timestamp: str) -> int:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		'INSERT INTO upload_history (nombre_original, nombre_guardado, tipo, filas, columnas, errores, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)',
		(nombre_original, nombre_guardado, tipo, filas, columnas, errores or '', timestamp),
	)
	conn.commit()
	rowid = cur.lastrowid
	conn.close()
	return rowid


def get_uploads(limit: int = 100) -> List[sqlite3.Row]:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('SELECT * FROM upload_history ORDER BY id DESC LIMIT ?', (limit,))
	rows = cur.fetchall()
	conn.close()
	return rows


def get_upload_by_guardado(nombre_guardado: str) -> sqlite3.Row | None:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('SELECT * FROM upload_history WHERE nombre_guardado = ? ORDER BY id DESC LIMIT 1', (nombre_guardado,))
	row = cur.fetchone()
	conn.close()
	return row


def insert_execution_log(upload_id: int | None, stdout: str, stderr: str, returncode: int, timestamp: str) -> int:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		'INSERT INTO execution_log (upload_id, stdout, stderr, returncode, timestamp) VALUES (?, ?, ?, ?, ?)',
		(upload_id, stdout or '', stderr or '', returncode, timestamp),
	)
	conn.commit()
	rowid = cur.lastrowid
	conn.close()
	return rowid


def get_execution_logs_for_upload(upload_id: int) -> List[sqlite3.Row]:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('SELECT * FROM execution_log WHERE upload_id = ? ORDER BY id DESC', (upload_id,))
	rows = cur.fetchall()
	conn.close()
	return rows


def get_upload_by_id(upload_id: int) -> sqlite3.Row | None:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('SELECT * FROM upload_history WHERE id = ? LIMIT 1', (upload_id,))
	row = cur.fetchone()
	conn.close()
	return row


def init_user_table() -> None:
	"""Crear tabla users si no existe."""
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		'''
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT UNIQUE,
			password_hash TEXT,
			is_admin INTEGER DEFAULT 0
		)
		'''
	)
	conn.commit()
	conn.close()


def create_user(username: str, password_hash: str, is_admin: bool = False) -> int:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)', (username, password_hash, 1 if is_admin else 0))
	conn.commit()
	rowid = cur.lastrowid
	conn.close()
	return rowid


def get_user_by_username(username: str) -> sqlite3.Row | None:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('SELECT * FROM users WHERE username = ? LIMIT 1', (username,))
	row = cur.fetchone()
	conn.close()
	return row


def list_users(limit: int = 100) -> list:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('SELECT id, username, is_admin FROM users ORDER BY id DESC LIMIT ?', (limit,))
	rows = cur.fetchall()
	conn.close()
	return rows


def update_user_password(username: str, password_hash: str) -> None:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('UPDATE users SET password_hash = ? WHERE username = ?', (password_hash, username))
	conn.commit()
	conn.close()


def delete_user(username: str) -> None:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('DELETE FROM users WHERE username = ?', (username,))
	conn.commit()
	conn.close()


def delete_execution_logs_for_upload(upload_id: int) -> None:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('DELETE FROM execution_log WHERE upload_id = ?', (upload_id,))
	conn.commit()
	conn.close()


def delete_upload(upload_id: int) -> None:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('DELETE FROM upload_history WHERE id = ?', (upload_id,))
	conn.commit()
	conn.close()


def insert_alert(upload_id: int | None, tipo_alerta: str, mensaje: str, valor: str | None, comparado_con: str | None, timestamp: str) -> int:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		'INSERT INTO alerts (upload_id, tipo_alerta, mensaje, valor, comparado_con, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
		(upload_id, tipo_alerta, mensaje, valor or '', comparado_con or '', timestamp),
	)
	conn.commit()
	rowid = cur.lastrowid
	conn.close()
	return rowid


def get_unacknowledged_alerts(limit: int = 100) -> list:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('SELECT * FROM alerts WHERE ack = 0 ORDER BY id DESC LIMIT ?', (limit,))
	rows = cur.fetchall()
	conn.close()
	return rows


def get_alerts_for_upload(upload_id: int) -> list:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('SELECT * FROM alerts WHERE upload_id = ? ORDER BY id DESC', (upload_id,))
	rows = cur.fetchall()
	conn.close()
	return rows


def acknowledge_alert(alert_id: int) -> None:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('UPDATE alerts SET ack = 1 WHERE id = ?', (alert_id,))
	conn.commit()
	conn.close()


def insert_download_log(upload_id: int | None, filename: str, client_ip: str | None, user_agent: str | None, timestamp: str) -> int:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		'INSERT INTO download_log (upload_id, filename, client_ip, user_agent, timestamp) VALUES (?, ?, ?, ?, ?)',
		(upload_id, filename or '', client_ip or '', user_agent or '', timestamp),
	)
	conn.commit()
	rowid = cur.lastrowid
	conn.close()
	return rowid


def get_downloads_for_upload(upload_id: int) -> list:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('SELECT * FROM download_log WHERE upload_id = ? ORDER BY id DESC', (upload_id,))
	rows = cur.fetchall()
	conn.close()
	return rows
