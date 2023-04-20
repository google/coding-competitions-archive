fun main(args: Array<String>) {
  // Read number of testcases from standard input.
  var T = readLine()!!.toInt()
  for (tc in 1..T) {
    // Read integers n and m from the standard input.
    var (N, M) = readLine()!!.split(" ").map { it.toInt() }
    // Read n integers from the standard input and save them in the array `C`.
    var C = readLine()!!.split(" ").map { it.toInt() }

    // Declare a variable for sum and set it to 0.
    var sum = 0
    // Loop through the array `bag` and sum its values.
    for (i in 0..N - 1) {
      sum += C[i]
    }
    // Compute the value of sum modulo m.
    var modulo = sum % M
    // Print result to the standard output.
    println("Case #$tc: $modulo")
  }
}
