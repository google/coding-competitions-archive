<?php
function test($handle) {
  // Declare and read variables N and M.
  fscanf($handle,"%d %d\n",$N, $M);
  // Read second line of the input.
  $_line = fgets($handle);
  // Split the numbers into array C.
  $C = explode(" ", $_line);
  // Declare a variable for sum and set it to 0.
  $sum = 0;
  // Loop through vector `C` and sum its values.
  for ($i = 0; $i < $N; $i++) {
    $sum += (int)$C[$i];
  }
  // Compute the value of the sum modulo M.
  $modulo = $sum % $M;
  // Print the result onto the standard output.
  echo $modulo . "\n";
}

// Declare file pointer handle to read input.
$handle = fopen("php://stdin", "r");
// Declare and read the number of test cases.
fscanf($handle,"%d\n",$T);
// Loop over the number of test cases.
for ($test_no = 1; $test_no <= $T; $test_no++) {
  // Print case number
  echo "Case #" . $test_no . ": ";
  // and solve each test.
  test($handle);
}
?>
