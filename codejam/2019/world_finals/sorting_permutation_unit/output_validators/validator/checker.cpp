#include "bits/stdc++.h"
using namespace std;

#define FOR(i, a, b) for (int i = (a), _##i = (b); i <= _##i; ++i)
#define REP(i, a) for (int i = 0, _##i = (a); i < _##i; ++i)
#define SZ(x) ((int)(x).size())

bool mocked_error;
string last_error;

void Error(const string& msg) {
  if (mocked_error) {
    last_error = msg;
    // throw to avoid additional errors.
    throw 1;
  } else {
    cerr << msg << endl;
    exit(1);
  }
}

#define AssertError(call, err) \
  mocked_error = true;         \
  try {                        \
    call;                      \
  } catch (...) {              \
  }                            \
  assert(last_error == err);   \
  last_error = "";             \
  mocked_error = false;

template <typename T>
ostream& operator<<(ostream& o, const vector<T>& v) {
  o << "[";
  for (const T& t : v) o << t << ", ";
  return o << "]";
}

string Strint(long long n) {
  ostringstream out;
  out << n;
  return out.str();
}

void TestStrint() {
  assert(Strint(5) == "5");
  assert(Strint(-21) == "-21");
  assert(Strint(0) == "0");
}

string Truncate(const string& s) {
  if (s.size() <= 50) return s;
  return s.substr(0, 47) + string("...");
}

void TestTruncate() {
  assert(Truncate("") == "");
  assert(Truncate("helloworld") == "helloworld");
  assert(Truncate(string(50, 'x')) == string(50, 'x'));
  assert(Truncate(string(51, 'x')) == string(47, 'x') + "...");
}

// Parses ints in [-10^18, 10^18] or raises Error.
long long ParseInt(const string& ss) {
  const string error = string("Not an integer in range: ") + Truncate(ss);
  if (ss[0] != '-' && (ss[0] < '0' || ss[0] > '9')) Error(error);
  for (int i = 1; i < (int)ss.size(); ++i)
    if (ss[i] < '0' || ss[i] > '9') Error(error);
  string s;
  if (!ss.empty()) {
    int first_digit = 0;
    if (ss[0] == '-') {
      s += '-';
      first_digit = 1;
    }
    while (first_digit < (int)ss.size() - 1 && ss[first_digit] == '0')
      ++first_digit;
    s += ss.substr(first_digit);
  }
  if (s.empty() || s.size() > 20) Error(error);
  if (s.size() == 20 && s != string("-1") + string(18, '0')) Error(error);
  if (s.size() == 19 && s[0] != '-' && s != string("1") + string(18, '0'))
    Error(error);
  istringstream in(s);
  long long r;
  in >> r;
  return r;
}

void TestParseInt() {
  assert(ParseInt("0") == 0);
  assert(ParseInt("0000") == 0);
  assert(ParseInt("-0") == 0);
  assert(ParseInt("-0000") == 0);
  assert(ParseInt("-10") == -10);
  assert(ParseInt("-010") == -10);
  assert(ParseInt("010111") == 10111);
  assert(ParseInt("00009") == 9);
  assert(ParseInt(string("1") + string(18, '0')) == 1000000000000000000);
  assert(ParseInt(string("0001") + string(18, '0')) == 1000000000000000000);
  assert(ParseInt(string("-1") + string(18, '0')) == -1000000000000000000);
  assert(ParseInt(string("-0001") + string(18, '0')) == -1000000000000000000);
  AssertError(ParseInt(""), "Not an integer in range: ");
  AssertError(ParseInt("a"), "Not an integer in range: a");
  AssertError(ParseInt("1a1"), "Not an integer in range: 1a1");
  AssertError(ParseInt(string("1") + string(17, '0') + "1"),
              "Not an integer in range: 1000000000000000001");
  AssertError(ParseInt(string("-1") + string(17, '0') + "1"),
              "Not an integer in range: -1000000000000000001");
  AssertError(ParseInt("0x10"), "Not an integer in range: 0x10");
  AssertError(ParseInt("1.0"), "Not an integer in range: 1.0");
}

