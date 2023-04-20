declare var require: any;
declare var process: any;

const readline = require('readline');
let rl = readline.createInterface(process.stdin, process.stdout);

// Define an interface for the data needed for each test case.
interface TestData {
  testNumber: number;
  numKids: number;
  candyBags: number[];
}

function parseInput(input: string[]) {
  let line: number = 0;
  // Read the number of test cases from the first line.
  const numCases = Number(input[line++]);

  const testData: TestData[] = [];
  for (let testNumber = 1; testNumber <= numCases; ++testNumber) {
    // The first line of each test case contains the number of candyBags
    // and the number of kids. The first number isn't needed.
    const numKids = Number(input[line++].split(' ')[1]);

    // The second line of each test contains the number of candies in each
    // bag.
    const candyBags = input[line++].split(' ').map((str) => Number(str));

    testData.push({testNumber, numKids, candyBags});
  }
  return testData;
}

function runTestCase(data: TestData) {
  // Compute the total number of candies.
  const sum = data.candyBags.reduce((sum, candies) => sum + candies, 0);

  // Compute the remainder after distributing the candies equally.
  const remainder = sum % data.numKids;

  // Print the result
  console.log(`Case #${data.testNumber}: ${remainder}`);
}

function runAllTests(input: string[]) {
  // Parse the input into TestData objects.
  const testCases = parseInput(input);

  // Run each test case.
  testCases.forEach(runTestCase);
}

// Read the input data and run all test cases.
const lines: string[] = [];
rl.on('line', line => lines.push(line)).on('close', () => runAllTests(lines));
