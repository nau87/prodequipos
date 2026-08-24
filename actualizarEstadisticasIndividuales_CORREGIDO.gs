function actualizarEstadisticasIndividuales() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var hojaLog = ss.getSheetByName('LOG_FECHAS');
  var hojaData = ss.getSheetByName('DATA_TOTAL');
  var hojaEst = ss.getSheetByName('ESTADISTICAS_INDIVIDUALES');
  var hojaEquipos = ss.getSheetByName('Equipos');

  if (!hojaLog || !hojaData || !hojaEst || !hojaEquipos) {
    throw new Error("Faltan hojas");
  }

  var fechaActual = Number(hojaData.getRange('E1').getValue());
  var temporadaActual = Number(hojaData.getRange('G1').getValue());
  var torneoActual = (hojaData.getRange('H1').getValue() || "").toString().trim().toUpperCase();
  var competenciaActual = (hojaData.getRange('I1').getValue() || "").toString().trim().toUpperCase();

  var datosLog = hojaLog.getDataRange().getValues();

  // === LEER EQUIPOS ACTUALES DESDE HOJA "Equipos" ===
  var equiposActuales = {};
  var datosEquipos = hojaEquipos.getDataRange().getValues();
  
  for (var e = 1; e < datosEquipos.length; e++) {
    var jugadorEq = (datosEquipos[e][0] || "").toString().trim().toUpperCase();
    var equipoEq = (datosEquipos[e][1] || "LIBRE").toString().trim().toUpperCase();
    
    if (jugadorEq) {
      equiposActuales[jugadorEq] = equipoEq;
    }
  }

  // === RESPALDAR PUESTOS ACTUALES (se convierten en puestos anteriores) Y DATOS MANUALES ===
  var puestosAnterioresGuardados = {};
  var datosManualesGuardados = {};
  var lrEst = hojaEst.getLastRow();
  
  if (lrEst > 1) {
    var todoEst = hojaEst.getRange(2, 1, lrEst - 1, 14).getValues();
    for (var j = 0; j < todoEst.length; j++) {
      var jugExistente = (todoEst[j][0] || "").toString().trim().toUpperCase();
      if (jugExistente) {
        // Guardar el PUESTO ACTUAL (columna B, índice 1) como el nuevo PUESTO ANTERIOR
        puestosAnterioresGuardados[jugExistente] = todoEst[j][1];
        
        // Guardar datos manuales de columnas L, M, N
        datosManualesGuardados[jugExistente] = {
          colL: todoEst[j][11],
          colM: todoEst[j][12],
          colN: todoEst[j][13]
        };
      }
    }
  }

  // === CALCULAR ESTADÍSTICAS GLOBALES HISTÓRICAS (sin filtrar por torneo/fecha) ===
  var statsJug = {};

  for (var i = 1; i < datosLog.length; i++) {
    var jugador = (datosLog[i][0] || "").toString().trim().toUpperCase();
    var puntos = Number(datosLog[i][2]) || 0;
    var ideal = Number(datosLog[i][10]) || 0;

    if (!jugador) continue;

    if (!statsJug[jugador]) {
      statsJug[jugador] = {
        mejor: 0,
        ideal: 0,
        hist: 0,
        fechas: 0
      };
    }

    statsJug[jugador].hist += puntos;
    statsJug[jugador].fechas += 1;
    statsJug[jugador].ideal += ideal;

    if (puntos > statsJug[jugador].mejor) {
      statsJug[jugador].mejor = puntos;
    }
  }

  // === CONSTRUIR RANKING DENSO ACTUAL BASADO EN PUNTOS HISTÓRICOS TOTALES ===
  var puntosHistoricos = {};
  Object.keys(statsJug).forEach(function(jugador) {
    puntosHistoricos[jugador] = statsJug[jugador].hist;
  });
  
  var rankingActual = construirRankingDenso(puntosHistoricos);

  // === ARMAR FILAS CON PUESTO ANTERIOR GUARDADO Y PUESTO ACTUAL NUEVO ===
  var filas = [];

  Object.keys(statsJug).forEach(function(jugador) {
    var s = statsJug[jugador];

    // Puesto actual: calculado según ranking histórico total
    var puestoActual = rankingActual[jugador] || (Object.keys(rankingActual).length + 1);
    
    // Puesto anterior: el que tenía ANTES de esta ejecución (o el actual si es nuevo jugador)
    var puestoAnterior = puestosAnterioresGuardados[jugador] !== undefined 
      ? puestosAnterioresGuardados[jugador] 
      : puestoActual;

    // Equipo actual desde la hoja Equipos
    var equipoActual = equiposActuales[jugador] || "LIBRE";

    // Datos manuales
    var manual = datosManualesGuardados[jugador] || { colL: "", colM: "", colN: "" };

    filas.push([
      jugador,           // A: JUGADOR
      puestoActual,      // B: PUESTO ACTUAL (nuevo)
      puestoAnterior,    // C: PUESTO ANTERIOR (el que tenía antes)
      s.mejor,           // D: MEJOR FECHA
      s.ideal,           // E: VECES IDEAL
      equipoActual,      // F: EQUIPO
      torneoActual,      // G: TORNEO ACTUAL (para referencia)
      s.hist,            // H: PUNTOS HISTÓRICOS
      Number((s.hist / s.fechas).toFixed(2)), // I: PROMEDIO
      puestoActual,      // J: PUESTO GLOBAL (mismo que puesto actual)
      s.fechas,          // K: CANTIDAD FECHAS
      manual.colL,       // L: (manual)
      manual.colM,       // M: (manual)
      manual.colN        // N: (manual)
    ]);
  });

  // === ORDENAR POR PUNTOS HISTÓRICOS (mayor a menor) ===
  filas.sort(function(a, b) {
    return b[7] - a[7] || a[0].localeCompare(b[0]);
  });

  // === VOLCAR DATOS A LA HOJA ===
  if (lrEst > 1) {
    hojaEst.getRange(2, 1, lrEst - 1, 14).clearContent();
  }

  if (filas.length > 0) {
    hojaEst.getRange(2, 1, filas.length, 14).setValues(filas);
  }

  return "Estadísticas actualizadas correctamente";
}

function construirRankingDenso(puntosPorJugador) {
  var lista = [];
  Object.keys(puntosPorJugador).forEach(function(jugador) {
    lista.push({ nombre: jugador, pts: puntosPorJugador[jugador] });
  });

  lista.sort(function(a, b) { return b.pts - a.pts; });

  var rankings = {};
  var puesto = 0;
  var ultimoPuntaje = -1;

  for (var i = 0; i < lista.length; i++) {
    if (lista[i].pts !== ultimoPuntaje) {
       puesto++;
       ultimoPuntaje = lista[i].pts;
    }
    rankings[lista[i].nombre] = puesto;
  }
  return rankings;
}