string Lowercase(const string& s) {
  string r(s);
  for (char& c : r) c = tolower(c);
  return r;
}

void TestLowercase() {
  assert(Lowercase("Case") == "case");
  assert(Lowercase("c") == "c");
  assert(Lowercase("A") == "a");
  assert(Lowercase("234") == "234");
  assert(Lowercase("AbC234xYz") == "abc234xyz");
}

vector<string> Tokenize(const string& l) {
  istringstream in(l);
  string s;
  vector<string> r;
  while (in >> s) r.push_back(Lowercase(s));
  return r;
}

void TestTokenize() {
  assert(Tokenize("a b c") == vector<string>({"a", "b", "c"}));
  assert(Tokenize("1") == vector<string>({"1"}));
  assert(Tokenize("  1  ") == vector<string>({"1"}));
  assert(Tokenize("  1\t2    \n3\n\n\n4") ==
         vector<string>({"1", "2", "3", "4"}));
}

vector<vector<string>> ReadAndTokenizeFileLines(istream& in) {
  string s;
  vector<vector<string>> r;
  while (getline(in, s)) {
    auto t = Tokenize(s);
    if (!t.empty()) r.push_back(t);
  }
  return r;
}

vector<vector<vector<string>>> SplitCases(const vector<vector<string>>& lines) {
  vector<vector<vector<string>>> cases;
  if (lines.empty() || lines[0].empty() || lines[0][0] != "case")
    Error("First line doesn't start with case");
  for (const vector<string>& line : lines) {
    if (!lines.empty() && line[0] == "case") {
      if (line.size() <= 1 || line[1].size() < 3 || line[1][0] != '#' ||
          line[1][line[1].size() - 1] != ':' ||
          ParseInt(line[1].substr(1, (int)line[1].size() - 2)) !=
              (int)cases.size() + 1) {
        Error(string("Wrongly formatted line to start Case #") +
              Strint(cases.size() + 1));
      }
      vector<string> new_line(line);
      new_line.erase(new_line.begin(), new_line.begin() + 2);
      cases.push_back(vector<vector<string>>(1, new_line));
    } else {
      cases.back().push_back(line);
    }
  }
  return cases;
}

void TestSplitCases() {
  // TODO(tullis): add tests.
}

template <typename T>
vector<T> ParseAllInput(istream& in, T ParseCaseInputF(istream&)) {
  int t;
  in >> t;
  vector<T> v(t);
  for (int i = 0; i < t; ++i) v[i] = ParseCaseInputF(in);
  return v;
}

template <typename T, typename U>
vector<U> ParseAllOutput(istream& in, const vector<T>& input,
                         U ParseCaseOutputF(const T&,
                                            const vector<vector<string>>&)) {
  vector<vector<vector<string>>> tokenized_lines =
      SplitCases(ReadAndTokenizeFileLines(in));
  vector<U> v(tokenized_lines.size());
  for (int i = 0; i < (int)tokenized_lines.size(); ++i)
    v[i] = ParseCaseOutputF(input[i], tokenized_lines[i]);
  return v;
}

template <typename T, typename U>
string JudgeAllCases(const vector<T>& input, const vector<U>& correct_output,
                     const vector<U>& attempt,
                     string JudgeCase(const T&, const U&, const U&)) {
  if (attempt.size() != input.size())
    Error(string("Wrong number of cases in attempt: ") +
          Strint(attempt.size()) + ", expected: " + Strint(input.size()));
  for (int i = 0; i < (int)input.size(); ++i) {
    string e = JudgeCase(input[i], correct_output[i], attempt[i]);
    if (e.empty()) continue;
    ostringstream out;
    out << "Case #" << (i + 1) << ": " << e;
    return out.str();
  }
  return "";
}

void TestJudgeAllCases() {
  // TODO(tullis): Add tests.
}

void TestLib() {
  TestStrint();
  TestTruncate();
  TestParseInt();
  TestLowercase();
  TestTokenize();
  TestSplitCases();
  TestJudgeAllCases();
}

