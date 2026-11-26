from pathlib import Path
p=Path(__file__).resolve().parents[1]
out=p/'scripts'/'gerados'; out.mkdir(exist_ok=True)
for mode in ('A_droptail','A_red','B_misto','B_referencia','C_diffserv'):
 src=(p/'originais'/'files'/('qos1.tcl' if mode=='C_diffserv' else 'qos0.tcl')).read_text(errors='replace')
 src=src.replace('set ns [new Simulator]','set ns [new Simulator]\nset seed 7\nif {[llength $argv] > 0} {set seed [lindex $argv 0]}\nns-random $seed')
 src=src.replace('qos0.tr','out.tr').replace('qos1.tr','out.tr').replace('qos0.nam','out.nam')
 # CBR packet_size_ e ignorado pela classe; packetSize_ explicita os 1000 bytes.
 src=src.replace('$cbr set packet_size_', '$cbr set packetSize_')
 # FTP original nao atribui identificador. Mantem TCP Tahoe original.
 src=src.replace('set tcp [new Agent/TCP]','set tcp [new Agent/TCP]\n\t$tcp set fid_ $fid\n\tincr fid')
 config='''
foreach par [list [list $E1 $C0] [list $E2 $C0] [list $C0 $E1] [list $C0 $E2]] {
 lassign $par a b
 $ns queue-limit $a $b 50
}
'''
 if mode=='A_red':
  src=src.replace('$ns duplex-link $E1 $C0 5Mb 10ms DropTail','$ns duplex-link $E1 $C0 5Mb 10ms RED').replace('$ns duplex-link $E2 $C0 5Mb 10ms DropTail','$ns duplex-link $E2 $C0 5Mb 10ms RED')
  config+='''
foreach par [list [list $E1 $C0] [list $E2 $C0]] {
 lassign $par a b
 set red [[$ns link $a $b] queue]
 $red set thresh_ 10; $red set maxthresh_ 20; $red set linterm_ 10
 $red set q_weight_ 0.002; $red set gentle_ true
 $red set mean_pktsize_ 1000; $red set bytes_ false; $red set queue_in_bytes_ false
}
'''
  # Only edge->core should use RED; return directions retain FIFO.
  src=src.replace('$ns duplex-link $E1 $C0 5Mb 10ms RED','$ns simplex-link $E1 $C0 5Mb 10ms RED\n$ns simplex-link $C0 $E1 5Mb 10ms DropTail').replace('$ns duplex-link $E2 $C0 5Mb 10ms RED','$ns simplex-link $E2 $C0 5Mb 10ms RED\n$ns simplex-link $C0 $E2 5Mb 10ms DropTail')
 src=src.replace('# Procedimentos auxiliares: criacao de fluxos CBR...',config+'\n# Procedimentos auxiliares: criacao de fluxos CBR...',1)
 if mode in ('B_misto','B_referencia'):
  a=src.index('set cbr(Cli1_Cli6)'); b=src.index('# Terminar a simulacao',a)
  src=src[:a]+'''
set apps [list [cria_fluxo_CBR $Cli1 $Cli6 1000 3000000] [cria_fluxo_FTP $Cli2 $Cli5 1000] [cria_fluxo_EXP $Cli3 $Cli4 160 64000 0.4] [cria_fluxo_CBR $Cli6 $Cli1 1000 3000000] [cria_fluxo_FTP $Cli4 $Cli2 1000] [cria_fluxo_EXP $Cli4 $Cli3 160 64000 0.4]]
foreach app $apps {$ns at 0.0 "$app start"; $ns at $tempo_simulacao "$app stop"}
'''+src[b:]
 if mode=='B_misto':
  src=src.replace('set tcp [new Agent/TCP]', 'set tcp [new Agent/TCP]\n\t$tcp set window_ 128')
 if mode=='C_diffserv':
  src=src.replace('global ns trace_file\n','global ns trace_file q\n    foreach name {E1C0 C0E2 E2C0 C0E1} {puts "FINAL $name"; $q($name) printStats}\n')
  # flush C/C++ stdout before Tcl headers to retain association of printStats.
 (out/(mode+'.tcl')).write_text('# Derivado do script oficial; ver scripts/preparar.py.\n'+src)
