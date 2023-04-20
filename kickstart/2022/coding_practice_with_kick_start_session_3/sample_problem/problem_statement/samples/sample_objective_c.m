#import <Foundation/Foundation.h>

int main() {
  int t, T;
  scanf("%d", &T);
  for (t = 1; t <= T; ++t) {
    int N, M, i;
    // Read the integers N and M from the standard input.
    scanf("%d %d", &N, &M);
    // Declare array `C` of length N.
    int C[N];
    // Read N integers from the standard input and save them in the array `C`.
    for (i = 0; i < N; ++i) {
      scanf("%d", C + i);
    }
    // Declare a variable for sum and set it to 0.
    int sum = 0;
    // Loop through array `C` and sum its values.
    for (i = 0; i < N; ++i) {
      sum += C[i];
    }
    // Print the result to the standard output.
    printf("Case #%d: %d\n", t, sum % M);
  }
  return 0;
}
