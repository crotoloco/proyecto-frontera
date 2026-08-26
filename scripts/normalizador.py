"""Normaliza ventas de Odoo o archivos exportados al formato del proyecto."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pandas as pd


COLUMNAS_REQUERIDAS = (
    'Cliente',
    'Estado',
    'Fecha de creación',
    'Referencia de la orden',
    'Total',
    'Vendedor',
)


def _nombre_relacionado(valor: Any) -> str:
    """Convierte un many2one de Odoo ([id, nombre]) en su nombre."""
    if isinstance(valor, (list, tuple)) and len(valor) >= 2:
        return str(valor[1])
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ''
    return str(valor)


def normalizar_ventas(registros: Iterable[dict[str, Any]] | pd.DataFrame) -> pd.DataFrame:
    """Devuelve un DataFrame compatible con el procesamiento CSV existente."""
    df = registros.copy() if isinstance(registros, pd.DataFrame) else pd.DataFrame(registros)
    if df.empty:
        return pd.DataFrame(columns=COLUMNAS_REQUERIDAS)

    renombres = {
        'amount_total': 'Total',
        'partner_id': 'Cliente',
        'date_order': 'Fecha de creación',
        'name': 'Referencia de la orden',
        'user_id': 'Vendedor',
        'state': 'Estado',
    }
    df = df.rename(columns=renombres)

    for columna in ('Cliente', 'Vendedor'):
        if columna in df:
            df[columna] = df[columna].map(_nombre_relacionado)

    if 'Total' in df:
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
    if 'Fecha de creación' in df:
        df['Fecha de creación'] = pd.to_datetime(
            df['Fecha de creación'], errors='coerce'
        ).dt.strftime('%Y-%m-%d %H:%M:%S')

    faltantes = [columna for columna in COLUMNAS_REQUERIDAS if columna not in df]
    if faltantes:
        raise ValueError(f'La fuente no contiene columnas compatibles: {", ".join(faltantes)}')

    return df


def leer_archivo_ventas(ruta: str | Path) -> pd.DataFrame:
    """Lee CSV o Excel y lo normaliza al contrato del proyecto."""
    ruta = Path(ruta)
    if ruta.suffix.lower() == '.xlsx':
        datos = pd.read_excel(ruta)
    else:
        datos = pd.read_csv(ruta, encoding='utf-8-sig')
    return normalizar_ventas(datos)
