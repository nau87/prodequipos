"""
Genera index.html conectado a la nueva planilla de Google Sheets
que usa LOG_FECHAS como fuente única de datos.

Uso: python gen_sheets_v2.py
"""

SHEET_ID = '1BA44xlhvKIWHMR-l8TJxVXUmfYV-NoHXr3iEdUkQ3hk'

# Script JavaScript que consumirá los datos
js_code = f'''
// === CONFIGURACIÓN ===
const SHEET_ID = '{SHEET_ID}';
const LOG_FECHAS_URL = `https://docs.google.com/spreadsheets/d/${{SHEET_ID}}/gviz/tq?tqx=out:json&sheet=LOG_FECHAS`;
const EQUIPOS_URL = `https://docs.google.com/spreadsheets/d/${{SHEET_ID}}/gviz/tq?tqx=out:json&sheet=Equipos`;

let rawData = [];  // Datos crudos de LOG_FECHAS
let equiposData = []; // Datos de equipos
let currentTorneo = 'APERTURA';
let currentCompetencia = 'LIGA';

// === FETCH DATA ===
async function loadAllData() {{
    try {{
        // Cargar LOG_FECHAS
        const logResponse = await fetch(LOG_FECHAS_URL);
        const logText = await logResponse.text();
        const logJson = JSON.parse(logText.substring(47).slice(0, -2));
        rawData = parseSheetData(logJson);
        
        // Cargar Equipos
        const equiposResponse = await fetch(EQUIPOS_URL);
        const equiposText = await equiposResponse.text();
        const equiposJson = JSON.parse(equiposText.substring(47).slice(0, -2));
        equiposData = parseEquiposData(equiposJson);
        
        console.log('✅ Datos cargados:', rawData.length, 'registros');
        
        renderAll();
    }} catch (error) {{
        console.error('❌ Error cargando datos:', error);
        document.querySelector('.error-overlay').classList.add('show');
    }} finally {{
        document.querySelector('.loading-overlay').classList.add('hidden');
    }}
}}

// === PARSE SHEET DATA ===
function parseSheetData(json) {{
    const rows = json.table.rows;
    const data = [];
    
    for (let i = 0; i < rows.length; i++) {{
        const row = rows[i].c;
        if (!row[0] || !row[0].v) continue; // Skip empty rows
        
        data.push({{
            jugador: row[0]?.v || '',
            fecha: parseInt(row[1]?.v) || 0,
            puntos: parseFloat(row[2]?.v) || 0,
            suma: parseFloat(row[3]?.v) || 0,
            torneo: row[4]?.v || '',
            competencia: row[5]?.v || '',
            timestamp: row[6]?.v || '',
            equipo: row[7]?.v || 'LIBRE',
            capitan: row[8]?.v === 'SI',
            idFecha: row[9]?.v || '',
            ideal: parseInt(row[10]?.v) || 0,
            temporada: row[11]?.v || '2026'
        }});
    }}
    
    return data;
}}

function parseEquiposData(json) {{
    const rows = json.table.rows;
    const equipos = [];
    
    for (let i = 0; i < rows.length; i++) {{
        const row = rows[i].c;
        if (!row[0] || !row[0].v) continue;
        
        equipos.push({{
            jugador: row[0]?.v || '',
            equipo: row[1]?.v || 'LIBRE',
            modo: row[2]?.v || null
        }});
    }}
    
    return equipos;
}}

// === FILTROS ===
function filterData(torneo = null, competencia = null) {{
    return rawData.filter(item => {{
        if (torneo && item.torneo !== torneo) return false;
        if (competencia && item.competencia !== competencia) return false;
        return true;
    }});
}}

// === CALCULAR TABLA DE POSICIONES ===
function calcularTabla(torneo, competencia) {{
    const filtered = filterData(torneo, competencia);
    const jugadores = {{}};
    
    filtered.forEach(item => {{
        if (!jugadores[item.jugador]) {{
            jugadores[item.jugador] = {{
                jugador: item.jugador,
                equipo: item.equipo,
                capitan: item.capitan,
                fechasJugadas: 0,
                puntosTotal: 0,
                puntosReal: 0, // Sin bonificación de capitán
                fechaDetalles: []
            }};
        }}
        
        const j = jugadores[item.jugador];
        j.fechasJugadas++;
        j.puntosTotal += item.suma;
        j.puntosReal += item.puntos;
        j.fechaDetalles.push({{
            fecha: item.fecha,
            puntos: item.puntos,
            suma: item.suma,
            ideal: item.ideal
        }});
    }});
    
    // Convertir a array y ordenar
    let tabla = Object.values(jugadores);
    tabla.sort((a, b) => b.puntosTotal - a.puntosTotal);
    
    // Asignar posiciones
    let pos = 1;
    tabla.forEach((j, i) => {{
        if (i > 0 && tabla[i-1].puntosTotal === j.puntosTotal) {{
            j.posicion = tabla[i-1].posicion;
            j.empate = true;
        }} else {{
            j.posicion = pos;
            j.empate = false;
        }}
        pos++;
    }});
    
    return tabla;
}}

// === CALCULAR EQUIPO IDEAL ===
function calcularEquipoIdeal(torneo, competencia) {{
    const filtered = filterData(torneo, competencia);
    const jugadores = {{}};
    
    filtered.forEach(item => {{
        if (!jugadores[item.jugador]) {{
            jugadores[item.jugador] = {{
                jugador: item.jugador,
                equipo: item.equipo,
                vecesIdeal: 0,
                puntosTotal: 0
            }};
        }}
        
        jugadores[item.jugador].vecesIdeal += item.ideal;
        jugadores[item.jugador].puntosTotal += item.puntos;
    }});
    
    let ideal = Object.values(jugadores);
    ideal.sort((a, b) => b.vecesIdeal - a.vecesIdeal || b.puntosTotal - a.puntosTotal);
    
    return ideal.slice(0, 11); // Top 11
}}

// === CALCULAR RANKING ANUAL ===
function calcularRankingAnual() {{
    const torneos = ['APERTURA', 'CLAUSURA', 'PROVINCIAL', 'PRE TEMPORADA', 'POST TEMPORADA', 'MUNDIAL'];
    const jugadores = {{}};
    
    torneos.forEach(torneo => {{
        const tabla = calcularTabla(torneo, 'LIGA');
        tabla.forEach(j => {{
            if (!jugadores[j.jugador]) {{
                jugadores[j.jugador] = {{
                    jugador: j.jugador,
                    equipo: j.equipo,
                    torneos: {{}},
                    totalPuntos: 0,
                    totalFechas: 0
                }};
            }}
            
            jugadores[j.jugador].torneos[torneo] = j.puntosTotal;
            jugadores[j.jugador].totalPuntos += j.puntosTotal;
            jugadores[j.jugador].totalFechas += j.fechasJugadas;
        }});
    }});
    
    let ranking = Object.values(jugadores);
    ranking.sort((a, b) => b.totalPuntos - a.totalPuntos);
    
    return ranking;
}}

// === RENDER FUNCIONES ===
function renderTabla(torneo, competencia) {{
    const tabla = calcularTabla(torneo, competencia);
    const tbody = document.querySelector('#tabla-tbody');
    
    tbody.innerHTML = tabla.map(j => `
        <tr>
            <td class="c">
                <div class="rank-num">${{j.posicion}}</div>
            </td>
            <td>
                <div class="team-pill">
                    <div class="team-avatar" style="background: ${{getTeamColor(j.equipo)}}">
                        ${{j.jugador.charAt(0)}}
                    </div>
                    <span class="team-name">${{j.jugador}}</span>
                </div>
            </td>
            <td>${{j.equipo}}</td>
            <td class="c">${{j.fechasJugadas}}</td>
            <td class="c">
                <span class="pts ${{j.puntosTotal > 50 ? 'pts-hi' : 'pts-lo'}}">${{j.puntosTotal}}</span>
            </td>
            <td class="c">
                <button class="btn-expand" onclick="toggleDetail(this)">
                    Ver <i class="fas fa-chevron-down"></i>
                </button>
            </td>
        </tr>
        <tr class="detail-row">
            <td colspan="6">
                <div class="detail-inner">
                    ${{renderDetalleJugador(j.fechaDetalles)}}
                </div>
            </td>
        </tr>
    `).join('');
}}

function renderDetalleJugador(fechas) {{
    return `
        <table>
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th class="c">Puntos</th>
                    <th class="c">Suma</th>
                    <th class="c">Ideal</th>
                </tr>
            </thead>
            <tbody>
                ${{fechas.map(f => `
                    <tr>
                        <td>Fecha ${{f.fecha}}</td>
                        <td class="c">${{f.puntos}}</td>
                        <td class="c">${{f.suma}}</td>
                        <td class="c">${{f.ideal ? '⚽' : '-'}}</td>
                    </tr>
                `).join('')}}
            </tbody>
        </table>
    `;
}}

function renderEquipoIdeal(torneo, competencia) {{
    const ideal = calcularEquipoIdeal(torneo, competencia);
    const container = document.querySelector('#ideal-list');
    
    container.innerHTML = ideal.map((j, i) => `
        <div class="ideal-list-item">
            <div class="ideal-list-num">${{i + 1}}</div>
            <div class="ideal-list-info">
                <div class="ideal-list-name">${{j.jugador}}</div>
                <div class="ideal-list-team">${{j.equipo}}</div>
            </div>
            <div class="ideal-list-pts">${{j.vecesIdeal}}</div>
        </div>
    `).join('');
}}

function renderRankingAnual() {{
    const ranking = calcularRankingAnual();
    const container = document.querySelector('#ranking-anual');
    
    container.innerHTML = `
        <div class="anual-list">
            ${{ranking.map((j, i) => `
                <div class="anual-row pos-${{i + 1}}">
                    <div class="ar-rank">
                        <div class="rank-num">${{i + 1}}</div>
                    </div>
                    <div class="ar-team">
                        <div class="team-avatar" style="background: ${{getTeamColor(j.equipo)}}">
                            ${{j.jugador.charAt(0)}}
                        </div>
                        <div>
                            <div class="ar-name">${{j.jugador}}</div>
                            <div class="ar-sub">${{j.equipo}}</div>
                        </div>
                    </div>
                    <div class="ar-total">
                        <div class="tv">${{j.totalPuntos}}</div>
                        <div class="tl">TOTAL</div>
                    </div>
                </div>
            `).join('')}}
        </div>
    `;
}}

function renderAll() {{
    renderTabla(currentTorneo, currentCompetencia);
    renderEquipoIdeal(currentTorneo, currentCompetencia);
    renderRankingAnual();
}}

// === UTILIDADES ===
function getTeamColor(equipo) {{
    const colors = {{
        'MONTRE': '#e74c3c',
        'CERRAJERIA OMARCITO': '#3498db',
        'FERRERO HNOS': '#f39c12',
        'CABRON': '#9b59b6',
        'AGENCIA 133': '#1abc9c',
        'PERCHA FC': '#e67e22',
        'EL GRAN DT': '#16a085',
        'FORTYUS GYM': '#d35400',
        'RADIO UNO': '#c0392b',
        'TRIBUNERAS': '#8e44ad',
        'INSIDE TRENEL': '#27ae60',
        'A LO DE JUAN': '#2980b9',
        'LIBRE': '#95a5a6'
    }};
    return colors[equipo] || '#34495e';
}}

function toggleDetail(btn) {{
    const detailRow = btn.closest('tr').nextElementSibling;
    detailRow.classList.toggle('open');
    btn.classList.toggle('open');
}}

// === TABS ===
function switchTab(tabName) {{
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    
    event.target.classList.add('active');
    document.querySelector(`#${{tabName}}`).classList.add('active');
}}

// === INIT ===
document.addEventListener('DOMContentLoaded', () => {{
    loadAllData();
}});
'''

