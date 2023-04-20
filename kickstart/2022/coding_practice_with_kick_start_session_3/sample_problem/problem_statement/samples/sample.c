#include <stdio.h>

void test() {
  // Declare integers N and M.
  int N, M;
  // Read the integers from the standard input.
  scanf("%d %d", &N, &M);
  // Declare array `C` of length N.
  int C[N];
  // Read N integers from the standard input and save them in the array `C`.
  for (int i = 0; i < N; i++) {
    scanf("%d", &C[i]);
  }
  // Declare a variable for sum and set it to 0.
  int sum = 0;
  // Loop through array `C` and sum its values.
  for (int i = 0; i < N; i++) {
    sum += C[i];
  }
  // Compute the value of the sum modulo M.
  int modulo = sum % M;
  // Print the result onto the standard output.
  printf("%d\n", modulo);
}

int main() {
  // Declare and read the number of test cases.
  int T;
  scanf("%d", &T);
  // Loop over the number of test cases.
  for (int test_no = 1; test_no <= T; test_no++) {
    // Print case number
    printf("Case #%d: ", test_no);
    // and solve each test.
    test();
  }
}
