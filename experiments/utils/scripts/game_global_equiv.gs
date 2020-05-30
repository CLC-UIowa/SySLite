#!./goal batch

if $# < 6 then
  echo "Usage: game_global_equiv SOLVER1 SOLVER2 SIZE PROPS DT AS";
  echo;
  echo "SOLVER1 SOLVER2: both solvers should support parity games and the second solver";
  echo "                 will be wrapped by a global optimization solver.";
  echo "SIZE: the state size of generated games.";
  echo "PROPS: the number of symbols in the alphabet.";
  echo "DT: the transition density.";
  echo "AS: the number of acceptance sets.";
  exit;
fi

$alg0 = $1;
$alg1 = $2;
$size = $3;
$props = $4;
$dt = $5;
$as = $6;

$players = "P0 P1";
$REGION = "WinningRegion";
$STRATEGY = "WinningStrategy";

$index = 0;
while true do
  $index = $index + 1;
  echo $index + " => ";

  $game = generate -t game -m density -A classical
          -a parity -s $size -n $props -dt $dt -as $as;

  for $player in $players do
    $regions[$player] = null;
  done

  echo -n "  " + $alg0 + ": ";
  $sol = solve -m $alg0 $game;
  for $player in $players do
    $region = $sol[$player][$REGION];
    echo "(" + $player + ": " + $region + ")";
    $regions[$player] = $region;
  done

  echo -n "  " + $alg1 + ": ";
  $sol = solve -m globalopt -solver $alg1 -pp -pc -ps $game;
  for $player in $players do
    $region = $sol[$player][$REGION];
    echo "(" + $player + ": " + $region + ")";
    if $regions[$player] != $region then
      echo;
      echo "Error Found!";
      echo "Counterexample:";
      echo $game;
      exit;
    fi
  done

done
