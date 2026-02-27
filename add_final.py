with open(r'C:\Users\Nahue\Desktop\prodequipos\index.html', encoding='utf-8') as f:
    content = f.read()

# ── 1. ADD TAB BUTTON ────────────────────────────────────────────────────────
old_tabs = "    <button class=\"tab\" onclick=\"showTab(event,'anual')\">Tabla Anual</button>\n  </div>"
new_tabs = "    <button class=\"tab\" onclick=\"showTab(event,'anual')\">Tabla Anual</button>\n    <button class=\"tab\" onclick=\"showTab(event,'final')\">Final</button>\n  </div>"
content = content.replace(old_tabs, new_tabs)

# ── 2. ADD CSS ───────────────────────────────────────────────────────────────
final_css = """
/* GRAN FINAL */
.final-stage { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); border-radius: 20px; padding: 32px 20px; color: #fff; }
.final-header { text-align: center; margin-bottom: 28px; }
.final-badge { background: linear-gradient(135deg, #f5a623, #e8870a); color: #fff; padding: 6px 22px; border-radius: 20px; font-weight: 900; font-size: 0.82rem; letter-spacing: 1px; display: inline-block; }
.final-vs-wrap { display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 28px; flex-wrap: wrap; }
.final-team { text-align: center; flex: 1; min-width: 110px; max-width: 160px; }
.final-avatar { width: 68px; height: 68px; border-radius: 50%; background: linear-gradient(135deg, var(--c1), var(--c2)); color: #fff; font-size: 1.3rem; font-weight: 900; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; border: 3px solid rgba(255,255,255,0.25); box-shadow: 0 6px 20px rgba(0,0,0,0.45); }
.final-team-role { font-size: 0.58rem; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.final-team-name { font-size: 0.82rem; font-weight: 700; color: rgba(255,255,255,0.9); }
.final-global { font-size: 2.4rem; font-weight: 900; color: #f5a623; line-height: 1; margin-top: 10px; }
.final-global-lbl { font-size: 0.58rem; color: rgba(255,255,255,0.35); text-transform: uppercase; letter-spacing: 0.5px; }
.vs-sep { font-size: 1.8rem; font-weight: 900; color: rgba(255,255,255,0.18); padding: 0 8px; align-self: center; }
.final-matches { display: flex; flex-direction: column; gap: 10px; margin-top: 4px; }
.final-match { background: rgba(255,255,255,0.07); border-radius: 12px; padding: 14px 20px; display: flex; align-items: center; justify-content: space-between; }
.match-label { font-size: 0.72rem; color: rgba(255,255,255,0.5); font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.match-scores { display: flex; gap: 28px; }
.match-score { text-align: center; }
.match-score .val { font-size: 1.3rem; font-weight: 900; color: #fff; line-height: 1; }
.match-score .lbl { font-size: 0.55rem; color: rgba(255,255,255,0.35); margin-top: 2px; }
.final-prox { text-align: center; padding: 36px 20px; color: rgba(255,255,255,0.35); font-size: 0.88rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; }
.winner-crown { font-size: 1.4rem; display: block; margin-bottom: 4px; }
.final-winner-name { font-size: 1rem; font-weight: 900; color: #f5a623; }
"""
content = content.replace('/* ANUAL LEADERBOARD */', final_css + '\n/* ANUAL LEADERBOARD */')

# ── 3. ADD HTML SECTION ──────────────────────────────────────────────────────
old_end = '</div>\n  </div>\n</div>\n\n<script>'
new_end = '''</div>
  </div>
</div>

<div class="section" id="sec-final">
  <div class="card" style="background:transparent;box-shadow:none;padding:0;">
    <div class="final-stage">
      <div class="final-header">
        <span class="final-badge">&#127942; GRAN FINAL</span>
      </div>
      <div id="final-content"></div>
    </div>
  </div>
</div>

<script>'''
content = content.replace(old_end, new_end, 1)

# ── 4. ADD fetchSheet FINAL TO PROMISE.ALL ───────────────────────────────────
content = content.replace(
    "fetchSheet('DATA_TOTAL'),\n  ]);",
    "fetchSheet('DATA_TOTAL'),\n    fetchSheet('FINAL'),\n  ]);"
)

# ── 5. UPDATE DESTRUCTURING ──────────────────────────────────────────────────
content = content.replace(
    'const [t1, tAp, tCl, tAn, tDt] = await',
    'const [t1, tAp, tCl, tAn, tDt, tFin] = await'
)

