"""Confere os dados compactos entregues sem exigir os traces ignorados pelo Git."""
from pathlib import Path
import json
import math
import statistics

ROOT = Path(__file__).resolve().parents[1]
SEEDS = {7, 11, 23, 41, 97}
SCENARIOS = {'A_droptail', 'A_red', 'B_misto', 'B_referencia', 'C_diffserv',
             'C4_normal', 'C4_livre', 'C4_abuso'}
base = ROOT / 'resultados' / 'multissementes'
rows = json.loads((base / 'metricas.json').read_text())
checks = json.loads((base / 'validacao.json').read_text())
summary = json.loads((base / 'estatisticas.json').read_text())
expected = {(s, z) for s in SCENARIOS for z in SEEDS}
assert len(checks) == 40
assert {(x['scenario'], x['seed']) for x in checks} == expected
for x in checks:
    assert x['checks'] == 'OK'
    assert x['udp_sent'] == x['udp_received'] + x['udp_dropped'], x
assert {(x['scenario'], x['seed']) for x in rows} == expected
keys = ['scenario', 'interface', 'metric', 'fid', 'type']
lookup = {(x['seed'], *(x[k] for k in keys)): x['value'] for x in rows}
assert len(lookup) == len(rows), 'Métricas duplicadas'
for x in rows:
    assert math.isfinite(x['value']) and x['value'] >= 0
for x in summary:
    values = [lookup.get((z, *(x[k] for k in keys)), 0.0) for z in sorted(SEEDS)]
    for name, actual in [('mean', statistics.mean(values)),
                         ('sd', statistics.stdev(values)),
                         ('min', min(values)), ('max', max(values))]:
        assert math.isclose(x[name], actual, rel_tol=1e-10, abs_tol=1e-8), (x, name)
    assert x['n'] == 5
reference = json.loads((ROOT / 'resultados' / 'resumo.json').read_text())
assert len(reference) == sum(x['seed'] == 7 for x in rows)
for x in reference:
    assert math.isclose(lookup[(7, *(x[k] for k in keys))], x['value'],
                        rel_tol=1e-10, abs_tol=1e-8)
def value(scenario, seed, interface, metric, fid=None):
    return sum(x['value'] for x in rows if x['scenario'] == scenario
               and x['seed'] == seed and x['interface'] == interface
               and x['metric'] == metric and (fid is None or x['fid'] == fid))
for s, z in expected:
    for interface in ('3->4', '5->4', '4->3', '4->5'):
        assert value(s, z, interface, 'bw_bps') <= 5e6 + 1040 * 8 / 12
    if s in ('C4_normal', 'C4_abuso'):
        for fid, interface in enumerate(('5->8', '5->7', '5->6', '3->0', '3->1', '3->2')):
            assert value(s, z, interface, 'dest_bps', fid) >= 1.5e6 - 8000 / 12
    if s == 'C4_livre':
        for fid, interface in ((0, '5->8'), (3, '3->0')):
            assert abs(value(s, z, interface, 'dest_bps', fid) - 5e6) <= 8000 / 12
for name in ('main.tex', 'preambulo.tex', 'llncs.cls'):
    assert (ROOT / 'relatorio' / name).is_file(), name
assert (ROOT / 'Relatorio_Grupo7.pdf').is_file()
assert not any(w in (ROOT/'relatorio/main.tex').read_text() for w in ('PENDENTE', 'por obter'))
print('OK: 40 execuções, conservação UDP registada, estatísticas recalculadas,')
print('    semente 7 coerente com o resumo, capacidade e quotas de C.4.')
print('Esta verificação confere os dados compactos; a auditoria pacote a pacote exige os traces.')
