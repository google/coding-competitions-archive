def test():
  # Read integers N and M from the standard input.
  (N, M) = tuple(map(int, input().split()))
  # Read N integers from the standard input and save them in the list `C`.
  C = list(map(int, input().split()))
  # Declare a variable for sum and set it to 0.
  sum = 0
  # Loop through the list `C` and sum its values.
  for Ci in C:
    sum += Ci
  # Compute the value of sum modulo M.
  modulo = sum % M
  # Print the result onto the standard output.
  print(modulo)


# Read the number of test cases.
T = int(input())
# Loop over the number of test cases.
for test_no in range(1, T + 1):
  # Print case number
  print("Case #%d:" % test_no, end=" ")
  # and solve each test.
  test()
