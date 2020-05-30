#!./goal batch

if $1 == "" || $2 == "" then
  echo "Usage: translation_equiv.gs BASE_ALGORITHM TEST_ALGORITHM [
         PROP_SIZE FORMULA_LENGTH WEIGHT_BOOL WEIGHT_FUTURE WEIGHT_PAST ]";
  exit;
fi

echo "Check the correctness of a translation algorithm.";
echo;

$base_alg = $1;
$test_alg = $2;
$prop = $3;
$len = $4;
$wb = $5;
$wf = $6;
$wp = $7;
if $prop == null || $len == null || $wb == null || $wf == null || $wp == null then
  $prop = 2;
  $len = 6;
  $wb = 1;
  $wf = 1;
  $wp = 0;
fi

$eq = 1;
$count = 0;
while $eq do
  $formula = generate -t qptl -of -n $prop -l $len -w $wb $wf $wp -of -mcp 1;
  echo "#" + $count + ": " + $formula;
  
  echo "  Translating by " + $base_alg;
  $o1 = translate -m $base_alg $formula;
  
  echo "  Translating by " + $test_alg;
  $o2 = translate -m $test_alg $formula;

  echo -n "  Checking equivalence: ";
  $equiv = equivalence $o1 $o2;
  echo $equiv;
  
  if ! $equiv then
    $eq = 0;
    echo "Counterexample found!";
    echo "";
    echo $formula;
  fi

  $count = $count + 1;
done
