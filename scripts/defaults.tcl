foreach cls {Queue Queue/RED Queue/dsRED Queue/dsRED/edge} {
 foreach var {limit_ numQueues_ numPrec_} {
  catch {puts "$cls $var = [$cls set $var]"}
 }
}
exit
