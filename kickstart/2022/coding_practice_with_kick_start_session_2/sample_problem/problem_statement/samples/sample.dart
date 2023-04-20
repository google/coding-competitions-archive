import 'dart:io';

int test() {
  // Read M from the standard input.
  int M = int.parse(stdin.readLineSync().split(' ').last);

  // Read N integers from the standard input and save them in the list C.
  List<int> C =
      stdin.readLineSync().split(' ').map((e) => int.parse(e)).toList();

  // Reduce all elements in the list `C` to their sum.
  int sum = C.reduce((a, b) => a + b);

  // Compute the value of the sum modulo M.
  int modulo = sum % M;

  return modulo;
}

void main() {
  // Declare and read the number of test cases.
  int T = int.parse(stdin.readLineSync());
  // Loop over the number of test cases.
  for (int test_no = 1; test_no <= T; test_no++) {
    // Print case number
    print('Case #$test_no: ${test()}');
  }
}
