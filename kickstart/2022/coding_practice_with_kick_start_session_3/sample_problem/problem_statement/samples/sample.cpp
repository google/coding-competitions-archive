#include <iostream>
#include <vector>

using namespace std;

void test() {
  // Declare integers N and M.
  int N, M;
  // Read the integers from the standard input.
  cin >> N >> M;
  // Declare vector `C` of length N.
  vector<int> C(N);
  // Read N integers from the standard input and save them in the vector `C`.
  for (int i = 0; i < N; i++) {
    cin >> C[i];
  }
  // Declare a variable for sum and set it to 0.
  int sum = 0;
  // Loop through vector `C` and sum its values.
  for (int i = 0; i < N; i++) {
    sum += C[i];
  }
  // Compute the value of the sum modulo M.
  int modulo = sum % M;
  // Print the result to the standard output.
  cout << modulo << "\n";
}

int main() {
  // Declare and read the number of test cases.
  int T;
  cin >> T;
  // Loop over the number of test cases.
  for (int test_no = 1; test_no <= T; test_no++) {
    // Print case number
    cout << "Case #" << test_no << ": ";
    // and solve each test.
    test();
  }
}
