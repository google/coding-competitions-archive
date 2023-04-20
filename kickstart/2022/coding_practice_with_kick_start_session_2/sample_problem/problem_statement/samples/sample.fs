open System

// Read the number of test cases
let T = int <| Console.ReadLine()

let test testNum =
    // Read integers N and M from the standard input.
    let [|N; M|] = Console.ReadLine().Split(" ") |> Array.map int
    
    // Read N integers from the standard input and save them in the array `C`.
    let C = Console.ReadLine().Split(" ") |> Array.map int
    
    // Sum the values of C
    let sum = Seq.sum C
    
    // Compute the value of sum modulo M.
    let modulo = sum % M
    
    // Print the result onto the standard output.
    printfn $"Case #{testNum}: {modulo}"

// Run each test case from 1 to T
[1..T] |> List.iter test