# ── 6. ADD FINAL PARSING + UPDATE RETURN ─────────────────────────────────────
old_return = "  return { jugadores, equipos_ap, equipos_cl, tabla_anual, ideal: { fecha: ideal_fecha, jugadores: ideal_jugadores, total: ideal_total } };"
new_return = """  // FINAL
  const fin_rows = (tFin && tFin.rows) ? tFin.rows.filter(r => gs(r,2)) : [];
  const fin_equipos = fin_rows.slice(0,2).map(r => ({
    rol: gs(r,1), nombre: gs(r,2),
    ida: gn(r,3), vta: gn(r,4), tercero: gn(r,5), global: gn(r,6)
  }));
  const final_data = { equipos: fin_equipos };

  return { jugadores, equipos_ap, equipos_cl, tabla_anual, ideal: { fecha: ideal_fecha, jugadores: ideal_jugadores, total: ideal_total }, final: final_data };"""
content = content.replace(old_return, new_return)

# ── 7. ADD renderFinal FUNCTION ──────────────────────────────────────────────
render_final_fn = """
function renderFinal() {
  const fin = DATA.final;
  const cont = document.getElementById('final-content');
  if (!fin || fin.equipos.length < 2) { cont.innerHTML = '<div class="final-prox">Sin datos</div>'; return; }
  const [e0, e1] = fin.equipos;
  const ini = n => n.split(' ').map(w=>w[0]||'').join('').slice(0,2).toUpperCase();
  const hasData = e0.ida > 0 || e1.ida > 0 || e0.vta > 0 || e1.vta > 0;
  const matchRows = [
    {label:'Final IDA', a: e0.ida, b: e1.ida},
    {label:'Final Vuelta', a: e0.vta, b: e1.vta},
    {label:'3er Partido', a: e0.tercero, b: e1.tercero},
  ].filter(m => !(m.label === '3er Partido' && m.a === 0 && m.b === 0));
  const teamBlock = (e, showGlobal) => `
    <div class="final-team">
      <div class="final-avatar">${ini(e.nombre)}</div>
      <div class="final-team-role">${e.rol}</div>
      <div class="final-team-name">${e.nombre}</div>
      ${showGlobal ? `<div class="final-global">${e.global}</div><div class="final-global-lbl">GLOBAL</div>` : ''}
    </div>`;
  if (!hasData) {
    cont.innerHTML = `
      <div class="final-vs-wrap">
        ${teamBlock(e0, false)}
        <div class="vs-sep">VS</div>
        ${teamBlock(e1, false)}
      </div>
      <div class="final-prox">&#8987;&nbsp; Pr\u00f3ximamente</div>`;
    return;
  }
  const winner = e0.global > e1.global ? e0 : e1.global > e0.global ? e1 : null;
  cont.innerHTML = `
    <div class="final-vs-wrap">
      ${teamBlock(e0, true)}
      <div class="vs-sep">VS</div>
      ${teamBlock(e1, true)}
    </div>
    <div class="final-matches">
      ${matchRows.map(m => `
        <div class="final-match">
          <div class="match-label">${m.label}</div>
          <div class="match-scores">
            <div class="match-score"><div class="val">${m.a}</div><div class="lbl">${e0.nombre}</div></div>
            <div class="match-score"><div class="val">${m.b}</div><div class="lbl">${e1.nombre}</div></div>
          </div>
        </div>`).join('')}
    </div>
    ${winner ? `<div class="final-prox"><span class="winner-crown">&#127942;</span><span class="final-winner-name">${winner.nombre}</span></div>` : ''}`;
}

"""
content = content.replace('async function init()', render_final_fn + 'async function init()')

# ── 8. CALL renderFinal IN init() ────────────────────────────────────────────
content = content.replace(
    '    renderAnual();\n  } catch(e)',
    '    renderAnual();\n    renderFinal();\n  } catch(e)'
)

with open(r'C:\Users\Nahue\Desktop\prodequipos\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

checks = [
    ('Tab Final', "showTab(event,'final')" in content),
    ('CSS .final-stage', '.final-stage' in content),
    ('HTML sec-final', 'sec-final' in content),
    ('fetchSheet FINAL', "fetchSheet('FINAL')" in content),
    ('tFin', 'tFin' in content),
    ('renderFinal fn', 'function renderFinal' in content),
    ('renderFinal call', 'renderFinal()' in content),
]
for label, ok in checks:
    print(f'{"OK" if ok else "FALLO"}: {label}')
