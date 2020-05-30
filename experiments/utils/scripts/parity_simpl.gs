#!./goal batch

if $# < 4 then
  echo "Usage: parity SIZE PROPS DT AS";
  echo;
  echo "SIZE: the state size of generated games.";
  echo "PROPS: the number of symbols in the alphabet.";
  echo "DT: the transition density.";
  echo "AS: the number of acceptance sets.";
  exit;
fi

$size = $1;
$props = $2;
$dt = $3;
$as = $4;

$index = 0;
while true do
  $index = $index + 1;
  echo -n $index + " => ";

  $aut = generate -t fsa -m density -A classical
         -a parity -s $size -n $props -dt $dt -as $as;

  $aut2 = parity propagate $aut;
  $aut2 = parity compress $aut;

  $eq = equivalence $aut $aut2;
  echo $eq;

  if !$eq then
    echo "COUNTEREXAMPLE FOUND!";
    echo $aut;
    exit;
  fi

done
