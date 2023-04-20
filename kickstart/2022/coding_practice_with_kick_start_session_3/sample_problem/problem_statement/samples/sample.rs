use std::io::BufRead;

fn input() -> String {
    std::io::stdin().lock().lines().next().unwrap().unwrap()
}

fn solve() -> u64 {
    // Read integers N and M from the standard input.
    let line = input();
    let mut tokens = line.split_whitespace();
    let N = tokens.next().unwrap().parse::<u64>().unwrap();
    let M = tokens.next().unwrap().parse::<u64>().unwrap();
    // Read N integers from the standard input and save them in the list `C`.
    let mut C = Vec::new();
    for token in input().split_whitespace() {
        C.push(token.parse::<u64>().unwrap());
    }

    // Declare a variable for sum and set it to 0.
    let mut sum = 0;
    // Loop through the list `C` and sum its values.
    for Ci in C {
        sum += Ci
    }
    // Compute the value of sum modulo M.
    return sum % M;
}

fn main() {
    // Read the number of test cases.
    let T = input().parse::<usize>().unwrap();
    // Loop over the number of test cases, starting from 1.
    for x in 1..T + 1 {
        // Solve the case.
        let y = solve();
        // Print case number and solution.
        println!("Case #{}: {}", x, y);
    }
}