//////////////////////////////////////////////

struct CaseInput {
  int P, S, K, N;
  vector<vector<int>> as;
};

struct CaseOutput {
  vector<vector<int>> permutations;
  vector<vector<int>> operations;
};

CaseInput ParseCaseInput(istream& cin) {
  CaseInput input;
  cin >> input.P >> input.S >> input.K >> input.N;
  REP(ik, input.K) {
    vector<int> a(input.N);
    REP(i, input.N) cin >> a[i];
    input.as.push_back(a);
  }
  return input;
}

bool IsZeroBasedPermutation(vector<int> array) {
  sort(array.begin(), array.end());
  REP(i, SZ(array)) {
    if (array[i] != i) return false;
  }
  return true;
}

const string BAD_OUTPUT_EMPTY = "Bad output format: case output is empty";
const string BAD_OUTPUT_LINE_1 =
    "Bad output format: 1st line should be 'Case #T:\n'";
const string BAD_OUTPUT_LINE_2 =
    "Bad output format: 2nd line should contain number of permutations";
const string BAD_OUTPUT_TOO_FEW_PERMUTATIONS =
    "Bad output format: Too few permutations";
const string BAD_OUTPUT_TOO_MANY_PERMUTATIONS =
    "Bad output format: Too many permutations";
const string BAD_OUTPUT_INCORRECT_N_LINES =
    "Bad output format: number of lines in output is incorrect";
const string BAD_OUTPUT_LINE_3 =
    "Bad output format: line 3..nPermutation+2 must contain exactly N elements";
const string BAD_OUTPUT_NOT_PERMUTATION =
    "Bad output format: not a permutation";
const string BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS =
    "Bad output format: operation line does not have correct number of "
    "elements";
const string BAD_OUTPUT_TOO_MANY_OPERATIONS = "Bad output: Too many operations";
const string BAD_OUTPUT_OPERATION_OUT_OF_RANGE =
    "Bad output format: operation not in [1, nPermutation]";

