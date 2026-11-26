"""Auditoria apenas de leitura: manifesto, dados compactos e os 40 traces incluídos."""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
import math
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SEEDS = (7, 11, 23, 41, 97)
SCENARIOS = ('A_droptail', 'A_red', 'B_misto', 'B_referencia', 'C_diffserv',
             'C4_normal', 'C4_livre', 'C4_abuso')
FIELDS = ('scenario', 'interface', 'metric', 'fid', 'type')

def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

manifest_path = ROOT / 'resultados/validacao/MANIFESTO_SHA256.json'
if manifest_path.exists():
    manifest = json.loads(manifest_path.read_text())
    for name, expected in manifest.items():
        path = ROOT / name
        assert path.is_file(), f'Ficheiro em falta: {name}'
        assert sha256(path) == expected, f'Hash diferente: {name}'
    print(f'OK: {len(manifest)} hashes SHA-256.', flush=True)
else:
    raise FileNotFoundError('Manifesto de integridade ausente')
subprocess.run(['python3', 'scripts/verificar_entrega.py'], cwd=ROOT, check=True)
rows = json.loads((ROOT / 'resultados/multissementes/metricas.json').read_text())
lookup = {(x['seed'], *(x[k] for k in FIELDS)): x['value'] for x in rows}
checks = {(x['seed'], x['scenario']): x for x in json.loads(
    (ROOT / 'resultados/multissementes/validacao.json').read_text())}
reference = json.loads((ROOT / 'resultados/resumo.json').read_text())
for name, json_rows, columns in [
    ('resumo', reference, FIELDS),
    ('multissementes/metricas', rows, ('seed', *FIELDS)),
]:
    with (ROOT / 'resultados' / (name + '.csv')).open(newline='') as fh:
        csv_rows = list(csv.DictReader(fh))
    assert len(csv_rows) == len(json_rows), (name, 'CSV/JSON')
    for item, expected in zip(csv_rows, json_rows):
        for key in columns:
            assert str(item[key]) == str(expected[key]), (name, key)
        assert math.isclose(float(item['value']), expected['value'], rel_tol=1e-12)

count = 0
for seed in SEEDS:
    for scenario in SCENARIOS:
        folder = ROOT / 'resultados' / scenario if seed == 7 else (
            ROOT / 'resultados/multissementes' / str(seed) / scenario)
        path = folder / ('out.tr' if seed == 7 else 'out.tr.gz')
        assert path.is_file(), path
        assert (folder / 'execucao.log').is_file(), folder
        op = path.open if seed == 7 else lambda: gzip.open(path, 'rt')
        sums = defaultdict(int)
        bins = defaultdict(int)
        sent, delivered, dropped = Counter(), Counter(), Counter()
        events = 0
        with op() as stream:
            for line in stream:
                f = line.split()
                if len(f) < 12 or f[0] not in ('+', '-', 'r', 'd'):
                    continue
                events += 1
                event, time, a, b, kind, size = f[:6]
                time, a, b, size, fid = float(time), int(a), int(b), int(size), int(f[7])
                source, dest = int(f[8].split('.')[0]), int(f[9].split('.')[0])
                if kind in ('cbr', 'exp'):
                    if event == '+' and a == source:
                        sent[fid] += 1
                    if event == 'r' and b == dest:
                        delivered[fid] += 1
                    if event == 'd':
                        dropped[fid] += 1
                interface = f'{a}->{b}'
                if event == 'r' and (a, b) in ((3, 4), (5, 4), (4, 3), (4, 5)):
                    metric, value = 'bw_bps', size * 8
                elif event == 'd':
                    metric, value = 'loss_pps', 1
                elif event == 'r' and b in (0, 1, 2, 6, 7, 8) and kind != 'ack':
                    metric, value = 'dest_bps', size * 8
                else:
                    continue
                key = (scenario, interface, metric, fid, kind)
                if 2 <= time < 14:
                    sums[key] += value
                if seed == 7:
                    bins[(int(time), interface, metric, fid, kind)] += value
        assert events > 0 and sent
        for fid, packets in sent.items():
            assert packets == delivered[fid] + dropped[fid], (seed, scenario, fid)
        check = checks[(seed, scenario)]
        assert (sum(sent.values()), sum(delivered.values()), sum(dropped.values())) == (
            check['udp_sent'], check['udp_received'], check['udp_dropped'])
        expected = {key[1:]: value for key, value in lookup.items()
                    if key[0] == seed and key[1] == scenario}
        assert set(sums) == set(expected), (seed, scenario, 'chaves de métricas')
        for key, total in sums.items():
            assert math.isclose(total / 12, expected[key], rel_tol=1e-10, abs_tol=1e-8), (
                seed, key, total / 12, expected[key])
        if seed == 7:
            with (folder / 'series.csv').open(newline='') as fh:
                series = list(csv.DictReader(fh))
            assert len(series) == len(bins), scenario
            for item in series:
                key = (int(item['second']), item['interface'], item['metric'],
                       int(item['fid']), item['type'])
                assert key in bins and float(item['value']) == bins[key], (scenario, key)
        if scenario in ('C4_normal', 'C4_abuso'):
            found = 0
            for line in (folder / 'execucao.log').read_text().splitlines():
                fields = line.split()
                if len(fields) == 5 and fields[0] in ('10', '20', '30'):
                    assert fields[3:] == ['0', '0'], (seed, scenario, line)
                    found += 1
            assert found == 12, (seed, scenario, 'contadores conformes incompletos')
        count += 1
        print(f'OK: semente {seed}, {scenario}: métricas e conservação conferidas.', flush=True)
# Ler todos os NAM comprimidos até ao fim valida igualmente o CRC gzip.
for path in sorted((ROOT / 'resultados').rglob('*.nam.gz')):
    with gzip.open(path, 'rb') as stream:
        while stream.read(1024 * 1024):
            pass
print(f'OK: {count} traces, séries da semente 7 e todos os NAM gzip íntegros.', flush=True)
print('Auditoria concluída sem modificar os resultados.', flush=True)
