Module kostka
  Sub test()
    ' Read integers N and M from the standard input as an array of strings.
    Dim NM() As String = Console.ReadLine().Split(" "c)
    ' Read N integers from the standard input and save them in the array of strings `C`.
    Dim C() As String = Console.ReadLine().Split(" "c)
    ' Declare a variable for sum and set it to 0.
    Dim sum As Integer = 0
    ' Loop through the array `C` and sum its values converted to integers.
    For Each i As String In C
      sum += Convert.ToInt32(i)
    Next
    ' Compute the value of sum modulo M.
    Dim modulo As Integer = sum Mod Convert.ToInt32(NM(1))
    ' Print the result onto the standard output.
    Console.WriteLine(modulo)
  End Sub

  Sub Main()
    ' Read the number of test cases.
    Dim T As Integer = Convert.ToInt32(Console.ReadLine())
    ' Loop over the number of test cases, starting from 1.
    For i As Integer = 1 To T
      ' Print case number
      Console.Write(String.Format("Case #{0}: ", i))
      ' and solve each test.
      test()
    Next
  End Sub
End Module
