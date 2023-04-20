// Note that all tests in this file operate with uppercase letters, but in fact
// we are converting everyting to lowercase right after reading input/output,
// and the judge is expected to be case-insensitive.
#include <bits/stdc++.h>
using namespace std;

template <typename T>
ostream& operator<<(ostream& out, const vector<T>& v) {
  out << "[";
  for (const T& t : v) out << t << ", ";
  return out << "]";
}

template <typename T>
bool Eq(const T& t1, const T& t2) {
  if (t1 != t2)
    cerr << "Expected " << t1 << " and " << t2 << " to be equal" << endl;
  return t1 == t2;
}

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
  for (int i = 1; i < ss.size(); ++i)
    if (ss[i] < '0' || ss[i] > '9') Error(error);
  string s;
  if (!ss.empty()) {
    int first_digit = 0;
    if (ss[0] == '-') {
      s += '-';
      first_digit = 1;
    }
    while (first_digit < ss.size() - 1 && ss[first_digit] == '0') ++first_digit;
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

vector<vector<string>> ReadAndTokenizeFileLines(const string& filename) {
  ifstream in(filename);
  string s;
  vector<vector<string>> r;
  while (getline(in, s)) {
    vector<string> tokens = Tokenize(s);
    if (!tokens.empty()) r.push_back(tokens);
  }
  return r;
}

vector<vector<vector<string>>> SplitCases(const vector<vector<string>>& lines) {
  vector<vector<vector<string>>> cases;
  for (const vector<string>& line : lines) {
    if (line.size() >= 2 && line[0] == "case" &&
        line[1][0] == '#') {  // New case line, like python judges define it.
      if (line[1].size() < 3 || line[1][line[1].size() - 1] != ':')
        Error("Bad format in case line");
      const string case_num = line[1].substr(1, line[1].size() - 2);
      if (ParseInt(case_num) != cases.size() + 1) {
        Error(string("Found case: ") + Truncate(case_num) +
              ", expected: " + Strint(cases.size() + 1));
      }
      vector<string> new_line(line);
      new_line.erase(new_line.begin(), new_line.begin() + 2);
      cases.push_back(vector<vector<string>>(1, new_line));
    } else {
      if (cases.empty()) Error("First line doesn't start with case #1:");
      cases.back().push_back(line);
    }
  }
  return cases;
}

void TestSplitCases() {
  auto SplitLines = [](const vector<string>& v) {
    vector<vector<string>> r;
    r.reserve(v.size());
    for (string s : v) r.push_back(Tokenize(s));
    return SplitCases(r);
  };
  assert(Eq(SplitLines({"Case   #1:  A  "}), {{{"a"}}}));
  assert(Eq(SplitLines({"Case\t#1:  A  ", "  cASE \t\t #2:\t   b  c  "}),
            {{{"a"}}, {{"b", "c"}}}));
  assert(Eq(SplitLines({"Case #01:  a  ", "x   y", "  z w ",
                        "CASE #0000002:", "   b  c  ", "WWWW"}),
            {{{"a"}, {"x", "y"}, {"z", "w"}}, {{}, {"b", "c"}, {"wwww"}}}));
  assert(Eq(SplitLines({"Case #1:", "", "  z w ", "CASE #2:", "", ""}),
            {{{}, {}, {"z", "w"}}, {{}, {}, {}}}));
  AssertError(SplitLines({"Case #1:", "case", "#1:", "CASE # 2:", "case #3:"}),
              "Bad format in case line");
  AssertError(SplitLines({"Case #1:", "case", "#1:", "CASE #2 :", "case #3:"}),
              "Bad format in case line");
  AssertError(SplitLines({"Case #1:", "case #1:"}),
              "Found case: 1, expected: 2");
  AssertError(SplitLines({"Case #2:", "case #1:"}),
              "Found case: 2, expected: 1");
  AssertError(SplitLines({"Case #0:", "case #1:"}),
              "Found case: 0, expected: 1");
  AssertError(SplitLines({"Case #-1:", "case #1:"}),
              "Found case: -1, expected: 1");
  AssertError(SplitLines({"Case #xyz:", "case #1:"}),
              "Not an integer in range: xyz");
  AssertError(SplitLines({"Case #ONE:", "case #1:"}),
              "Not an integer in range: one");
  AssertError(SplitLines({"Case #1.0:", "case #1:"}),
              "Not an integer in range: 1.0");
  AssertError(SplitLines({"Case #1:", "case", "#1:", "case #3:"}),
              "Found case: 3, expected: 2");
  AssertError(SplitLines({"Case #1:", "case", "#1:", "case #02:", "case #2:"}),
              "Found case: 2, expected: 3");
  AssertError(SplitLines({"Case#1:A"}),
              "First line doesn't start with case #1:");
  AssertError(SplitLines({"Case#1: A"}),
              "First line doesn't start with case #1:");
  AssertError(SplitLines({"Case #1:A"}), "Bad format in case line");
  AssertError(SplitLines({"Case #: A"}), "Bad format in case line");
  assert(Eq(SplitLines({"Case #1: A B", "Case#2:A"}),
            {{{"a", "b"}, {"case#2:a"}}}));
  assert(Eq(SplitLines({"Case #1: A B", "Case#2: A"}),
            {{{"a", "b"}, {"case#2:", "a"}}}));
  AssertError(SplitLines({"Case #1: A B", "Case #2:A"}),
              "Bad format in case line");
  AssertError(SplitLines({"Case # 1: A"}), "Bad format in case line");
  AssertError(SplitLines({"Case #1 : A"}), "Bad format in case line");
  AssertError(SplitLines({"Case# 1: A"}),
              "First line doesn't start with case #1:");
  AssertError(SplitLines({"Cases #1: A"}),
              "First line doesn't start with case #1:");
  assert(Eq(SplitLines({"Case #01: A"}), {{{"a"}}}));
  AssertError(SplitLines({"", "Cases #1: A"}),
              "First line doesn't start with case #1:");
}

template <typename T>
vector<T> ParseAllInput(const string& filename, T ParseCaseInputF(istream&)) {
  ifstream in(filename);
  int t;
  in >> t;
  vector<T> v(t);
  for (int i = 0; i < t; ++i) v[i] = ParseCaseInputF(in);
  return v;
}

template <typename U>
vector<U> ParseAllOutput(const string& filename,
                         U ParseCaseOutputF(const vector<vector<string>>&)) {
  vector<vector<vector<string>>> tokenized_lines =
      SplitCases(ReadAndTokenizeFileLines(filename));
  vector<U> v(tokenized_lines.size());
  for (int i = 0; i < tokenized_lines.size(); ++i)
    v[i] = ParseCaseOutputF(tokenized_lines[i]);
  return v;
}

template <typename T, typename U>
string JudgeAllCases(const vector<T>& input, const vector<U>& correct_output,
                     const vector<U>& attempt,
                     string JudgeCase(const T&, const U&, const U&)) {
  if (attempt.size() != input.size())
    Error(string("Wrong number of cases in attempt: ") +
          Strint(attempt.size()) + ", expected: " + Strint(input.size()));
  for (int i = 0; i < input.size(); ++i) {
    string e = JudgeCase(input[i], correct_output[i], attempt[i]);
    if (e.empty()) continue;
    ostringstream out;
    out << "Case #" << (i + 1) << ": " << e;
    return out.str();
  }
  return "";
}

string JudgeCaseTest(const int& n, const int& m, const int& o) {
  if (n != o) return Strint(o) + " not equal to input: " + Strint(n);
  return "";
};

void TestJudgeAllCases() {
  AssertError(JudgeAllCases({1}, {1}, {1, 2}, JudgeCaseTest),
              "Wrong number of cases in attempt: 2, expected: 1");
  AssertError(JudgeAllCases({1, 2}, {1, 2}, {1}, JudgeCaseTest),
              "Wrong number of cases in attempt: 1, expected: 2");
  AssertError(JudgeAllCases({1, 2}, {1, 2}, {}, JudgeCaseTest),
              "Wrong number of cases in attempt: 0, expected: 2");
  assert(JudgeAllCases({1}, {1}, {1}, JudgeCaseTest) == "");
  assert(JudgeAllCases({1}, {1}, {2}, JudgeCaseTest) ==
         "Case #1: 2 not equal to input: 1");
  assert(JudgeAllCases({1, 1}, {1, 1}, {2, 2}, JudgeCaseTest) ==
         "Case #1: 2 not equal to input: 1");
  assert(JudgeAllCases({1, 2}, {1, 2}, {1, 2}, JudgeCaseTest) == "");
  assert(JudgeAllCases({1, 2}, {1, 2}, {1, 1}, JudgeCaseTest) ==
         "Case #2: 1 not equal to input: 2");
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
  int R;
  int C;
  vector<string> wall;
};

typedef string CaseOutput;

CaseInput ParseCaseInput(istream& in) {
  int R, C;
  in >> R >> C;
  vector<string> wall(R);
  for (int i = 0; i < R; i++) {
    in >> wall[i];
    wall[i] = Lowercase(wall[i]);
  }
  return {
    .R = R,
    .C = C,
    .wall = wall
  };
}

void TestParseCaseInput() {
  string input = "2 3\n"
                 "ABC\n"
                 "DEF";
  istringstream in(input);
  CaseInput parsed_input = ParseCaseInput(in);

  assert(parsed_input.R == 2);
  assert(parsed_input.C == 3);
  vector<string> wall = {"abc", "def"};
  assert(parsed_input.wall == wall);
}

CaseOutput ParseCaseOutput(const vector<vector<string>>& lines) {
  if (lines.size() != 1) Error("Wrong number of lines in case output");
  if (lines[0].size() != 1) Error("Wrong number of tokens in case output");
  return lines[0][0];
}

void TestParseCaseOutput() {
  assert(ParseCaseOutput({{"-1"}}) == "-1");
  assert(ParseCaseOutput({{"ABC"}}) == "ABC");
  AssertError(ParseCaseOutput({{"ABC", "DEF"}}),
              "Wrong number of tokens in case output");
  AssertError(ParseCaseOutput({{"ABC"}, {"DEF"}}),
              "Wrong number of lines in case output");
}

string VerifyCorrectness(const CaseInput& input, const CaseOutput& output) {
  set<char> polyominos;
  for (string s : input.wall) {
    for (char c : s) {
      polyominos.insert(c);
    }
  }

  set<char> output_chars;
  for (char c : output) {
    if (polyominos.find(c) == polyominos.end()) {
      return "Answer should only contain letters from the input";
    }
    if (output_chars.find(c) != output_chars.end()) {
      return "Answer should not contain repeated letters";
    }
    output_chars.insert(c);
  }

  if (output_chars != polyominos) {
    return "Answer should contain all letters in input";
  }

  // squares is an RxC grid that contains 1 if a square is placed, 0 otherwise.
  vector<int> empty_row(input.C, 0);
  vector<vector<int>> squares(input.R, empty_row);

  for (char c : output) {
    // Find all occurences of c in input and populate squares.
    for (int i = 0; i < input.R; i++) {
      for (int j = 0; j < input.C; j++) {
        if (input.wall[i][j] != c) continue;  // Ignore different letters.
        assert(squares[i][j] == 0);  // Sanity check: No repeated letters.
        squares[i][j] = 1;
      }
    }

    // For each 1 in squares, make sure it's stable (1 or ground under it).
    for (int i = 0; i < input.R - 1; i++) {
      // We don't check last row because it's always stable.
      for (int j = 0; j < input.C; j++) {
        if (squares[i][j] == 0) continue;  // Ignore zeros.
        if (squares[i+1][j] == 1) continue;  // Stable.
        stringstream ss;
        ss << "Inserting polyomino " << input.wall[i][j] << " is unstable";
        return ss.str();
      }
    }
  }

  // Sanity check: Polyominos fill entire rectangle.
  for (int i = 0; i < input.R; i++) {
      for (int j = 0; j < input.C; j++) {
        assert(squares[i][j] == 1);
      }
  }

  return "";
}

string JudgeCase(const CaseInput& input, const CaseOutput& correct_output,
                 const CaseOutput& attempt) {
  // Judge correct output.
  if (correct_output != "-1") {
    string s = VerifyCorrectness(input, correct_output);
    if (!s.empty()) return "Correct output failed judging:\n" + s;
  }

  // Handle these cases first.
  if (correct_output == "-1" && attempt == "-1") {
    return "";
  } else if (correct_output == "-1") {
    return "Answer should be -1";
  } else if (attempt == "-1") {
    return "Answer should not be -1";
  }

  assert(correct_output != "-1");
  assert(attempt != "-1");

  return VerifyCorrectness(input, attempt);
}

void Test() {
  TestParseCaseInput();
  TestParseCaseOutput();

  CaseInput input;
  input = {
    .R = 4,
    .C = 6,
    .wall = {{"ZOAAMM"},
             {"ZOAOMM"},
             {"ZOOOOM"},
             {"ZZZZOM"}}
  };
  assert(JudgeCase(input, "ZOAM", "ZOAM") == "");
  assert(JudgeCase(input, "ZOAM", "-1") == "Answer should not be -1");
  assert(JudgeCase(input, "ZOAM", "ZOMA") == "");
  assert(JudgeCase(input, "ZOAM", "YZOAM") ==
         "Answer should only contain letters from the input");
  assert(JudgeCase(input, "ZOAM", "12345") ==
         "Answer should only contain letters from the input");
  assert(JudgeCase(input, "ZOAM", "ZZOAM") ==
         "Answer should not contain repeated letters");
  assert(JudgeCase(input, "ZOAM", "OAM") ==
         "Answer should contain all letters in input");
  assert(JudgeCase(input, "ZOAM", "AZOM") ==
         "Inserting polyomino A is unstable");
  assert(JudgeCase(input, "AZOM", "AZOM") ==
         "Correct output failed judging:\nInserting polyomino A is unstable");

  input = {
    .R = 4,
    .C = 4,
    .wall = {{"XXOO"},
             {"XFFO"},
             {"XFXO"},
             {"XXXO"}}
  };
  assert(JudgeCase(input, "-1", "-1") == "");
  assert(JudgeCase(input, "-1", "XFO") == "Answer should be -1");
  assert(JudgeCase(input, "XFO", "-1") ==
         "Correct output failed judging:\nInserting polyomino X is unstable");

  input = {
    .R = 5,
    .C = 3,
    .wall = {{"XXX"},
             {"XPX"},
             {"XXX"},
             {"XJX"},
             {"XXX"}}
  };
  assert(JudgeCase(input, "-1", "-1") == "");
  assert(JudgeCase(input, "-1", "XPJ") == "Answer should be -1");
  assert(JudgeCase(input, "XPJ", "-1") ==
         "Correct output failed judging:\nInserting polyomino X is unstable");

  input = {
    .R = 3,
    .C = 10,
    .wall = {{"AAABBCCDDE"},
             {"AABBCCDDEE"},
             {"AABBCCDDEE"}}
  };
  assert(JudgeCase(input, "EDCBA", "EDCBA") == "");
  assert(JudgeCase(input, "EDCBA", "-1") == "Answer should not be -1");
  assert(JudgeCase(input, "EDCBA", "EDCAB") ==
         "Inserting polyomino A is unstable");
}

int main(int argc, const char* argv[]) {
  if (argc == 2 && string(argv[1]) == "-2") {
    TestLib();
    Test();
    cerr << "All tests passed!" << endl;
    return 0;
  }
  if (argc != 4) return 1;
  auto input = ParseAllInput(argv[1], ParseCaseInput);
  auto attempt = ParseAllOutput(argv[2], ParseCaseOutput);
  auto correct_output = ParseAllOutput(argv[3], ParseCaseOutput);
  string e = JudgeAllCases(input, correct_output, attempt, JudgeCase);
  if (e.empty()) return 0;
  Error(e);
}