CaseOutput ParseCaseOutput(const CaseInput& input,
                           const vector<vector<string>>& lines) {
  CaseOutput output;
  if (lines.empty()) {
    Error(BAD_OUTPUT_EMPTY);
  }

  // line 0: "Case #T:"
  if (!lines[0].empty()) {
    Error(BAD_OUTPUT_LINE_1);
  }

  // line 1: nPermutation
  if (SZ(lines) <= 1 || lines[1].empty()) {
    Error(BAD_OUTPUT_LINE_2);
  }
  int nPermutation = ParseInt(lines[1][0]);
  if (nPermutation < 1) {
    Error(BAD_OUTPUT_TOO_FEW_PERMUTATIONS);
  }
  if (nPermutation > input.P) {
    Error(BAD_OUTPUT_TOO_MANY_PERMUTATIONS);
  }

  // lines 2..nPermutation+1: permutations
  if (SZ(lines) != nPermutation + input.K + 2) {
    Error(BAD_OUTPUT_INCORRECT_N_LINES);
  }
  output.permutations.clear();
  FOR(l, 2, nPermutation + 1) {
    if (SZ(lines[l]) != input.N) {
      Error(BAD_OUTPUT_LINE_3);
    }
    vector<int> permutation(input.N);
    REP(i, input.N) { permutation[i] = ParseInt(lines[l][i]) - 1; }

    if (!IsZeroBasedPermutation(permutation)) {
      Error(BAD_OUTPUT_NOT_PERMUTATION);
    }

    output.permutations.push_back(permutation);
  }

  // lines nPermutation+2..input.K+1: operations
  output.operations.clear();
  FOR(l, nPermutation + 2, nPermutation + input.K + 1) {
    assert(!lines[l].empty());
    int nOps = ParseInt(lines[l][0]);
    if (SZ(lines[l]) != nOps + 1) {
      Error(BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
    }
    if (nOps > input.S) {
      Error(BAD_OUTPUT_TOO_MANY_OPERATIONS);
    }

    vector<int> operation;
    REP(i, nOps) {
      int op = ParseInt(lines[l][i + 1]);
      if (op < 1 || op > nPermutation) {
        Error(BAD_OUTPUT_OPERATION_OUT_OF_RANGE);
      }
      operation.push_back(op - 1);
    }
    output.operations.push_back(operation);
  }
  return output;
}

vector<int> PermuteArray(const vector<int>& array,
                         const vector<int>& permutation) {
  vector<int> permutedArray(SZ(array));
  REP(i, SZ(array)) { permutedArray[i] = array[permutation[i]]; }
  return permutedArray;
}

bool IsSorted(const vector<int>& array) {
  REP(i, SZ(array) - 1) {
    if (array[i] > array[i + 1]) return false;
  }
  return true;
}

const string NOT_SORTED = "Wrong: Not sorted";
string JudgeCase(const CaseInput& input, const CaseOutput& correct,
                 const CaseOutput& attempt) {
  REP(i, input.K) {
    auto a = input.as[i];

    for (auto op : attempt.operations[i]) {
      a = PermuteArray(a, attempt.permutations[op]);
    }

    if (!IsSorted(a)) {
      return NOT_SORTED;
    }
  }
  return "";
}

string join(const vector<string>& strings, const char* const delim = "\n") {
  ostringstream imploded;
  std::copy(strings.begin(), strings.end(),
            ostream_iterator<string>(imploded, delim));
  return imploded.str();
}

void TestParseAllOutput(const vector<CaseInput>& inputs,
                        const vector<string>& output_lines, string error_msg) {
  istringstream output_stream(join(output_lines));

  if (error_msg != "") {
    AssertError(ParseAllOutput(output_stream, inputs, ParseCaseOutput),
                error_msg);
  } else {
    ParseAllOutput(output_stream, inputs, ParseCaseOutput);
  }
}

void TestJudgeAllCases(const vector<CaseInput>& inputs,
                       const vector<string>& output_lines,
                       const vector<string>& attempt_lines, string error_msg) {
  istringstream output_stream(join(output_lines));
  auto outputs = ParseAllOutput(output_stream, inputs, ParseCaseOutput);

  istringstream attempt_stream(join(attempt_lines));
  auto attempts = ParseAllOutput(attempt_stream, inputs, ParseCaseOutput);

  assert(JudgeAllCases(inputs, outputs, attempts, JudgeCase) == error_msg);
}

vector<string> Modify(const vector<string>& lines, int idx, string new_value) {
  vector<string> res(lines);
  res[idx] = new_value;
  return res;
}

void Test() {
  string input_file = join(
      {// 1 test case, 4 permutations, 5 operations, 4 arrays of length 3
       "1", "4 5 4 3", "10 10 11", "17 4 1000", "999 998 997", "10 10 11"});
  istringstream input_stream(input_file);
  auto inputs = ParseAllInput(input_stream, ParseCaseInput);

  string invalid_character = "";
  invalid_character += (char)6;

  TestParseAllOutput(inputs, vector<string>{invalid_character},
                     "First line doesn't start with case");
  TestParseAllOutput(inputs, vector<string>{"Case #1:", invalid_character},
                     "Not an integer in range: " + invalid_character);
  TestParseAllOutput(inputs, vector<string>{},
                     "First line doesn't start with case");
  TestParseAllOutput(inputs, vector<string>{"Case ##1:"},
                     "Not an integer in range: #1");

  vector<string> output_lines = {"Case #1:", "2",   "3 1 2", "2 1 3",
                                 "0",        "1 2", "2 2 1", "1 2"};
  // Valid outputs.
  TestParseAllOutput(inputs, output_lines, "");
  TestParseAllOutput(inputs, Modify(output_lines, 0, "  Case     #1:     "),
                     "");
  TestParseAllOutput(
      inputs,
      vector<string>{"Case #1:", "   ", "\t\t", "2", "", "3 1 2", "2 1 3", "",
                     "0", "", "1 2", "   ", "\t\t", "2 2 1", "", "1 2"},
      "");

  // Wrong: 1st line.
  FOR(i, 1, SZ(output_lines)) {
    TestParseAllOutput(
        inputs, vector<string>(output_lines.begin() + i, output_lines.end()),
        "First line doesn't start with case");
  }
  TestParseAllOutput(inputs, Modify(output_lines, 0, "Case #1: 2"),
                     BAD_OUTPUT_LINE_1);
  TestParseAllOutput(inputs, Modify(output_lines, 0, "Case 1:"),
                     "Wrongly formatted line to start Case #1");

  // Wrong: permutations.
  TestParseAllOutput(inputs, Modify(output_lines, 1, "3"),
                     BAD_OUTPUT_INCORRECT_N_LINES);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "3 1"), BAD_OUTPUT_LINE_3);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "3 1   "),
                     BAD_OUTPUT_LINE_3);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "3 1 2 4"),
                     BAD_OUTPUT_LINE_3);
  TestParseAllOutput(inputs, Modify(output_lines, 2, ""),
                     BAD_OUTPUT_INCORRECT_N_LINES);
  TestParseAllOutput(inputs, Modify(output_lines, 3, "3 1"), BAD_OUTPUT_LINE_3);
  TestParseAllOutput(inputs, Modify(output_lines, 3, "3 1   "),
                     BAD_OUTPUT_LINE_3);
  TestParseAllOutput(inputs, Modify(output_lines, 3, "3 1 2 4"),
                     BAD_OUTPUT_LINE_3);
  TestParseAllOutput(inputs, Modify(output_lines, 3, ""),
                     BAD_OUTPUT_INCORRECT_N_LINES);

  // Wrong: operations.
  TestParseAllOutput(inputs, Modify(output_lines, 4, ""),
                     BAD_OUTPUT_INCORRECT_N_LINES);
  TestParseAllOutput(inputs, Modify(output_lines, 4, "1"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
  TestParseAllOutput(inputs, Modify(output_lines, 4, "1 2 1"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
  TestParseAllOutput(inputs, Modify(output_lines, 4, "2 2"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
  TestParseAllOutput(inputs, Modify(output_lines, 5, ""),
                     BAD_OUTPUT_INCORRECT_N_LINES);
  TestParseAllOutput(inputs, Modify(output_lines, 5, "1"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
  TestParseAllOutput(inputs, Modify(output_lines, 5, "1 2 1"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
  TestParseAllOutput(inputs, Modify(output_lines, 5, "2 2"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
  TestParseAllOutput(inputs, Modify(output_lines, 6, ""),
                     BAD_OUTPUT_INCORRECT_N_LINES);
  TestParseAllOutput(inputs, Modify(output_lines, 6, "1"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
  TestParseAllOutput(inputs, Modify(output_lines, 6, "1 2 1"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
  TestParseAllOutput(inputs, Modify(output_lines, 6, "2 2"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
  TestParseAllOutput(inputs, Modify(output_lines, 7, ""),
                     BAD_OUTPUT_INCORRECT_N_LINES);
  TestParseAllOutput(inputs, Modify(output_lines, 7, "1"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
  TestParseAllOutput(inputs, Modify(output_lines, 7, "1 2 1"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);
  TestParseAllOutput(inputs, Modify(output_lines, 7, "2 2"),
                     BAD_OUTPUT_OPERATION_WRONG_N_ELEMENTS);

  // Not number
  TestParseAllOutput(inputs, Modify(output_lines, 1, "two"),
                     "Not an integer in range: two");
  TestParseAllOutput(inputs, Modify(output_lines, 2, "three 1 2"),
                     "Not an integer in range: three");
  TestParseAllOutput(inputs, Modify(output_lines, 2, "3 one 2"),
                     "Not an integer in range: one");

  // Number of permutations not in [1, S].
  TestParseAllOutput(
      inputs, vector<string>{"Case #1:", "0", "0", "1 2", "2 2 1", "1 2"},
      BAD_OUTPUT_TOO_FEW_PERMUTATIONS);
  TestParseAllOutput(
      inputs,
      vector<string>{"Case #1:", "5", "1 2 3", "1 2 3", "1 2 3", "1 2 3",
                     "1 2 3", "0", "1 2", "2 2 1", "1 2"},
      BAD_OUTPUT_TOO_MANY_PERMUTATIONS);
  TestParseAllOutput(inputs,
                     vector<string>{"Case #1:", "4", "1 2 3", "1 2 3", "1 2 3",
                                    "1 2 3", "0", "1 2", "2 2 1", "1 2"},
                     "");

  // Bad permutation
  TestParseAllOutput(inputs, vector<string>{"Case #1:"}, BAD_OUTPUT_LINE_2);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "3 1 1"),
                     BAD_OUTPUT_NOT_PERMUTATION);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "1 2 2"),
                     BAD_OUTPUT_NOT_PERMUTATION);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "1 3 3"),
                     BAD_OUTPUT_NOT_PERMUTATION);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "2 1 1"),
                     BAD_OUTPUT_NOT_PERMUTATION);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "2 1 2"),
                     BAD_OUTPUT_NOT_PERMUTATION);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "2 4 3"),
                     BAD_OUTPUT_NOT_PERMUTATION);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "0 1 3"),
                     BAD_OUTPUT_NOT_PERMUTATION);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "0 1 2"),
                     BAD_OUTPUT_NOT_PERMUTATION);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "0 2 1"),
                     BAD_OUTPUT_NOT_PERMUTATION);
  TestParseAllOutput(inputs, Modify(output_lines, 2, "2 2 2"),
                     BAD_OUTPUT_NOT_PERMUTATION);

  // Operations: too many operations.
  TestParseAllOutput(inputs, Modify(output_lines, 7, "6 1 2 1 2 1 2"),
                     BAD_OUTPUT_TOO_MANY_OPERATIONS);
  TestParseAllOutput(inputs, Modify(output_lines, 7, "5 1 2 1 2 1 "), "");

  // Operations: out of bound.
  TestParseAllOutput(inputs, Modify(output_lines, 7, "5 1 2 1 2 3"),
                     BAD_OUTPUT_OPERATION_OUT_OF_RANGE);
  TestParseAllOutput(inputs, Modify(output_lines, 7, "5 1 2 1 2 0"),
                     BAD_OUTPUT_OPERATION_OUT_OF_RANGE);

  // Test judge.
  TestJudgeAllCases(inputs, output_lines, output_lines, "");
  TestJudgeAllCases(inputs, output_lines, Modify(output_lines, 4, "3 1 1 1"),
                    "");

  TestJudgeAllCases(inputs, output_lines, Modify(output_lines, 4, "1 1"),
                    "Case #1: " + NOT_SORTED);
  TestJudgeAllCases(inputs, output_lines, Modify(output_lines, 5, "1 1"),
                    "Case #1: " + NOT_SORTED);
  TestJudgeAllCases(inputs, output_lines, Modify(output_lines, 6, "2 1 2"),
                    "Case #1: " + NOT_SORTED);
  TestJudgeAllCases(inputs, output_lines, Modify(output_lines, 7, "1 1"),
                    "Case #1: " + NOT_SORTED);
}

int32_t main(int argc, const char* argv[]) {
  if (argc == 2 && string(argv[1]) == "-2") {
    TestLib();
    Test();
    cerr << "All test passed!" << endl;
    return 0;
  }
  if (argc != 4) {
    cerr << "Wrong number of args" << endl;
    return 1;
  }

  ifstream input_file(argv[1]);
  auto input = ParseAllInput(input_file, ParseCaseInput);
  ifstream attempt_file(argv[2]);
  auto attempt = ParseAllOutput(attempt_file, input, ParseCaseOutput);
  ifstream output_file(argv[3]);
  auto correct_output = ParseAllOutput(output_file, input, ParseCaseOutput);
  string e = JudgeAllCases(input, correct_output, attempt, JudgeCase);
  if (e.empty()) return 0;
  Error(e);
}
