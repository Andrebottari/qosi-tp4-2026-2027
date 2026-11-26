"""Repete os oito cenarios e conserva traces comprimidos, metricas e validacao."""
from pathlib import Path
from collections import defaultdict, Counter
import subprocess, gzip, shutil, json, csv, statistics, math
ROOT=Path(__file__).resolve().parents[1]
SEEDS=[7,11,23,41,97]
SCENARIOS=['A_droptail','A_red','B_misto','B_referencia','C_diffserv','C4_normal','C4_livre','C4_abuso']
base=ROOT/'resultados'/'multissementes';base.mkdir(exist_ok=True)
subprocess.run(['python3','scripts/preparar.py'],cwd=ROOT,check=True)
rows=[];validation=[]
for seed in SEEDS:
 for scenario in SCENARIOS:
  folder=ROOT/'resultados'/scenario if seed==7 else base/str(seed)/scenario
  folder.mkdir(parents=True,exist_ok=True)
  tr=folder/'out.tr'; compressed=folder/'out.tr.gz'
  if seed!=7 and not tr.exists() and not compressed.exists():
   rel=str(folder.relative_to(ROOT))
   cmd=['scripts/cenario.tcl',scenario,rel,str(seed)] if scenario.startswith('C4_') else ['/work/scripts/gerados/'+scenario+'.tcl',str(seed)]
   work='/work' if scenario.startswith('C4_') else '/work/'+rel
   import os
   with (folder/'execucao.log').open('w') as log:
    subprocess.run(['docker','run','--rm','--user',f'{os.getuid()}:{os.getgid()}','-v',str(ROOT)+':/work','-w',work,'--entrypoint','stdbuf','tp4-qos-ns2','-oL','ns',*cmd],stdout=log,stderr=subprocess.STDOUT,check=True)
  sums=defaultdict(float);sent=Counter();received=Counter();drops=Counter()
  op=tr.open if tr.exists() else lambda:gzip.open(compressed,'rt')
  with op() as fh:
   for line in fh:
    f=line.split()
    if len(f)<12 or f[0] not in ('+','-','r','d'):continue
    event=f[0];t=float(f[1]);a=int(f[2]);b=int(f[3]);typ=f[4];size=int(f[5]);fid=int(f[7]);src=int(f[8].split('.')[0]);dst=int(f[9].split('.')[0])
    if typ in ('cbr','exp'):
     if event=='+' and a==src:sent[fid]+=1
     if event=='r' and b==dst:received[fid]+=1
     if event=='d':drops[fid]+=1
    if not 2<=t<14:continue
    interface=f'{a}->{b}'
    if event=='r' and (a,b) in [(3,4),(5,4),(4,3),(4,5)]:sums[(interface,'bw_bps',fid,typ)]+=size*8/12
    elif event=='d':sums[(interface,'loss_pps',fid,typ)]+=1/12
    elif event=='r' and b in (0,1,2,6,7,8) and typ!='ack':sums[(interface,'dest_bps',fid,typ)]+=size*8/12
  assert all(sent[f]==received[f]+drops[f] for f in sent),(scenario,seed)
  def rate(interface,metric,fid=None):return sum(v for (i,m,f,_),v in sums.items() if i==interface and m==metric and (fid is None or fid==f))
  for interface in ('3->4','5->4','4->3','4->5'):assert rate(interface,'bw_bps')<=5e6+1040*8/12
  if scenario in ('C4_normal','C4_abuso'):
   for fid,i in enumerate(('5->8','5->7','5->6','3->0','3->1','3->2')):assert rate(i,'dest_bps',fid)>=1.5e6-8000/12,(scenario,seed,fid)
   for line in (folder/'execucao.log').read_text().splitlines():
    f=line.split()
    if len(f)==5 and f[0] in ('10','20','30'):assert f[3:]==['0','0'],(scenario,seed,line)
  if scenario=='C4_livre':
   for fid,i in ((0,'5->8'),(3,'3->0')):assert abs(rate(i,'dest_bps',fid)-5e6)<=8000/12
  rows.extend(dict(seed=seed,scenario=scenario,interface=i,metric=m,fid=f,type=typ,value=v) for (i,m,f,typ),v in sorted(sums.items()))
  validation.append(dict(seed=seed,scenario=scenario,udp_sent=sum(sent.values()),udp_received=sum(received.values()),udp_dropped=sum(drops.values()),checks='OK'))
  if seed!=7:
   if tr.exists():
    with tr.open('rb') as source,gzip.open(compressed,'wb',compresslevel=1) as target:shutil.copyfileobj(source,target)
    tr.unlink()
   nam=folder/'out.nam'
   if nam.exists():
    with nam.open('rb') as source,gzip.open(folder/'out.nam.gz','wb',compresslevel=1) as target:shutil.copyfileobj(source,target)
    nam.unlink()
  print(f'OK: semente {seed}, {scenario}',flush=True)
(base/'metricas.json').write_text(json.dumps(rows,indent=2))
(base/'validacao.json').write_text(json.dumps(validation,indent=2))
# Missing rows are zeros, crucial for flows starved by DropTail or no-loss runs.
keys=sorted({(x['scenario'],x['interface'],x['metric'],x['fid'],x['type']) for x in rows})
lookup={(x['seed'],x['scenario'],x['interface'],x['metric'],x['fid'],x['type']):x['value'] for x in rows}
summary=[]
for key in keys:
 values=[lookup.get((seed,*key),0.) for seed in SEEDS];mean=statistics.mean(values);sd=statistics.stdev(values)
 summary.append(dict(zip(['scenario','interface','metric','fid','type'],key),mean=mean,sd=sd,min=min(values),max=max(values),ci95_halfwidth=2.776445105*sd/math.sqrt(5),n=5))
(base/'estatisticas.json').write_text(json.dumps(summary,indent=2))
for name,data in [('metricas',rows),('validacao',validation),('estatisticas',summary)]:
 with (base/(name+'.csv')).open('w') as fh:
  w=csv.DictWriter(fh,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
print('40 execuções verificadas; média, desvio-padrão amostral e IC95% t de Student (4 g.l.).',flush=True)
