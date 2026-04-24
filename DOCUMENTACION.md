# 📊 Sistema Prode v2.0 - Documentación

## ¿Qué cambió?

### ✅ Sistema Anterior
- Múltiples hojas con datos duplicados
- Difícil de mantener y actualizar
- Había que actualizar varias hojas manualmente

### 🚀 Sistema Nuevo (LOG_FECHAS)
- **Una sola hoja de entrada: LOG_FECHAS**
- Todo se calcula automáticamente desde ahí
- Fácil de escalar y agregar nuevos torneos
- Menos errores, más eficiente

---

## 📋 Estructura de LOG_FECHAS

La hoja **LOG_FECHAS** es el corazón del sistema. Cada fila representa un registro de puntos de un jugador en una fecha específica.

### Columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| **JUGADOR** | Nombre del jugador | "HORACIO BELTRAMINO" |
| **FECHA** | Número de fecha | 3 |
| **PUNTOS** | Puntos obtenidos | 8 |
| **SUMA** | Puntos con bonif. capitán | 8 o 16 |
| **TORNEO** | Torneo actual | "APERTURA" |
| **COMPETENCIA** | Tipo de competencia | "LIGA" o "COPA" |
| **TIMESTAMP** | Fecha y hora del registro | "20/12/2024 11:15:00" |
| **EQUIPO** | Equipo del jugador | "MONTRE" |
| **CAPITAN** | Es capitán? | "SI" o "NO" |
| **ID_FECHA** | ID único del registro | "HORACIO_2026_APERTURA_LIGA_3" |
| **IDEAL** | Está en equipo ideal? | 1 o 0 |
| **TEMPORADA** | Año | "2026" |

---

## 🎯 Cómo Usar el Sistema

### 1. Cargar Datos (Google Sheets)

Solo necesitas agregar filas a **LOG_FECHAS**. Por ejemplo, cuando termina una fecha:

```
JUGADOR: "NAHUEL MENDEZ"
FECHA: 5
PUNTOS: 12
SUMA: 24 (si es capitán) o 12 (si no)
TORNEO: "APERTURA"
COMPETENCIA: "LIGA"
EQUIPO: "CABRON"
CAPITAN: "SI"
IDEAL: 1 (si está en el ideal de la fecha)
```

### 2. La Web Calcula Automáticamente:

- **Tabla de Posiciones**: Por torneo y competencia
- **Equipo Ideal**: Los jugadores que más veces estuvieron en el ideal
- **Ranking Anual**: Suma de todos los torneos
- **Estadísticas**: Fechas jugadas, puntos promedio, etc.

---

## 🔧 Archivos del Proyecto

### Nuevos:
- **`gen_sheets_v2.py`**: Script que genera el HTML nuevo
- **`index_v2.html`**: Web actualizada que consume LOG_FECHAS
- **`analyze_sheets.py`**: Script para analizar la estructura de Sheets

### Mantener:
- **`index.html`**: Tu HTML actual (hacer backup)
- **`sponsors/`**: Carpeta con logos de sponsors

---

## 📊 Cómo Funciona el Código

### 1. Fetch de Datos
```javascript
// La web consulta directamente a Google Sheets
const LOG_FECHAS_URL = 'https://docs.google.com/spreadsheets/d/[ID]/gviz/tq?tqx=out:json&sheet=LOG_FECHAS';

// Parsea los datos
rawData = parseSheetData(logJson);
```

### 2. Filtros
```javascript
// Filtra por torneo y competencia
function filterData(torneo, competencia) {
    return rawData.filter(item => {
        if (torneo && item.torneo !== torneo) return false;
        if (competencia && item.competencia !== competencia) return false;
        return true;
    });
}
```

### 3. Cálculo de Tabla
```javascript
function calcularTabla(torneo, competencia) {
    const filtered = filterData(torneo, competencia);
    const jugadores = {};
    
    // Agrupa por jugador y suma puntos
    filtered.forEach(item => {
        if (!jugadores[item.jugador]) {
            jugadores[item.jugador] = {
                jugador: item.jugador,
                equipo: item.equipo,
                puntosTotal: 0,
                fechasJugadas: 0
            };
        }
        
        jugadores[item.jugador].puntosTotal += item.suma;
        jugadores[item.jugador].fechasJugadas++;
    });
    
    // Ordena por puntos
    return Object.values(jugadores).sort((a, b) => b.puntosTotal - a.puntosTotal);
}
```

