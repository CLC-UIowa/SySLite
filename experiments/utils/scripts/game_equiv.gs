#!./goal batch

if $# < 8 then
  echo "Usage: game_equiv SOLVER1 SOLVER2 ... SOLVERn ACC SIZE PROPS DT DA AS";
  echo;
  echo "SOLVER1 SOLVER2 ... SOLVERn: at least two solvers are required.";
  echo "ACC: the acceptance condition of generated games.";
  echo "SIZE: the state size of generated games.";
  echo "PROPS: the number of symbols in the alphabet.";
  echo "DT: the transition density.";
  echo "DA: the acceptance density.";
  echo "AS: the number of acceptance sets.";
  exit;
fi

$ints = seq 0 ($# - 7);
for $i in $ints do
  $algorithms = $algorithms + $*[$i] + " ";
done
$acc = $*[$# - 6];
$size = $*[$# - 5];
$props = $*[$# - 4];
$dt = $*[$# - 3];
$da = $*[$# - 2];
$as = $*[$# - 1];

$players = "P0 P1";
$REGION = "WinningRegion";
$STRATEGY = "WinningStrategy";

$index = 0;
while true do
  $index = $index + 1;
  echo $index + " => ";

  $game = generate -t game -m density -A classical
          -a $acc -s $size -n $props -dt $dt -da $da -as $as;

  for $player in $players do
    $regions[$player] = null;
  done

  for $alg in $algorithms do
   echo -n "  " + $alg + ": ";
    $sol = solve -m $alg $game;
    for $player in $players do
      $region = $sol[$player][$REGION];
      echo -n "(" + $player + ": " + $region + ")";
      if $regions[$player] == null then
        $regions[$player] = $region;
      elif $regions[$player] != $region then
        echo;
        echo "Error Found!";
        echo "Counterexample:";
        echo $game;
        exit;
      fi
    done
    echo;
  done

done
