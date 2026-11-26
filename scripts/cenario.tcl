# Proposta C.4: apenas as cargas normal, livre e abuso. A–C usam os TCL oficiais gerados.
set mode [lindex $argv 0]
set out [lindex $argv 1]
if {$mode ni {C4_normal C4_livre C4_abuso}} {error "Use C4_normal, C4_livre ou C4_abuso"}
set ns [new Simulator]
set seed 7
if {[llength $argv] > 2} {set seed [lindex $argv 2]}
ns-random $seed
set tr [open "$out/out.tr" w]
$ns trace-all $tr
set nam [open "$out/out.nam" w]
$ns namtrace-all $nam
for {set i 0} {$i < 9} {incr i} {set n($i) [$ns node]}
foreach i {0 1 2} {$ns duplex-link $n($i) $n(3) 5Mb 5ms DropTail}
foreach i {6 7 8} {$ns duplex-link $n($i) $n(5) 5Mb 5ms DropTail}
foreach pair {{3 4} {5 4}} {
 lassign $pair a b
 $ns simplex-link $n($a) $n($b) 5Mb 10ms dsRED/edge
 $ns simplex-link $n($b) $n($a) 5Mb 10ms dsRED/core
}
set queues {}
foreach pair {{3 4} {4 3} {5 4} {4 5}} {
 lassign $pair a b
 $ns queue-limit $n($a) $n($b) 50
 set q [[$ns link $n($a) $n($b)] queue]
 lappend queues [list $a $b $q]
 $q meanPktSize 1000
 $q set numQueues_ 4
 $q setNumPrec 1
 $q setSchedularMode WRR
 for {set j 0} {$j < 4} {incr j} {
  $q setMREDMode RIO-C $j
  if {$j < 3} {
   $q configQ $j 0 20 40 0.02
   $q addQueueWeights $j 3
  } else {
   $q configQ $j 0 10 20 0.10
   $q addQueueWeights $j 1
  }
 }
 $q addPHBEntry 10 0 0
 $q addPHBEntry 20 1 0
 $q addPHBEntry 30 2 0
 $q addPHBEntry 11 3 0
}
set pairs {{0 8} {1 7} {2 6} {8 0} {7 1} {6 2}}
set fid 0
foreach pair $pairs {
 lassign $pair s d
 set idx [expr {$fid % 3}]
 if {$s < 3} {set edge 3} else {set edge 5}
 set q [[$ns link $n($edge) $n(4)] queue]
 $q addPolicyEntry $s $d TokenBucket [expr {10*($idx+1)}] 1500000 5000
 set rate 3Mb
 if {$mode eq "C4_livre"} {if {$idx != 0} {incr fid; continue}; set rate 5Mb}
 if {$mode eq "C4_abuso"} {if {$idx == 0} {set rate 4.5Mb} else {set rate 1.5Mb}}
 set agent [new Agent/UDP]; set sink [new Agent/Null]
 set app [new Application/Traffic/CBR]
 $app set packetSize_ 1000; $app set rate_ $rate; $app set random_ false
 $agent set fid_ $fid
 $ns attach-agent $n($s) $agent; $ns attach-agent $n($d) $sink
 $ns connect $agent $sink; $app attach-agent $agent
 $ns at 0.1 "$app start"; $ns at 15.1 "$app stop"
 incr fid
}
foreach item $queues {
 lassign $item a b q
 if {$a == 3 || $a == 5} {
  foreach cp {10 20 30} {$q addPolicerEntry TokenBucket $cp 11}
 }
}
proc finish {} {
 global ns tr nam queues
 $ns flush-trace
 foreach item $queues {lassign $item a b q; puts "INTERFACE $a $b"; $q printStats}
 close $tr; close $nam; exit 0
}
$ns at 16.0 finish
$ns run
