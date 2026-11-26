from pathlib import Path
from collections import defaultdict
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':8,'axes.titlesize':9,'legend.fontsize':6,'axes.labelsize':8})
def draw(ax,scenario,metric):
 values=defaultdict(lambda:[0.]*16)
 with (ROOT/'resultados'/scenario/'series.csv').open() as fh:
  for r in csv.DictReader(fh):
   if r['interface']=='3->4' and r['metric']==metric:
    values[int(r['fid'])][int(r['second'])]+=float(r['value'])/(1e6 if metric=='bw_bps' else 1)
 if scenario.startswith('A_') or scenario=='C_diffserv':
  for f in (1,2,3):values[f]
 total=[0.]*16
 for fid,v in sorted(values.items()):
  total=[a+b for a,b in zip(total,v)];ax.step(range(16),v,where='post',label=f'F{fid}',linewidth=.9)
 ax.step(range(16),total,where='post',label='Total',color='black',linestyle='--',linewidth=.9)
 ax.set_ylim(bottom=0);ax.grid(alpha=.25);ax.set_xlabel('Tempo (s)');ax.set_ylabel('Mbps' if metric=='bw_bps' else 'Pacotes/s');ax.set_xlim(0,16)
 ax.legend(ncol=4,loc='best')
def save(fig,name):
 fig.tight_layout(pad=.6)
 for ext in ('pdf','png'):fig.savefig(ROOT/'figuras'/f'{name}.{ext}',dpi=200,bbox_inches='tight')
 plt.close(fig)
for scenario in ('A_droptail','A_red','C_diffserv'):
 fig,axs=plt.subplots(1,2,figsize=(6.4,2.0))
 for ax,metric,title in zip(axs,('bw_bps','loss_pps'),('Débito E1 → C0','Perdas E1 → C0')):draw(ax,scenario,metric);ax.set_title(title)
 save(fig,scenario+'_compacto')
fig,axs=plt.subplots(3,2,figsize=(6.4,5.8))
for row,(s,title) in enumerate((('C4_normal','Normal'),('C4_livre','Livre'),('C4_abuso','Abuso'))):
 for col,metric in enumerate(('bw_bps','loss_pps')):draw(axs[row,col],s,metric);axs[row,col].set_title(title+' — '+('débito' if col==0 else 'perdas'))
save(fig,'C4_comparacao')
