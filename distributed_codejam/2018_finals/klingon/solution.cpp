#include <cstdio>
#include <vector>
#include <utility>
#include "message.h"  // NOLINT
#include "klingon.h"  // NOLINT

typedef long long ll;  // NOLINT

int A;
int W;
int Q;
// My node ID
int M;
// Number of nodes.
int N;
// ID of the current "master" node. We'll rotate the responsibility of being
// the master to ignore the "number of messages sent" limit.
int master;

// The answers in the "correct" and "incorrect" tables are the values you should
// provide to the "doAnswer" function, not the actual answers.

// The correct answers for the questions we already know the correct answers to.
int correct[26000];
// Known incorrect answers to the questions (these are easier to get).
int incorrect[26000];
// The number of known correct answers.
int n_correct = 0;
// The final answer to the problem.
int code;
// The correct question-answer pairs found in the search we're currently doing.
std::vector<std::pair<int, int>> current_correct;

// Semi-randomize our answers. While it's a pretty weak randomness, it should be
// strong enough that a single node should be somewhat unlikely to hit a very
// large number of correct answers.
inline int Transform(int a, int q) {
  return (a + 1 + ((q * (q ^ 12345) + (q/3)))) % A;
}

int doAnswer(int a, int q) {
  return Answer(Transform(a, q));
}

// Provide the answers to all the questions we know the answers to.
void begin() {
  for (int q = 0; q < n_correct; ++q) {
    assert(doAnswer(correct[q], q) == 0);
  }
}

// Answer a consistent whatever, until we either reset the game, or (somewhat
// accidentally) win. If we win, we'll store the secret code on the "code"
// variable, and return -1, otherwise we'll return how many questions we needed
// to ask to reset the game.
// If we were able to incorrectly answer, we would just answer questions
// incorrectly here for as long as needed, and we would know that the number of
// incorrect previously is W+1 minus the one of incorrect answers we needed
// here. Unfortunately, we don't know incorrect answers, and so we answer at
// random, assuming we'll mostly hit incorrect answers.
// Leaves the game in the reset state.
ll finish() {
  ll ans = 0;
  int q;
  // We need any reasonably random way of generating answers that is unlikely
  // to hit a long streak of correct answers.
  for (q = 0; ans == 0; q++) {
    ans = doAnswer(0, q);
  }
  if (ans != -1) {
    code = ans;
    return -1;
  }
  return q;
}

// Will provide the given answer in the range [from, to). Before n_correct, will
// provide correct answers. In the range [n_correct, n_correct+W+1), except
// [from, to), will provide incorrect answers. After n_correct+W+1, will use
// finish() to provide answers, and will return 1+finish(), or 0 if the call to
// finish() was not needed. Will return -1 and store the code on "code" if we
// accidentally finish the game.
// The key observation here is that if we return a positive number, at least one
// of the answers in the [from, to) range had to be correct - otherwise, we'd
// have given incorrect answers in the whole n_correct, n_correct + W + 1 range,
// and we wouldn't have needed the call to finish. And conversely, if this
// returns zero, we know all the answers in the [from, to) range were incorrect.
//
// Leaves the game in a reset state.
int answer_in_range(int a, int from, int to) {
  begin();
  int ans = -1;
  assert(from >= n_correct);
  assert(to <= n_correct + W + 1);
  for (int q = n_correct; q < from; ++q) {
    assert(doAnswer(incorrect[q], q) == 0);
  }
  for (int q = from; q < to; ++q) {
    ans = doAnswer(a, q);
    if (ans > 0) {
      code = ans;
      return -1;
    }
  }
  for (int q = to; q < n_correct + W + 1; ++q) {
    ans = doAnswer(incorrect[q], q);
    if (ans > 0) {
      code = ans;
      return -1;
    }
  }
  // Only the last answer can possibly be -1, since it's the W+1st unknown
  // answer.
  if (ans == -1) {
    return 0;
  }
  int result = finish();
  if (result == -1) {
    return -1;
  }
  return result + 1;
}

