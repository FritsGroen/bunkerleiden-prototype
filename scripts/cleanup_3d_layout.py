from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Disable the previously injected room-cloning behavior while retaining the tech-card injection.
s = s.replace("const run=()=>{addRooms();addTech()};", "const run=()=>{addTech()};")

new_three = '''<section id="three" class="screen"><div class="threed-shell"><div class="threed-head"><div><div class="k">DIGITALE RECONSTRUCTIE · STL PROTOTYPE</div><h1>3D BUNKER R616</h1></div><p class="copy">Sleep met de muis om vrij 360° rond het model te draaien. Zoom met muiswiel of pinch. Het model zelf kan niet worden gewijzigd.</p></div><div class="threed-clean-stage"><aside class="threed-rail threed-left"><div class="hotspot" onclick="go('techniek')"><b>01 · SCHAKELRUIMTE</b><p>KEV, telefonie en elektrische installatie.</p></div><div class="hotspot" onclick="hes()"><b>02 · HES 1.2</b><p>Ventilatie en overdruk.</p></div><div class="hotspot"><b>03 · GASSLUIS</b><p>Beschermde overgang naar binnen.</p></div><div class="hotspot" onclick="nooduitgang()"><b>04 · NOODUITGANG</b><p>Alternatieve uitgang.</p></div><div class="hotspot"><b>05 · NAHKAMPFRAUM</b><p>Nabijverdediging van de bunker.</p></div></aside><div class="threed-center"><div class="modelwrap" id="modelwrap"><div class="modelload" id="modelload">STL MODEL LADEN…</div><canvas id="stlviewer"></canvas><div class="modelhud">SLEEP = 360° DRAAIEN · MUISWIEL/PINCH = ZOOM · GEEN BEWERKING</div></div><div class="modelsource">Bron 3D-model: eigen digitale reconstructie Stichting Bunker Leiden · <b>Assembly1.stl</b> · model in ontwikkeling.</div></div><aside class="threed-rail threed-right"><div class="hotspot"><b>06 · ONDERHOUDSCORRIDOR</b><p>Technische toegang en onderhoudsroute.</p></div><div class="hotspot"><b>07 · TOBRUK</b><p>Toegang naar de aangebouwde Tobruk-positie.</p></div><div class="hotspot" onclick="go('techniek')"><b>08 · WT80K</b><p>Bunkeroven/kachel voor verwarming.</p></div><div class="hotspot" onclick="ff33()"><b>09 · COMMUNICATIE</b><p>FF33, Sprachrohr en interne verbindingen.</p></div></aside></div></div></section>'''

pattern = re.compile(r'<section id="three" class="screen">.*?</section>', re.S)
if not pattern.search(s):
    raise SystemExit('3D section not found')
s = pattern.sub(new_three, s, count=1)

css = '''\n<style id="clean-3d-layout-20260818">\n.threed-clean-stage{display:grid;grid-template-columns:230px minmax(0,1fr) 230px;gap:14px;align-items:start}.threed-center{min-width:0}.threed-rail{display:grid;gap:10px;align-content:start}.threed-clean-stage .hotspot{padding:12px 13px}.threed-clean-stage .hotspot p{margin:6px 0 0;color:#afa691;font-size:11px;line-height:1.45}.modelsource{margin-top:8px;color:#8f8774;font:9px/1.45 monospace;text-align:center}.threed-clean-stage .modelwrap{height:calc(100vh - 205px);min-height:520px;max-height:780px}@media(max-width:1200px){.threed-clean-stage{grid-template-columns:190px minmax(0,1fr) 190px}}@media(max-width:900px){.threed-clean-stage{grid-template-columns:1fr}.threed-center{order:1}.threed-left{order:2}.threed-right{order:3}.threed-rail{grid-template-columns:repeat(2,1fr);padding:0 12px}.threed-clean-stage .modelwrap{height:60vh;min-height:400px}}@media(max-width:560px){.threed-rail{grid-template-columns:1fr}.threed-clean-stage .modelwrap{height:55vh;min-height:360px}}\n</style>\n'''
if 'clean-3d-layout-20260818' not in s:
    s = s.replace('</head>', css + '</head>', 1)

p.write_text(s, encoding='utf-8')
print('Cleaned 3D layout: 01-05 left, 06-09 right, no duplicate room lists.')
