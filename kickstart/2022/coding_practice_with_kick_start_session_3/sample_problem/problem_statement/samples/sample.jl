function test()
  # Read integers N and M from the standard input.
  (N, M) = map(x -> parse(Int64, x), split(readline()))
  # Read N integers from the standard input and save them in the list `C`.
  C = map(x -> parse(Int64, x), split(readline()))
  # Declare a variable for sum and set it to 0.
  sum = 0
  # Loop through the list `C` and sum its values.
  for i in range(1, length = N, step = 1)
    sum = sum + C[i]
  end
  # Compute the value of sum modulo M.
  modulo = sum % M
  # Print the result onto the standard output.
  println(modulo)
end

# Read the number of test cases.
T = parse(Int64, readline())
# Loop over the number of test cases, starting from 1.
for test_no in range(1, length = T, step = 1)
  # Print case number
  print("Case #$(test_no): ")
  # and solve each test.
  test()
end
