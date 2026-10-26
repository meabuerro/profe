import json, pathlib
from collections import defaultdict

repo = pathlib.Path('.')
materias_dir = repo / 'data' / 'materias'

records = []
for f in sorted(materias_dir.glob('*.json')):
    if f.name.startswith('.') or f.name == 'merge_duplicates.py':
        continue
    try:
        d = json.loads(f.read_text(encoding='utf-8'))
    except Exception as e:
        print('PARSE ERROR', f, e)
        continue
    records.append({
        'file': f.name,
        'id_etapa': d.get('id_etapa'),
        'id_materia': d.get('id_materia'),
        'nombre': (d.get('nombre') or '').strip(),
    })

print('total registros:', len(records))
print('=' * 60)

# 1) duplicados por id_materia (mismo id, posiblemente distinta etapa o nombre)
by_id = defaultdict(list)
for r in records:
    if r['id_materia']:
        by_id[r['id_materia']].append(r)
print('DUPLICADOS POR id_materia (mismo id en varios archivos):')
for idm, group in sorted(by_id.items()):
    if len(group) > 1:
        print(f"  id_materia={idm}")
        for r in group:
            print(f"    - {r['file']} | etapa={r['id_etapa']} | nombre={r['nombre']!r}")
print('=' * 60)

# 2) duplicados por nombre normalizado (misma etapa, nombre casi idéntico)
def normalize_name(s):
    if not s:
        return ''
    import unicodedata
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
    s = s.lower()
    s = s.replace('ii', '2').replace('iii', '3').replace('iv', '4')
    s = ' '.join(s.split())
    # remove trailing roman/hindu numerals like "ii", "2", "3"
    s = s.rstrip('0123456789')
    s = s.strip()
    return s

by_name = defaultdict(list)
for r in records:
    key = (r['id_etapa'], normalize_name(r['nombre']))
    by_name[key].append(r)

print('DUPLICADOS POR nombre normalizado (misma etapa, nombre equivalente):')
found_any = False
for (etapa, namekey), group in sorted(by_name.items()):
    if len(group) > 1:
        found_any = True
        print(f"  etapa={etapa} | nombre_normalizado={namekey!r}")
        for r in group:
            print(f"    - {r['file']} | id_materia={r['id_materia']} | nombre={r['nombre']!r}")
if not found_any:
    print('  (ninguno)')

print('=' * 60)
print('resumen de ids_duplicados o conflictivos por id_materia:')
for idm, group in sorted(by_id.items()):
    if len(group) > 1:
        print(f"  {idm}: {len(group)} archivos -> {[r['file'] for r in group]}")