### 4. Equipo Ideal
```javascript
function calcularEquipoIdeal(torneo, competencia) {
    const filtered = filterData(torneo, competencia);
    
    // Cuenta cuántas veces cada jugador estuvo en el ideal
    const jugadores = {};
    filtered.forEach(item => {
        jugadores[item.jugador].vecesIdeal += item.ideal;
    });
    
    // Retorna top 11
    return Object.values(jugadores)
        .sort((a, b) => b.vecesIdeal - a.vecesIdeal)
        .slice(0, 11);
}
```

---

## ✨ Ventajas del Nuevo Sistema

### Para Administradores:
✅ Solo cargan datos en **una hoja** (LOG_FECHAS)  
✅ No necesitan actualizar tablas, rankings, etc. manualmente  
✅ Fácil agregar nuevos torneos (solo cambiar columna TORNEO)  
✅ Menos errores humanos

### Para Jugadores:
✅ Datos actualizados en tiempo real  
✅ Ver estadísticas detalladas por fecha  
✅ Histórico completo de su rendimiento  
✅ Equipo ideal calculado automáticamente

### Para Desarrolladores:
✅ Código más limpio y mantenible  
✅ Fácil agregar nuevas funcionalidades  
✅ Sistema escalable (soporta infinitos torneos)  
✅ Separación de datos y lógica

---

## 🚀 Migración Paso a Paso

### Fase 1: Testing (Ahora)
1. ✅ Analizar estructura de LOG_FECHAS
2. ✅ Generar `index_v2.html`
3. 📝 Abrir `index_v2.html` en el navegador
4. 📝 Verificar que muestre correctamente:
   - Tabla de posiciones
   - Equipo ideal
   - Ranking anual

### Fase 2: Ajustes (Si es necesario)
1. Agregar funcionalidades faltantes
2. Ajustar estilos CSS
3. Verificar compatibilidad mobile

### Fase 3: Producción
1. Hacer backup de `index.html` actual
2. Renombrar `index_v2.html` a `index.html`
3. Subir a hosting
4. ✅ ¡Listo!

---

## 📝 Agregar Nuevos Torneos

Es muy simple, solo agrega registros a LOG_FECHAS con el nuevo torneo:

```
JUGADOR: "JUAN PEREZ"
FECHA: 1
PUNTOS: 10
TORNEO: "COPA DE ORO"  ← Nuevo torneo
COMPETENCIA: "COPA"
...resto de datos...
```

La web automáticamente:
- Lo mostrará en las tablas
- Lo incluirá en el ranking anual
- Calculará su equipo ideal

---

## 🔧 Personalización

### Cambiar Colores de Equipos
En `gen_sheets_v2.py`, modifica la función `getTeamColor`:

```javascript
function getTeamColor(equipo) {
    const colors = {
        'MI NUEVO EQUIPO': '#ff6b6b',  ← Agregar aquí
        'MONTRE': '#e74c3c',
        // ...resto
    };
    return colors[equipo] || '#34495e';
}
```

### Agregar Nueva Pestaña
1. Agrega el tab en el HTML:
```html
<button class="tab" onclick="switchTab('mi-seccion')">🎯 Mi Sección</button>
```

2. Agrega la sección:
```html
<div class="section" id="mi-seccion">
    <!-- Tu contenido -->
</div>
```

3. Crea la función de render:
```javascript
function renderMiSeccion() {
    // Tu lógica aquí
}
```

---

## 🆘 Troubleshooting

### "No se cargan los datos"
- ✅ Verifica que la planilla sea pública (cualquiera con el link puede ver)
- ✅ Chequea la consola del navegador (F12) para ver errores
- ✅ Verifica que el SHEET_ID sea correcto

### "Los puntos no coinciden"
- Verifica que la columna SUMA tenga la bonificación de capitán aplicada
- El capitán duplica sus puntos: SUMA = PUNTOS * 2 si CAPITAN = "SI"

### "Falta un jugador"
- Verifica que tenga al menos un registro en LOG_FECHAS
- Chequea que el nombre esté escrito exactamente igual en todos los registros

---

## 📞 Soporte

¿Dudas? ¿Problemas? ¿Ideas?
- Revisa esta documentación
- Chequea el código en `gen_sheets_v2.py`
- Contacta al equipo de desarrollo

---

**🎉 ¡Disfruta del nuevo sistema!**
