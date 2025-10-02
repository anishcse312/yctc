<?php
// Ask user for input
echo "Enter a number: ";
$n = intval(trim(fgets(STDIN))); // Read input from user

if ($n > 0) {
    echo $n;
}
?>