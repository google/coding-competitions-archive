#include "recruiting/arena/problem_dev/cocolib/cc/judges/custom_judge.h"

#include <algorithm>
#include <string>
#include <unordered_map>
#include <vector>

#include "recruiting/arena/problem_dev/cocolib/cc/base.h"
#include "recruiting/arena/problem_dev/cocolib/cc/reader.h"

using cocolib::CaseSensitiveStr;           // NOLINT
using cocolib::Int;                        // NOLINT
using cocolib::LenientReader;              // NOLINT
using cocolib::List;                       // NOLINT
using cocolib::Str;                        // NOLINT
using WA = cocolib::WrongAnswerException;  // NOLINT
using JE = cocolib::JudgeErrorException;   // NOLINT

using Input = std::vector<std::string>;

struct Output {
  /**
   * Whether or not the characters in the input words can be permuted such that
   * the list of words is sorted.
   */
  bool possible;
  /**
   * Answer, or empty if no solution exists.
   */
  std::vector<std::string> words;

  bool operator==(const Output& other) const {
    return possible == other.possible && words == other.words;
  }
};

class GameSortPart1ProblemJudge
    : public cocolib::StreamingCustomJudge<Input, Output> {
 public:
  GameSortPart1ProblemJudge() = default;

  /**
   * Expects two lines. First an integer n, then a space separated list of n
   * strings.
   */
  Input ReadCaseInput(LenientReader& reader) override {
    int n = reader.ReadL(Int);
    return reader.ReadL(List(Str, n));
  }

  /**
   * Expect a single line with a verdict. If it is "POSSIBLE" then the following
   * line should contain the solution.
   */
  Output ReadCaseOutput(const Input& input, LenientReader& reader) override {
    std::string verdict = reader.ReadL(Str);
    if (verdict == "possible") {
      return Output{true, reader.ReadL(List(Str, input.size()))};
    } else if (verdict == "impossible") {
      return Output{false, {}};
    } else {
      throw WA{"Unrecognized verdict '", verdict, "'."};
    }
  }

  /**
   * Verifies that a POSSIBLE solution is valid.
   *
   * All IMPOSSIBLE solutions are valid, but they may not be correct.
   */
  void VerifyCaseOutput(const Input& input, const Output& output) override {
    if (output.possible) {
      Assert(input.size() == output.words.size(), "Answer contains ",
             output.words.size(), " words, expected ", input.size(), ".");
      Assert(std::is_sorted(output.words.begin(), output.words.end()),
             "Expected answer to be ordered in non-decreasing order.");

      for (int i = 0; i < (int)output.words.size(); ++i) {
        std::string s_in = input[i], s_out = output.words[i];
        std::sort(s_in.begin(), s_in.end());
        std::sort(s_out.begin(), s_out.end());

        Assert(s_in == s_out, "Word '", output.words[i],
               "' is not a permutation of the input word '", input[i], "'.");
      }
    }
  }

  /**
   * Verifies that the user's verdict matches that of the judge.
   *
   * If the user's output has been verified and the verdicts match, then the
   * solution is correct.
   */
  void JudgeCase(const Input& input, const Output& judge_output,
                 const Output& user_output) override {
    if (judge_output.possible) {
      Assert(user_output.possible, "Expected POSSIBLE but got IMPOSSIBLE.");
    } else if (user_output.possible) {
      throw JE{"User found an answer but judge said IMPOSSIBLE"};
    }
  };
};

COCOLIB_MULTIPLE_CASES_MAIN(GameSortPart1ProblemJudge)