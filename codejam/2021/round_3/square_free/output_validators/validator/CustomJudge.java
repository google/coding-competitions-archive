import static cocolib.CustomJudgeInterface.judgeError;
import static cocolib.CustomJudgeInterface.wrongAnswer;
import static cocolib.constraints.StringConstraint.alphabet;
import static cocolib.constraints.StringConstraint.length;
import static java.lang.Math.min;

import cocolib.CustomJudgeInterface;
import cocolib.JudgeErrorException;
import cocolib.Reader;
import cocolib.WrongAnswerException;
import java.io.IOException;

public final class CustomJudge
    implements CustomJudgeInterface<CustomJudge.Input, CustomJudge.Output> {

  public static void main(String[] args) {
    new CustomJudge().runCustomJudgeMultipleCases(args);
  }

  @Override
  public Input readCaseInput(Reader reader) throws IOException {
    Input input = new Input();
    input.r = reader.readInt();
    input.c = reader.readInt();
    input.s = reader.readIntArray(input.r);
    input.d = reader.readIntArray(input.c);
    return input;
  }

  @Override
  public void judgeCase(Input input, Output judgeOutput, Output contestantOutput)
      throws WrongAnswerException, JudgeErrorException {
    if (judgeOutput.isPossible == contestantOutput.isPossible) {
      return;
    }
    if (judgeOutput.isPossible) {
      wrongAnswer("Judge says POSSIBLE but contestant printed IMPOSSIBLE");
    }
    if (contestantOutput.isPossible) {
      judgeError("Judge says IMPOSSIBLE but contestant provided a valid solution");
    }
  }

  @Override
  public Output readAndVerifyCaseOutput(Input input, Reader reader)
      throws IOException, WrongAnswerException {
    Output output = new Output();

    // Read POSSIBLE / IMPOSSIBLE.
    output.isPossible =
        reader.readStringOneOf("isPossible", new String[] {"POSSIBLE", "IMPOSSIBLE"}) == 0;
    if (!output.isPossible) {
      return output;
    }

    output.grid = new char[input.r][];
    int[] rowCounts = new int[input.r];
    int[] colCounts = new int[input.c];
    // Read the grid and keep track of the counts.
    for (int r = 0; r < input.r; r++) {
      output.grid[r] = reader.readString("line", alphabet("/\\"), length(input.c)).toCharArray();
      for (char c = 0; c < input.c; c++) {
        if (output.grid[r][c] == '/') {
          rowCounts[r]++;
          colCounts[c]++;
        }
      }
    }

    // Verify row counts.
    for (int r = 0; r < input.r; r++) {
      if (rowCounts[r] != input.s[r]) {
        wrongAnswer("Expected exactly %d /s in row %d but found %d", input.s[r], r, rowCounts[r]);
      }
    }
    // Verify column counts.
    for (int c = 0; c < input.c; c++) {
      if (colCounts[c] != input.d[c]) {
        wrongAnswer(
            "Expected exactly %d /s in column %d but found %d", input.d[c], c, colCounts[c]);
      }
    }

    checkForSquares(output.grid);
    return output;
  }

  static void checkForSquares(char[][] grid) throws WrongAnswerException {
    int nr = grid.length;
    int nc = grid[0].length;
    for (int len = 1; len <= min(nr, nc); len++) {
      for (int sr = 0; sr < nr; sr++) {
        int er = sr + len * 2 - 1;
        if (er >= nr) {
          break;
        }
        outer:
        for (int sc = 0; sc < nc; sc++) {
          int ec = sc + len * 2 - 1;
          if (ec >= nc) {
            break;
          }
          for (int i = 0; i < len; i++) {
            if (grid[sr + len - 1 - i][sc + i] != '/'
                || grid[sr + len + i][sc + i] != '\\'
                || grid[sr + i][sc + len + i] != '\\'
                || grid[sr + len * 2 - 1 - i][sc + len + i] != '/') {
              continue outer;
            }
          }
          wrongAnswer("The grid is not square free!");
        }
      }
    }
  }

  static class Input {
    int r;
    int c;
    int[] s;
    int[] d;
  }

  static class Output {
    boolean isPossible;
    char[][] grid;
  }
}