# Crear el HTML completo (reutilizando el CSS del actual index.html)
# Leer el index.html actual para obtener el CSS
try:
    with open('index.html', 'r', encoding='utf-8') as f:
        current_html = f.read()
        
    # Extraer solo la parte de CSS
    css_start = current_html.find('<style>')
    css_end = current_html.find('</style>') + 8
    css_section = current_html[css_start:css_end]
except:
    css_section = "<!-- CSS no encontrado -->"

html_output = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Prode Equipos</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
{css_section}
</head>
<body>

<!-- LOADING -->
<div class="loading-overlay">
  <div class="loading-ball">⚽</div>
  <div class="spinner"></div>
  <div class="loading-text">Cargando datos del prode...</div>
</div>

<!-- ERROR -->
<div class="error-overlay">
  <h2>⚠️ Error al cargar los datos</h2>
  <p>No se pudieron cargar los datos de Google Sheets. Verifica tu conexión e intenta nuevamente.</p>
</div>

<!-- HEADER -->
<div class="header">
  <div class="header-top">
    <div class="header-ball">⚽</div>
    <div class="header-title">
      <h1>Prode Equipos</h1>
      <p>Temporada 2026</p>
    </div>
  </div>
  
  <div class="header-stats">
    <div class="hstat">
      <div class="val" id="total-jugadores">0</div>
      <div class="lbl">Jugadores</div>
    </div>
    <div class="hstat">
      <div class="val" id="total-fechas">0</div>
      <div class="lbl">Fechas</div>
    </div>
    <div class="hstat">
      <div class="val" id="total-equipos">0</div>
      <div class="lbl">Equipos</div>
    </div>
  </div>
  
  <!-- TABS -->
  <div class="tabs-wrap">
    <button class="tab active" onclick="switchTab('tabla')">📊 Tabla</button>
    <button class="tab" onclick="switchTab('ideal')">⚽ Equipo Ideal</button>
    <button class="tab" onclick="switchTab('anual')">🏆 Ranking Anual</button>
  </div>
