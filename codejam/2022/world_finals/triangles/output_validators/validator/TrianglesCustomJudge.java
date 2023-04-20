import static cocolib.CustomJudgeInterface.judgeError;
import static cocolib.CustomJudgeInterface.wrongAnswer;

import cocolib.CustomJudgeInterface;
import cocolib.JudgeErrorException;
import cocolib.Reader;
import cocolib.WrongAnswerException;
import java.io.IOException;
import java.util.HashSet;

public final class TrianglesCustomJudge
    implements CustomJudgeInterface<TrianglesCustomJudge.Input, TrianglesCustomJudge.Output> {

  static class Input {
    int n;
    Vec[] ps;
  }

  static class Output {
    Vec[][] tris;
  }

  public static void main(String[] args) {
    new TrianglesCustomJudge().runCustomJudgeMultipleCases(args);
  }

  @Override
  public Input readCaseInput(Reader reader) throws IOException {
    Input input = new Input();
    input.n = reader.readInt();
    input.ps = new Vec[input.n];
    for (int i = 0; i < input.n; i++) {
      input.ps[i] = new Vec(reader.readLong(), reader.readLong());
    }
    return input;
  }

  @Override
  public void judgeCase(Input input, Output judgeOutput, Output contestantOutput)
      throws WrongAnswerException, JudgeErrorException {
    if (judgeOutput.tris.length > contestantOutput.tris.length) {
      wrongAnswer(
          "Judge provides %d triangles but contestant only provides %d",
          judgeOutput.tris.length, contestantOutput.tris.length);
    } else if (judgeOutput.tris.length < contestantOutput.tris.length) {
      judgeError(
          "Judge provides only %d triangles but contestant provides %d",
          judgeOutput.tris.length, contestantOutput.tris.length);
    }
  }

  @Override
  public Output readCaseOutput(Input input, Reader reader)
      throws IOException, WrongAnswerException {
    Output output = new Output();

    int numTriangles = reader.readInt();
    if (numTriangles < 0 || numTriangles > input.n / 3) {
      wrongAnswer(
          "Expected number of triangles to be in range [%d, %d] but was %d",
          0, input.n / 3, numTriangles);
    }

    // Read triangle assignments.
    HashSet<Integer> usedPoints = new HashSet<>();
    output.tris = new Vec[numTriangles][3];
    for (int i = 0; i < numTriangles; i++) {
      for (int j = 0; j < 3; j++) {
        int p = reader.readInt();
        if (p <= 0 || p > input.n) {
          wrongAnswer("Expected point index to be in range [%d, %d] but was %d", 1, input.n, p);
        }
        if (!usedPoints.add(p)) {
          wrongAnswer("Point %d was used more than once", p);
        }
        output.tris[i][j] = input.ps[p - 1];
      }
    }
    return output;
  }

  @Override
  public void verifyCaseOutput(Input input, Output output) throws WrongAnswerException {
    for (Vec[] tri : output.tris) {
      // Check that the triangle has positive area.
      if (!isValidTriangle(tri)) {
        wrongAnswer("{%s, %s, %s} is not a valid triangle", tri[0], tri[1], tri[2]);
      }
    }
    // Check that the triangles are valid.
    checkForInvalidIntersections(output.tris);
  }

  static boolean isValidTriangle(Vec[] t) {
    return t[1].sub(t[0]).cross(t[2].sub(t[0])) != 0;
  }

  static void checkForInvalidIntersections(Vec[][] tris) throws WrongAnswerException {
    for (int i = 0; i < tris.length; i++) {
      Vec[] a = tris[i];
      for (int j = i + 1; j < tris.length; j++) {
        Vec[] b = tris[j];
        if (isInvalidIntersection(a, b)) {
          wrongAnswer(
              "Triangle {%s, %s, %s} intersects with {%s, %s, %s}",
              a[0], a[1], a[2], b[0], b[1], b[2]);
        }
      }
    }
  }

  static boolean isInvalidIntersection(Vec[] a, Vec[] b) {
    // Check if any two segments are on top of each other.
    for (int ai = 0; ai < 3; ai++) {
      for (int bi = 0; bi < 3; bi++) {
        if (segSegOnTopOfEachother(a[ai], a[(ai + 1) % 3], b[bi], b[(bi + 1) % 3])) {
          return true;
        }
      }
    }
    return !areTrianglesNested(a, b) && !areTrianglesSeparate(a, b);
  }

  static boolean areTrianglesSeparate(Vec[] a, Vec[] b) {
    // Two triangles are "separate" if one of their edges forms a line that partitions the points
    // such that all points of one triangle are on or to the left of the line and all points of the
    // other triangle are on or to the right of the line.
    outer:
    for (int i = 0; i < 6; i++) {
      Vec u = i < 3 ? a[i] : b[i - 3];
      Vec v = i < 3 ? a[(i + 1) % 3] : b[(i - 2) % 3];
      Vec uv = v.sub(u);
      int aSide = 0;
      for (Vec p : a) {
        int side = Long.signum(uv.cross(p.sub(u)));
        if (side == 0) {
          continue;
        }
        if (aSide * side == -1) {
          continue outer;
        }
        aSide = side;
      }
      int bSide = 0;
      for (Vec p : b) {
        int side = Long.signum(uv.cross(p.sub(u)));
        if (side == 0) {
          continue;
        }
        if (bSide * side == -1) {
          continue outer;
        }
        bSide = side;
      }
      if (aSide != bSide) {
        return true;
      }
    }
    return false;
  }

  // Returns true if and only if either triangle A fully contains B or B fully contains A.
  static boolean areTrianglesNested(Vec[] a, Vec[] b) {
    return isTriangleNested(a, b) || isTriangleNested(b, a);
  }

  // Returns true if and only if all points of A are inside or on triangle B.
  static boolean isTriangleNested(Vec[] a, Vec[] b) {
    for (Vec p : a) {
      if (getPointTriangleStatus(b, p) == -1) {
        return false;
      }
    }
    return true;
  }

  static boolean segSegOnTopOfEachother(Vec a, Vec b, Vec c, Vec d) {
    Vec ab = b.sub(a);
    Vec ac = c.sub(a);
    Vec ad = d.sub(a);
    // If not all points are parallel, the lines are not on top of each other.
    if (ab.cross(ac) != 0 || ab.cross(ad) != 0) {
      return false;
    }
    long dotC = ab.dot(ac);
    // Check if C is on the segment AB.
    if (dotC >= 0 && dotC <= ab.mag2()) {
      return true;
    }
    long dotD = ab.dot(ad);
    // Check if D is on the segment AB.
    if (dotD >= 0 && dotD <= ab.mag2()) {
      return true;
    }
    // Check if CD fully contains the segment AB.
    return Long.signum(dotC) != Long.signum(dotD);
  }

  // Returns -1 if the point is fully outside of the triangle and 1 if the point is inside or on the
  // triangle.
  static int getPointTriangleStatus(Vec[] tri, Vec p) {
    Vec a = tri[0];
    Vec b = tri[1];
    Vec c = tri[2];
    // Put ABC in counter-clockwise order.
    if (b.sub(a).cross(c.sub(a)) < 0) {
      b = tri[2];
      c = tri[1];
    }
    long crossAB = b.sub(a).cross(p.sub(a));
    long crossBC = c.sub(b).cross(p.sub(b));
    long crossCA = a.sub(c).cross(p.sub(c));
    return (crossAB < 0 || crossBC < 0 || crossCA < 0) ? -1 : 1;
  }

  static class Vec {
    long x;
    long y;

    Vec(long xx, long yy) {
      x = xx;
      y = yy;
    }

    Vec add(Vec v) {
      return new Vec(x + v.x, y + v.y);
    }

    Vec sub(Vec v) {
      return new Vec(x - v.x, y - v.y);
    }

    long dot(Vec v) {
      return x * v.x + y * v.y;
    }

    long cross(Vec v) {
      return x * v.y - y * v.x;
    }

    long mag2() {
      return dot(this);
    }

    @Override
    public String toString() {
      return String.format("(%d, %d)", x, y);
    }

    @Override
    public int hashCode() {
      return Long.hashCode(x ^ y);
    }

    @Override
    public boolean equals(Object o) {
      if (!(o instanceof Vec)) {
        return false;
      }
      Vec v = (Vec) o;
      return v.x == x && v.y == y;
    }
  }
}
