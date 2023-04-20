using System;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
					
public class Program
{
	private static void Test()
	{
		// Read integers N and M from the standard input.
  		IEnumerable<int> nM = Console.ReadLine().Split().Select(x => int.Parse(x));
		int N = nM.ElementAt(0);
		int M = nM.ElementAt(1);
		// Read N integers from the standard input and save them in the list `C`.
		List<int> C = Console.ReadLine().Split().Select(x => int.Parse(x)).ToList();
		// Declare a variable for sum and set it to 0.
		int sum = 0;
		// Loop through the list `C` and sum its values.
		for (int i = 0; i < N; i++)
		{
			sum += C[i];	
		}
		// Compute the value of sum modulo M.
		int modulo = sum % M;
		// Print the result onto the standard output.
		Console.WriteLine(modulo);
		
	}
	
	public static void Main()
	{
		// Read the number of test cases.
		int T = int.Parse(Console.ReadLine());
		// Loop over the number of test cases, starting from 1.
		for (int test_no = 1; test_no < T + 1; test_no++)
		{
			Console.Write(String.Format("Case #{0}: ", test_no));
			Program.Test();
		}
	}	
}
