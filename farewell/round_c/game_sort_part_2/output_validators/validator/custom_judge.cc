#include "recruiting/arena/problem_dev/cocolib/cc/judges/custom_judge.h"

#include <algorithm>
#include <string>
#include <tuple>
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

struct Input {
  int p;
  std::string s;

  bool operator==(const Input& other) const {
    return p == other.p && s == other.s;
  }
};

struct Output {
  /**
   * Whether or not the string in the input can be cut in p words, such that
   * is impossible to independently permute the letters in each word to make
   * the list of words sorted.
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

class GameSortPart2ProblemJudge
    : public cocolib::StreamingCustomJudge<Input, Output> {
 public:
  GameSortPart2ProblemJudge() = default;

  /**
   * Expects one line containing an integer and a string.
   */
  Input ReadCaseInput(LenientReader& reader) override {
    std::tuple<int, std::string> input = reader.ReadL(Int, CaseSensitiveStr);
    return Input{std::get<0>(input), std::get<1>(input)};
  }

  /**
   * Expect a single line with a verdict.
   * If it is "POSSIBLE" then the following line should contain the solution.
   */
  Output ReadCaseOutput(const Input& input, LenientReader& reader) override {
    std::string verdict = reader.ReadL(Str);
    if (verdict == "possible") {
      return Output{true, reader.ReadL(List(CaseSensitiveStr, input.p))};
    } else if (verdict == "impossible") {
      return Output{false, {}};
    } else {
      throw WA{"Unrecognized verdict '", verdict, "'."};
    }
  }

  /**
   * Find the smallest permutation of 'cur' that is greater than or equal
   * to 'prev'. Returns an empty string if not possible.
   */
  std::string smallest_valid_permutation(const std::string& prev, const std::string& cur) {
    std::vector<int> freq(26, 0);
    for(int i = 0; i < (int)cur.size(); ++i) {
      freq[cur[i]-'A']++;
    }

    // Match the longest possible prefix
    int pos = 0;
    while(pos < (int)prev.size() && freq[prev[pos]-'A'] > 0) {
      freq[prev[pos]-'A']--;
      pos++;
    }

    std::string ans = prev.substr(0, pos);
    bool ok = true;
    if(pos < (int)prev.size()) {
      ok = false;
      ans = "";
      // Reduce the matched prefix one by one until being able to
      // generate a valid permutation
      while(pos >= 0 && !ok) {
        for(int i = prev[pos]-'A'+1; i < 26; ++i) {
          if(!ok && freq[i] > 0) {
            ok = true;
            freq[i]--;
            ans = prev.substr(0, pos) + char('A'+i);
            pos++;
            break;
          }
        }
        if(!ok) {
          pos--;
          if(pos >= 0){
            freq[prev[pos]-'A']++;
          }
        }
      }
    }
    if(ok) {
      for(int i = 0; i < 26; ++i) {
        for(int _ = 0; _ < freq[i]; ++_) {
          ans.push_back(char('A'+i));
        }
      }
    }

    return ans;
  }

  // Find a way Bob can win. Returns an empty vector if not possible.
  std::vector<std::string> playAsBob(const std::vector<std::string>& words) {
    std::string prev = "";
    std::vector<std::string> ans;
    for(int i = 0; i < (int)words.size(); ++i) {
      prev = smallest_valid_permutation(prev, words[i]);
      if(prev.empty()) {
        return std::vector<std::string>();
      }
      ans.push_back(prev);
    }
    return ans;
  }

  /**
   * Verifies that a POSSIBLE solution is valid.
   *
   * All IMPOSSIBLE solutions are valid, but they may not be correct.
   */
  void VerifyCaseOutput(const Input& input, const Output& output) override {
    if (output.possible) {
      Assert(input.p == output.words.size(), "Answer contains ",
             output.words.size(), " words, expected ", input.p, ".");

      int slen = 0;
      for (int i = 0; i < (int)output.words.size(); ++i) {
        slen += (int)output.words[i].size();
      }
      std::string s_out = "";
      s_out.reserve(slen);
      for (int i = 0; i < (int)output.words.size(); ++i) {
        s_out += output.words[i];
      }
      Assert(input.s == s_out,
             "Answer is not a valid separation of the input string.");
      
      // Verify bob cannot win
      Assert(playAsBob(output.words).empty(), 
             "Answer does not guarantee Alice will win.");
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

COCOLIB_MULTIPLE_CASES_MAIN(GameSortPart2ProblemJudge)