// Assumes that running answer_in_range(a, from, to) returns cur_num_over, and
// that cur_num_over is greater than zero (that is, that "a" is a correct answer
// to some question in the [from, to) range). Will fill in the current_correct
// vector with all the (q, a) pairs where q is in the [from, to) range, and a
// is the correct answer to q.
// Leaves the game in a reset state.
void fill_in_answers_binary(int a, int cur_num_over, int from, int to) {
  // If there is a correct answer in the range, and the range is of length one,
  // we can pinpoint the correct answer pretty easily :)
  if (to - from == 1) {
    current_correct.push_back(std::make_pair(from, a));
    return;
  }
  // If the range is longer, split it in half, and check both parts.
  int med = (from + to) / 2;
  int required_to_finish = answer_in_range(a, from, med);
  // The assumption is we already ran the game answering "a" in the whole
  // [num_correct, num_correct+W+1) range, and didn't finish the game - and now
  // we will give no fewer incorrect answers than that run-through. So, we can't
  // finish the game.
  assert(required_to_finish >= 0);
  // If there were no correct answers in the range, search the latter range.
  if (required_to_finish == 0) {
    fill_in_answers_binary(a, cur_num_over, med, to);
    return;
  }
  // If we required the same finish length, it means all the correct answers are
  // in this range, so search it.
  if (required_to_finish == cur_num_over) {
    fill_in_answers_binary(a, cur_num_over, from, med);
    return;
  }
  // Now, we have correct answers in both the sub-ranges. First, let's search
  // the first range (since we know how many answers were required to finish).
  fill_in_answers_binary(a, required_to_finish, from, med);
  // We also need to know how many answers are required to finish the second
  // half.
  required_to_finish = answer_in_range(a, med, to);
  assert(required_to_finish >= 0);
  fill_in_answers_binary(a, required_to_finish, med, to);
}

// We try to identify incorrect answers for all the questions in the
// [num_correct, num_correct + W + 1) range.
// We'll do this by first answering "0" to all the questions (thanks to the
// pseudorandomization we do, this won't be correct too often), and checking
// how many extra answers we had to provide.
// Then, we will, for each question in the range, switch the answer to that one
// question to "1", and see what happens to the number of extra answers. If the
// number of extra answers goes up, it means that "1" is correct, and "0" isn't.
// If it goes down, "0" is correct, and "1" isn't. If it stays the same, they're
// equally correct, which is to say, they're both incorrect (since they can't be
// both correct). So, in each case, we learn an incorrect answer.
// We will do this in a distributed fashion (although it might be that doing it
// on every node would run in time) - each node checking the answers in some
// sub-range of [num_correct, num_correct + W + 1), sending the indices of the
// answers where "0" was correct to the master, and receiving the full list of
// the answers where "0" was correct back.
// Leaves the incorrect array filled in with incorrect answers up to num_correct
// + W inclusive; and the game in a reset state.
int identify_all_incorrect() {
  // We'll reuse the "answer_in_range" method. This method answers with the
  // answer provided in the provided range, and with the answer from
  // "incorrect" outside this range. We'll cheat, fill in incorrect with
  // 0, and use it that way (even though "incorrect" will not necessarily all be
  // incorrect this way). We'll store the indices on which it happens that a
  // is correct on a separate vector.
  std::vector<int> zero_correct_indices;
  int beg = M * (W + 1) / N;
  int end = (M + 1) * (W + 1) / N;
  for (int q = n_correct; q < n_correct + W + 1; ++q) incorrect[q] = 0;
  bool found_solution = false;
  int over_zero = answer_in_range(0, n_correct, n_correct);
  if (over_zero == -1) {
    found_solution = true;
  }
  if (!found_solution) {
    for (int q = n_correct + beg; q < n_correct + end; ++q) {
      int res = answer_in_range(1, q, q+1);
      // We might accidentally finish the game. It's very unlikely, but it's
      // theoretically possible.
      if (res == -1) {
        found_solution = true;
        break;
      }
      if (res < over_zero) zero_correct_indices.push_back(q);
    }
  }
  // Everybody sends their data to the master.
  PutChar(master, found_solution);
  if (found_solution) {
    PutInt(master, code);
  } else {
    PutInt(master, zero_correct_indices.size());
    for (int q : zero_correct_indices) {
      PutInt(master, q);
    }
  }
  Send(master);
  // Master receives and accumulates the data. If there's a correct answer,
  // master prints it.
  if (M == master) {
    found_solution = false;
    zero_correct_indices.clear();
    for (int n = 0; n < N; ++n) {
      Receive(n);
      if (GetChar(n)) {
        int sol = GetInt(n);
        if (!found_solution) printf("%d\n", sol);
        found_solution = true;
      } else {
        int cnt = GetInt(n);
        for (int i = 0; i < cnt; ++i) {
          zero_correct_indices.push_back(GetInt(n));
        }
      }
    }
    for (int n = 0; n < N; ++n) {
      PutChar(n, found_solution);
      if (!found_solution) {
        PutInt(n, zero_correct_indices.size());
        for (int q : zero_correct_indices) {
          PutInt(n, q);
        }
      }
      Send(n);
    }
  }
  // Everybody receives correct answers.
  Receive(master);
  if (GetChar(master)) {
    // The master received the correct answer and printed it out.
    return -1;
  } else {
    int cnt = GetInt(master);
    for (int i = 0; i < cnt; ++i) {
      incorrect[GetInt(master)] = 1;
    }
  }
  master = (master + 1) % N;
  return 0;
}

