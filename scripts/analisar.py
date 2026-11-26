"""Metricas por interface e destino, sem contar varias vezes o mesmo pacote."""
from pathlib import Path
from collections import defaultdict
import csv, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
allrows=[]
for folder in sorted((ROOT/'resultados').iterdir()):
 if not (folder/'out.tr').exists(): continue
 bins=defaultdict(float); sums=defaultdict(float)
 for line in (folder/'out.tr').open():
  f=line.split()
  if len(f)<12 or f[0] not in ('r','d','+','-'): continue
  event,t,a,b,typ,size=f[:6]; t=float(t); a=int(a); b=int(b); size=int(size); fid=int(f[7])
  # ACKs sao incluidos apenas no total da interface; dados separados por fluxo.
  metric=None; interface=f'{a}->{b}'
  if event=='r' and (a,b) in [(3,4),(5,4),(4,3),(4,5)]: metric='bw_bps'; value=size*8
  elif event=='d': metric='loss_pps'; value=1
  elif event=='r' and b in (0,1,2,6,7,8) and typ!='ack': metric='dest_bps'; value=size*8
  else: continue
  key=(interface,metric,fid,typ)
  bins[(int(t),)+key]+=value
  if 2<=t<14: sums[key]+=value/12
 with (folder/'series.csv').open('w') as fh:
  w=csv.writer(fh);w.writerow(['second','interface','metric','fid','type','value'])
  for k,v in sorted(bins.items()): w.writerow([*k,v])
 rows=[dict(scenario=folder.name,interface=k[0],metric=k[1],fid=k[2],type=k[3],value=v) for k,v in sorted(sums.items())]
 allrows+=rows
 fig,axes=plt.subplots(2,2,figsize=(12,6),sharex=True)
 for col,interface in enumerate(('3->4','5->4')):
  for row,(metric,label) in enumerate((('bw_bps','Débito recebido (Mbps)'),('loss_pps','Descartes (pacotes/s)'))):
   ax=axes[row,col]; total=[0.]*16
   fids={k[3] for k in bins if k[1]==interface and k[2]==metric}
   if not folder.name.startswith('C4_'):
    fids.update((1,2,3) if col==0 else (4,5,6))
   fids=sorted(fids)
   for fid in fids:
    values=[sum(v for k,v in bins.items() if k[0]==t and k[1]==interface and k[2]==metric and k[3]==fid) for t in range(16)]
    total=[a+b for a,b in zip(total,values)]
    ax.step(range(16),[v/(1e6 if metric=='bw_bps' else 1) for v in values],where='post',label=f'Fluxo {fid}')
   ax.step(range(16),[v/(1e6 if metric=='bw_bps' else 1) for v in total],where='post',color='black',linestyle='--',label='Total')
   ax.set_ylabel(label);ax.set_title('E1 → C0' if col==0 else 'E2 → C0');ax.grid(alpha=.25);ax.set_ylim(bottom=0)
   if row==1: ax.set_xlabel('Tempo (s)')
 for ax in axes[0,:]: ax.legend(fontsize=7,ncol=2)
 fig.suptitle(folder.name+' — NS-2, semente 7')
 fig.tight_layout()
 for ext in ('png','pdf'): fig.savefig(ROOT/'figuras'/f'{folder.name}.{ext}',dpi=170)
 plt.close(fig)
(ROOT/'resultados'/'resumo.json').write_text(json.dumps(allrows,indent=2))
with (ROOT/'resultados'/'resumo.csv').open('w') as fh:
 w=csv.DictWriter(fh,fieldnames=['scenario','interface','metric','fid','type','value']);w.writeheader();w.writerows(allrows)
print('Gráficos e resumos gerados. Médias em [2,14[ s.')
