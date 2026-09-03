#!/usr/bin/env python
"""Resetear/crear usuario admin en la base de datos local.

Uso:
  python scripts/reset_admin.py --username admin --password MiNuevaPass123
Si no se proporciona --password se solicitará por prompt (oculto).

Este script usa las funciones de centro_control.db y generate_password_hash
para crear o actualizar el usuario indicado con is_admin=True.
"""
from __future__ import annotations

import argparse
import getpass
import sys

try:
	from werkzeug.security import generate_password_hash
except Exception:
	print('Error: falta werkzeug. Instala dependencias: pip install werkzeug')
	raise

try:
	# importar el módulo db del paquete centro_control
	from centro_control import db
except Exception as exc:
	print('Error importando centro_control.db:', exc)
	sys.exit(1)


def main() -> None:
	p = argparse.ArgumentParser(description='Reset/create admin user in local DB')
	p.add_argument('--username', '-u', default='frontera', help='Nombre de usuario (por defecto: frontera)')
	p.add_argument('--password', '-p', default='living', help='Nueva contraseña (por defecto: living)')
	args = p.parse_args()

	username = args.username
	password = args.password
	if not password:
		password = getpass.getpass('Nueva contraseña para %s: ' % username)
		if not password:
			print('Contraseña vacía cancelada')
			sys.exit(1)

	ph = generate_password_hash(password)

	try:
		existing = db.get_user_by_username(username)
	except Exception as exc:
		print('Error accediendo a la base de datos:', exc)
		sys.exit(1)

	if existing:
		try:
			db.update_user_password(username, ph)
			print(f'Contraseña actualizada para usuario "{username}"')
		except Exception as exc:
			print('Error al actualizar contraseña:', exc)
			sys.exit(1)
	else:
		try:
			db.create_user(username, ph, is_admin=True)
			print(f'Usuario "{username}" creado con privilegios admin')
		except Exception as exc:
			print('Error al crear usuario:', exc)
			sys.exit(1)


if __name__ == '__main__':
	main()
