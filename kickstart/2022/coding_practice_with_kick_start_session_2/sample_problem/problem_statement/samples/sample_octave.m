% Read number of cases
t = scanf("%d", "C");
for case_i = 1:t
  % Read integers N and M from the standard input.
  [n, m] = scanf("%d %d", "C");
  % Read N integers from the standard input and save them in the vector `C`.
  C = scanf("%d", n);
  % Compute sum of values.
  Csum = sum(C);
  % Compute the value of Csum modulo M.
  modulo = mod(Csum, m);
  % Print the result to standard output.
  printf("Case #%d: %d\n", case_i, modulo);
end
