with open(r'C:\Users\Nahue\Desktop\prodequipos\index.html', encoding='utf-8') as f:
    content = f.read()

# ── 1. Move hstats inline next to subtitle ───────────────────────────────────
old_title_block = """    <div class="header-title">
      <h1>PRODE EQUIPOS</h1>
      <p>Torneo Apertura &amp; Clausura &mdash; Posiciones en vivo</p>
    </div>"""
new_title_block = """    <div class="header-title">
      <h1>PRODE EQUIPOS</h1>
      <div class="htitle-sub">
        <p>Torneo Apertura &amp; Clausura &mdash; Posiciones en vivo</p>
        <span id="hstats"></span>
      </div>
    </div>"""
content = content.replace(old_title_block, new_title_block)

# ── 2. Remove standalone header-stats div ───────────────────────────────────
content = content.replace('  <div class="header-stats" id="hstats"></div>\n', '')

# ── 3. Update renderHeaderStats to render compact fecha badge ────────────────
old_fn = """  document.getElementById("hstats").innerHTML = `
    <div class="hstat"><div class="val">${fecha}</div><div class="lbl">Fecha actual</div></div>`;"""
new_fn = """  document.getElementById("hstats").innerHTML = `<span class="header-fecha-val">Fecha ${fecha}</span>`;"""
content = content.replace(old_fn, new_fn)

# ── 4. Replace old .header-stats CSS with new .htitle-sub + badge CSS ────────
old_css = """.header-stats { display: flex; gap: 24px; margin-top: 20px; position: relative; z-index: 1; }
.hstat .val { font-size: 1.4rem; font-weight: 800; color: #fff; line-height: 1; }
.hstat .lbl { font-size: 0.7rem; color: rgba(255,255,255,0.55); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }"""
new_css = """.htitle-sub { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 2px; }
.htitle-sub p { margin: 0; }
.header-fecha-val { font-size: 0.72rem; font-weight: 700; color: rgba(255,255,255,0.8); background: rgba(255,255,255,0.12); padding: 3px 12px; border-radius: 12px; white-space: nowrap; flex-shrink: 0; }"""
content = content.replace(old_css, new_css)

with open(r'C:\Users\Nahue\Desktop\prodequipos\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

checks = [
    ('htitle-sub en HTML', 'htitle-sub' in content),
    ('hstats inline', '<span id="hstats">' in content),
    ('header-stats div eliminado', '<div class="header-stats" id="hstats">' not in content),
    ('renderHeaderStats actualizado', 'header-fecha-val' in content),
    ('CSS htitle-sub', '.htitle-sub' in content),
]
for label, ok in checks:
    print(f'{"OK" if ok else "FALLO"}: {label}')
