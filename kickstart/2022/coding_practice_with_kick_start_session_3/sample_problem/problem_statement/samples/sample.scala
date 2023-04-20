object Solution {
    def main(args: Array[String]) {
        // Read the number of test cases.
        val t: Int = scala.io.StdIn.readInt
        // Loop over the number of test cases, starting from 1.
        for (caseId <- 1 to t) {
            // Read integers N and M.
            val Array(n, m) = scala.io.StdIn.readLine.split(" ").map(_.toInt)
            // Read an array of integers C1, ..., Cn.
            val c: Array[Int] = scala.io.StdIn.readLine.split(" ").map(_.toInt)
            // Declare a variable for the sum and set it to 0.
            var sum = 0
            // Loop through the list `C` and sum the values.
            for (ci <- c) {
                sum += ci
            }
            // Compute the value of sum modulo M.
            val modulo = sum % m
            // Print the case number and the result.
            println(s"Case #$caseId: $modulo")
        }
    }
}
