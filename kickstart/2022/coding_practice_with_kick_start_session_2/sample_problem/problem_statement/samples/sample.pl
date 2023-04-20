$T = <STDIN>;
for ($ti = 1; $ti <= $T; $ti++) {
    ($N, $M) = split(' ', <STDIN>);
    @C = split(' ', <STDIN>);
    $sum = 0;
    for (@C) {
        $sum += $_;
    }
    $modulo = $sum % $M;
    print("Case #", $ti, ": ", $modulo, "\n");
}
