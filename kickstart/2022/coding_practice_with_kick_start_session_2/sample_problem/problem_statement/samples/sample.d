import std.stdio;

void main()
{
    // Declare and read the number of test cases.
    int T;
    readf("%d\n", T);
    // Loop over the number of test cases.
    for(int tc = 1; tc <= T; tc++)
    {
        int N, M, sum = 0;
        // Read the integers from the standard input.
        readf("%d %d\n", N, M);

        // Declare array `C` of length N.
        int[] C = new int[N];
        // Read N integers from the standard input and save them in the vector `C`.
        foreach (i; 0..N)
            readf(" %d ", C[i]);

        // Loop through array `C` and sum its values.
        foreach(key, value; C)
            sum += value;

        // Print the result to the standard output.
        writeln("Case #", tc, ": ", sum % M);
    }
}
