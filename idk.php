<?php
// Ask user for input
echo "Enter a number: ";
$n = intval(trim(fgets(STDIN))); // Read input from user

if ($n >10){
    echo ">10";
}
// Print numbers from 1 to n
for ($i = 1; $i <= $n; $i++) {
    echo $i . PHP_EOL; // prints each number on a new line
echo("Hi");
}
if ($n > 0) {
    echo $n;
}

echo("Hi");

?>