int main() {
  A = GetNumberOfPossibleAnswers();
  W = GetAllowedNumberOfWrongAnswers();
  Q = GetNumberOfQuestions();
  M = MyNodeId();
  N = NumberOfNodes();
  master = 0;
  while (true) {
    // First, try to identify an incorrect answer. Note that this isn't required
    // if A > W - we could just find an answer that's fully incorrect - but that
    // would require one extra round of communication, and extra code. Instead,
    // let's just always run the default search-for-incorrect code.
    if (identify_all_incorrect() == -1) return 0;
    // Now, that we have an incorrect answer for every question in the range,
    // let's try to identify the correct answers.
    int beg = (M * A) / N;
    int end = ((M + 1) * A) / N;
    current_correct.clear();
    bool solution_found = false;
    for (int a = beg; a < end; ++a) {
      int num_over = answer_in_range(a, n_correct, n_correct + W + 1);
      if (num_over == -1) {
        solution_found = true;
        break;
      }
      if (num_over) {
        fill_in_answers_binary(a, num_over, n_correct, n_correct + W + 1);
      }
    }
    // Now, send the data to the master.
    PutChar(master, solution_found);
    if (solution_found) {
      PutInt(master, code);
    } else {
      PutInt(master, current_correct.size());
      for (auto p : current_correct) {
        PutInt(master, p.first);
        PutInt(master, p.second);
      }
    }
    Send(master);
    // Receive and aggregate on the master.
    if (M == master) {
      solution_found = false;
      current_correct.clear();
      for (int n = 0; n < N; ++n) {
        Receive(n);
        if (GetChar(n)) {
          int sol = GetInt(n);
          if (!solution_found) printf("%d\n", sol);
          solution_found = true;
        } else {
          int cnt = GetInt(n);
          for (int i = 0; i < cnt; ++i) {
            int q = GetInt(n);
            int a = GetInt(n);
            current_correct.push_back(std::make_pair(q, a));
          }
        }
      }
      // Resend back to everybody.
      for (int n = 0; n < N; ++n) {
        PutChar(n, solution_found);
        if (!solution_found) {
          assert(current_correct.size() == W + 1);
          for (auto p : current_correct) {
            PutInt(n, p.first);
            PutInt(n, p.second);
          }
        }
        Send(n);
      }
    }
    // Everybody receives from master, and updates their information about
    // correct answers.
    Receive(master);
    if (GetChar(master)) return 0;
    // Note - we could decrease the network traffic a bit by resorting the data
    // on the master, and just sending the answers in order, without the
    // questions.
    for (int ans = 0; ans < W + 1; ++ans) {
      int q = GetInt(master);
      int a = GetInt(master);
      correct[q] = a;
    }
    n_correct += (W + 1);
    master = (master + 1) % N;
  }
  assert(false);  // Unreachable code.
  return 0;
}