</div>

<!-- CONTENT -->
<div class="content">
  
  <!-- TABLA -->
  <div class="section active" id="tabla">
    <div class="card">
      <div class="card-head">
        <div class="card-head-icon">📊</div>
        <h2>Tabla de Posiciones - Apertura 2026</h2>
      </div>
      <div class="search-wrap">
        <div class="search-wrap-inner">
          <i class="fas fa-search search-icon"></i>
          <input type="text" class="search-input" placeholder="Buscar jugador o equipo..." onkeyup="buscarJugador(this.value)">
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th class="c">Pos</th>
              <th>Jugador</th>
              <th>Equipo</th>
              <th class="c">FJ</th>
              <th class="c">Puntos</th>
              <th class="c">Detalle</th>
            </tr>
          </thead>
          <tbody id="tabla-tbody">
            <!-- Generado por JS -->
          </tbody>
        </table>
      </div>
    </div>
  </div>
  
  <!-- EQUIPO IDEAL -->
  <div class="section" id="ideal">
    <div class="card">
      <div class="card-head">
        <div class="card-head-icon">⚽</div>
        <h2>Equipo Ideal - Apertura 2026</h2>
      </div>
      <div class="ideal-list-container">
        <div class="ideal-list" id="ideal-list">
          <!-- Generado por JS -->
        </div>
      </div>
    </div>
  </div>
  
  <!-- RANKING ANUAL -->
  <div class="section" id="anual">
    <div class="card">
      <div class="card-head">
        <div class="card-head-icon">🏆</div>
        <h2>Ranking Anual 2026</h2>
        <span>Acumulado de todos los torneos</span>
      </div>
      <div id="ranking-anual">
        <!-- Generado por JS -->
      </div>
    </div>
  </div>
  
</div>

<script>
{js_code}
</script>

</body>
</html>
'''

# Guardar el archivo
with open('index_v2.html', 'w', encoding='utf-8') as f:
    f.write(html_output)

print("✅ Archivo 'index_v2.html' generado exitosamente!")
print(f"📊 Conectado a Google Sheets ID: {SHEET_ID}")
print("\nPróximos pasos:")
print("1. Abre index_v2.html en tu navegador para probar")
print("2. Si funciona bien, renombra index_v2.html a index.html")
print("3. Los datos se actualizan automáticamente desde Google Sheets")
