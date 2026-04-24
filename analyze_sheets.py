"""
Script para analizar la nueva planilla de Google Sheets
"""
import urllib.request
import json

SHEET_ID = '1BA44xlhvKIWHMR-l8TJxVXUmfYV-NoHXr3iEdUkQ3hk'

# Intentar obtener información de diferentes hojas
def get_sheet_data(gid=0, sheet_name=None):
    if sheet_name:
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet={sheet_name}'
    else:
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&gid={gid}'
    
    try:
        with urllib.request.urlopen(url) as response:
            text = response.read().decode('utf-8')
        # Limpiar el JavaScript wrapper
        json_str = text.replace("/*O_o*/\ngoogle.visualization.Query.setResponse(", "")[:-2]
        data = json.loads(json_str)
        return data
    except Exception as e:
        print(f"Error getting sheet {sheet_name or gid}: {e}")
        return None

# Hojas posibles basadas en el nombre del archivo
sheet_names = [
    'LOGS', 'LOG_FECHAS', 'Jugadores', 'Equipos', 
    'Tabla', 'Posiciones', 'Estadísticas', 'Ranking',
    'APERTURA', 'CLAUSURA', 'ANUAL', 'Ideal'
]

print("=== ANALIZANDO ESTRUCTURA DE LA PLANILLA ===\n")

for name in sheet_names:
    data = get_sheet_data(sheet_name=name)
    if data and data.get('status') == 'ok':
        table = data.get('table', {})
        cols = table.get('cols', [])
        rows = table.get('rows', [])
        
        print(f"\n📊 HOJA: {name}")
        print(f"   Columnas: {len(cols)}")
        print(f"   Filas: {len(rows)}")
        
        # Mostrar encabezados
        headers = [col.get('label', f"Col{col.get('id', '')}") or f"Col{col.get('id', '')}" for col in cols]
        print(f"   Headers: {headers[:10]}...")  # Primeras 10
        
        # Mostrar primeras filas
        if rows:
            print(f"   Primera fila:")
            first_row = rows[0].get('c', [])
            values = [cell.get('v') if cell else None for cell in first_row]
            print(f"   {values[:10]}...")
        
        if len(rows) > 1:
            print(f"   Segunda fila:")
            second_row = rows[1].get('c', [])
            values = [cell.get('v') if cell else None for cell in second_row]
            print(f"   {values[:10]}...")

print("\n\n=== FIN DEL ANÁLISIS ===")
