sin <- file("stdin")
open(sin)

T <- scan(sin, what = integer(0), n = 1)

for (t in 1:T) {
  N <- scan(sin, what = integer(0), n = 1)
  M <- scan(sin, what = integer(0), n = 1)
  C <- scan(sin, what = integer(0), n = N)
  cat(sprintf("Case #%d: %d\n", t, sum(C) %% M))
}
