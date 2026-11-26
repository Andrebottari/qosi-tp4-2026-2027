"""Verifica conservacao UDP e capacidade a partir dos traces executados."""
from pathlib import Path
from collections import Counter
import json
root=Path(__file__).resolve().parents[1]
for folder in sorted((root/'resultados').iterdir()):
 if not (folder/'out.tr').exists(): continue
 sent=Counter(); received=Counter(); dropped=Counter()
 for line in (folder/'out.tr').open():
  f=line.split()
  if len(f)<12 or f[4] not in ('cbr','exp'): continue
  source=int(f[8].split('.')[0]); dest=int(f[9].split('.')[0]); fid=int(f[7])
  if f[0]=='+' and int(f[2])==source: sent[fid]+=1
  if f[0]=='r' and int(f[3])==dest: received[fid]+=1
  if f[0]=='d': dropped[fid]+=1
 for fid,n in sent.items():
  assert n==received[fid]+dropped[fid],(folder.name,fid,n,received[fid],dropped[fid])
 assert sent,folder
 print(f'{folder.name}: conservação UDP confirmada ({sum(sent.values())} pacotes gerados).')
r=json.loads((root/'resultados/resumo.json').read_text())
for scenario in {x['scenario'] for x in r}:
 for interface in ('3->4','5->4','4->3','4->5'):
  rate=sum(x['value'] for x in r if x['scenario']==scenario and x['interface']==interface and x['metric']=='bw_bps')
  assert rate<=5e6+1040*8/12,(scenario,interface,rate)
print('Capacidade das quatro interfaces respeitada nas médias.')
assert not any(word in (root/'relatorio/main.tex').read_text() for word in ['PENDENTE','por obter'])
print('Relatório sem marcadores pendentes.')
for scenario in ('C4_normal','C4_abuso'):
 for fid,interface in [(0,'5->8'),(1,'5->7'),(2,'5->6'),(3,'3->0'),(4,'3->1'),(5,'3->2')]:
  rate=sum(x['value'] for x in r if x['scenario']==scenario and x['interface']==interface and x['metric']=='dest_bps' and x['fid']==fid)
  assert rate>=1.5e6-8000/12,(scenario,fid,rate)
for fid,interface in [(0,'5->8'),(3,'3->0')]:
 rate=sum(x['value'] for x in r if x['scenario']=='C4_livre' and x['interface']==interface and x['metric']=='dest_bps' and x['fid']==fid)
 assert abs(rate-5e6)<=8000/12,(fid,rate)
for scenario in ('C4_normal','C4_abuso'):
 for line in (root/'resultados'/scenario/'execucao.log').read_text().splitlines():
  fields=line.split()
  if len(fields)==5 and fields[0] in ('10','20','30'):
   assert fields[3:]==['0','0'],(scenario,line)
print('C.4: quotas >= 1,5 Mbps, empréstimo até 5 Mbps e ausência de descartes conformes confirmados nos ensaios.')
