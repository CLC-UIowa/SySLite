#!./goal batch

if $1 == "" || $2 == "" then
  echo "Usage: complement_equiv.gs BASE_ALGORITHM BASE_OPTIONS
         TEST_ALGORITHM TEST_OPTIONS [ STATE_SIZE PROP_SIZE TRAN_DENSITY
         ACC_DENSITY ]";
  exit;
fi

echo "Check the correctness of a complementation algorithm.";
echo;

$alg1 = $1;
$options1 = $2;
$alg2 = $3;
$options2 = $4;
$state_size = $5;
$prop_size = $6;
$dt = $7;
$da = $8;
if $state_size == null || $prop_size == null || $dt == null || $da == null then
  $state_size = 6;
  $prop_size = 2;
  $dt = 1.0;
  $da = 0.5;
fi

$st1 = 0;
$tr1 = 0;
$st2 = 0;
$tr2 = 0;
$st_diff_accum = 0;
$tr_diff_accum = 0;
$count = 0;
while true do
  echo "#" + $count + ": ";
  echo -n "  Generating an automaton: ";
  $o = generate -t fsa -a NBW -m density -s $state_size -n $prop_size -dt $dt -da $da -r -ms;
  ($s, $t) = stat $o;
  echo $s + ", " + $t;
  
  echo -n "  Complementing by " + $alg1 + ": ";
  $o1 = complement -m $alg1 --option $options1 $o;
  ($s1, $t1) = stat $o1;
  $st1 = $st1 + $s1;
  $tr1 = $tr1 + $t1;
  echo $s1 + ", " + $t1 + " (" + $st1 + ", " + $tr1 + ")";
  
  echo -n "  Complementing by " + $alg2 + ": ";
  $o2 = complement -m $alg2 --option $options2 $o;
  ($s2, $t2) = stat $o2;
  $st2 = $st2 + $s2;
  $tr2 = $tr2 + $t2;
  echo $s2 + ", " + $t2 + " (" + $st2 + ", " + $tr2 + ")";

  $st_diff = $s1 - $s2;
  $tr_diff = $t1 - $t2;
  $st_diff_accum = $st_diff_accum + $st_diff;
  $tr_diff_accum = $tr_diff_accum + $tr_diff;
  echo "  Diff: " + $st_diff + ", " + $tr_diff + 
       " (" + $st_diff_accum + ", " + $tr_diff_accum + ")";

  $count = $count + 1;
done
