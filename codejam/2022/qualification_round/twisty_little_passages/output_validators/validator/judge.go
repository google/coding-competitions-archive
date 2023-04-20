// "Twisty Little Passages" - judge
//
// GCJ 2022 R?
//
// Usage:
//
// go run local_testing_tool.go 0
//
// Or run using the interactive_runner script found at:
//
// https://codingcompetitions.withgoogle.com/codejam/faq#how-can-i-test-an-interactive-solution
//
// using the command line:
//
// python3 interactive_runner.py go run local_testing_tool.go 0 -- <command line for your solution>
package main

import (
	"bufio"
	"fmt"
	"io"
	"math/rand"
	"os"
	"os/signal"
	"syscall"
	"time"
)

const (
	debug = false // if true, write a copy of the input we receive to stderr.

	// Problem limits
	T    = 100
	MinN = 2
	MaxN = 1e5
	MinK = 8000
	MaxK = 8000
)

// Case is a case constructed by having subgraphs of nodes with consistent properties.
// For any two subgraphs A and B, each node in A has ds[A][B] edges adjacent to
// a node in B.  (This holds for A=B also.)
type Case struct {
	n       int     // number of rooms
	k       int     // number of rounds
	ns      []int   // size of each subgraph
	ds      [][]int // number of edges adjacent to each node of subgraph i that are adjacent to a node of subgraph j
	caseNum int
}

func egcd(xx, yy int) (g, xinv int) {
	x, y, a, b := xx, yy, 1, 0
	for y != 0 {
		m := x / y
		x, y, a, b = y, x%y, b, a-m*b
	}
	g, xinv = x, a
	for xinv < 0 {
		xinv += yy / g
	}
	return g, xinv
}

// InternalToExternal takes a node number from the test case and scrambles it
// so that nodes from each subgraph are not sequential.  This effectively
// shuffles the node numbers.
func (c *Case) InternalToExternal(w int) int {
	if c.n <= 2 {
		return w + 1
	}
	var m int
	for m = 2; ; m++ {
		g, _ := egcd(m, c.n)
		if g == 1 {
			break
		}
	}
	for i := 0; i < 20; i++ {
		w = (w + c.caseNum) % c.n
		w = int((int64(w) * int64(m)) % int64(c.n))
		if w < c.n/2 {
			w = c.n/2 - 1 - w
		}
	}
	return w + 1
}

// ExternalToInternal is the inverse of InternalToExternal.
func (c *Case) ExternalToInternal(w int) int {
	w--
	if c.n <= 2 {
		return w
	}
	var inv int
	for m := 2; ; m++ {
		var g int
		g, inv = egcd(m, c.n)
		if g == 1 {
			break
		}
	}
	for i := 0; i < 20; i++ {
		if w < c.n/2 {
			w = c.n/2 - 1 - w
		}
		w = int((int64(w) * int64(inv)) % int64(c.n))
		w = (w + (c.n - c.caseNum)) % c.n
	}
	return w
}

// TotalEdges returns the number of edges in the graph.
func (c *Case) TotalEdges() int64 {
	var ret int64
	for i := 0; i < len(c.ns); i++ {
		for j := 0; j < len(c.ns); j++ {
			ret += int64(c.ns[i]) * int64(c.ds[i][j])
		}
	}
	return ret / 2
}

// subgraph returns which subgraph v belongs to, and its 0-based index within that subgraph.
func (c *Case) subgraph(v int) (subgraph int, indexInSubgraph int) {
	subgraph = 0
	for v >= c.ns[subgraph] {
		v -= c.ns[subgraph]
		subgraph++
	}
	return subgraph, v
}

// Degree returns the degree of node v.
func (c *Case) Degree(v int) int {
	ret := 0
	subgraph, _ := c.subgraph(v)
	for _, x := range c.ds[subgraph] {
		ret += x
	}
	return ret
}

// RandomNeighbour returns a randomly-chosen neighbour of v.
func (c *Case) RandomNeighbour(v int) int {
	// which subgraph is v in?
	p1, indexInP1 := c.subgraph(v)
	// Choose a (0-based) edge index.  The ordering is
	// <all edges to subgraph 0> <all edges to subgraph 1> etc.
	edgeIndex := rand.Intn(c.Degree(v))
	// which subgraph is the other node of this edge in?
	p2 := 0
	for edgeIndex >= c.ds[p1][p2] {
		edgeIndex -= c.ds[p1][p2]
		p2++
	}
	d12 := c.ds[p1][p2]
	var indexInP2 int
	p1size := c.ns[p1]
	p2size := c.ns[p2]
	if p1 < p2 {
		// Node i in part p1 connects to the interval of nodes [i*ds[p1][p2], (i+1)*ds[p1][p2]) mod |p2|.
		edgenum := int64(indexInP1)*int64(d12) + int64(edgeIndex)
		indexInP2 = int(edgenum % int64(p2size))
	} else if p1 > p2 {
		// Invert the logic of the previous case.
		edgenum := int64(edgeIndex)*int64(p1size) + int64(indexInP1)
		indexInP2 = int(edgenum / int64(c.ds[p2][p1]))
	} else if d12%2 == 0 {
		// P1=P2.  Each node is connected to the (d12/2) vertices before and after.
		if edgeIndex < d12/2 {
			indexInP2 = (indexInP1 + 1 + edgeIndex) % p1size
		} else {
			indexInP2 = (indexInP1 - 1 - (edgeIndex - d12/2) + p1size) % p1size
		}
	} else {
		// Each node is connected to the floor(d12/2) vertices before and after, and, if
		// you imagine the nodes of this subgraph to be arranged in a circle, the node
		// diagonally across.
		if edgeIndex < d12/2 {
			indexInP2 = (indexInP1 + 1 + edgeIndex) % p1size
		} else if edgeIndex < d12-1 {
			indexInP2 = (indexInP1 - 1 - (edgeIndex - d12/2) + p1size) % p1size
		} else {
			indexInP2 = (indexInP1 + p1size/2) % p1size
		}
	}
	var ret int
	for i := 0; i < p2; i++ {
		ret += c.ns[i]
	}
	ret += indexInP2
	return ret
}

// Validate does some internal consistency checks, and returns nil on success.
func (c *Case) Validate() error {
	if c.n < MinN || MaxN < c.n {
		return fmt.Errorf("invalid n: %d", c.n)
	}
	if c.k < MinK || MaxK < c.k {
		return fmt.Errorf("invalid k: %d", c.k)
	}
	n2 := 0
	for _, x := range c.ns {
		n2 += x
	}
	if n2 != c.n {
		return fmt.Errorf("n does not equal sum of subgraphs: %d %v", c.n, c.ns)
	}
	if len(c.ns) != len(c.ds) {
		return fmt.Errorf("ns does not match ds: %v %v", c.ns, c.ds)
	}
	for _, ds := range c.ds {
		if len(ds) != len(c.ns) {
			return fmt.Errorf("ns does not match ds: %v %v", c.ns, c.ds)
		}
	}
	for i, ds := range c.ds {
		for j := 0; j < len(ds); j++ {
			deg := ds[j]
			ni := c.ns[i]
			nj := c.ns[j]
			if deg < 0 || deg > nj || (i == j && deg >= ni) || (i == j && deg%2 == 1 && ni%2 == 1) {
				return fmt.Errorf("invalid ds[%d][%d]: %d", i, j, deg)
			}
			if i != j && ni*deg != nj*c.ds[j][i] {
				return fmt.Errorf("ds[%d][%d]=%d does not match ds[%d][%d]=%d", i, j, deg, j, i, c.ds[j][i])
			}
		}
		ok := false
		for _, d := range ds {
			if d != 0 {
				ok = true
				break
			}
		}
		if !ok {
			return fmt.Errorf("subgraph %d has degree zero", i)
		}
	}
	if c.caseNum <= 3 {
		// Verify Internal<->External functions.  This is too expensive to do
		// every time.
		for i := 0; i < c.n; i++ {
			ext := c.InternalToExternal(i)
			if ext < 1 || c.n < ext {
				return fmt.Errorf("InternalToExternal(%d)=%d is out of range", i, ext)
			}
			j := c.ExternalToInternal(ext)
			if i != j {
				return fmt.Errorf("ExternalToInternal(%d)=%d, expected %d", ext, j, i)
			}
		}
	}
	return nil
}

// cases1 is a set of cases with only low-degree nodes.
var cases1 = [...]Case{
	// degree 1
	Case{n: 1e5, k: 8000, ns: []int{1e5}, ds: [][]int{[]int{1}}},
	// mostly degree 1
	Case{n: 1e5, k: 8000, ns: []int{1e5 - 4, 3, 1}, ds: [][]int{
		[]int{1, 0, 0},
		[]int{0, 0, 1},
		[]int{0, 3, 0},
	}},
	// degree 2
	Case{n: 1e5, k: 8000, ns: []int{1e5}, ds: [][]int{[]int{2}}},
}

// cases2 is a set of cases with a large number of low-degree nodes, and a
// very small number of high-degree nodes that are hard to find randomly.
var cases2 = [...]Case{
	// 1 big star (plus some edges)
	Case{n: 1e5, k: 8000, ns: []int{1e5 - 5, 1, 4}, ds: [][]int{
		[]int{0, 1, 0},
		[]int{1e5 - 5, 0, 4},
		[]int{0, 1, 3},
	}},
	// 1 big star (plus some edges)
	Case{n: 1e5, k: 8000, ns: []int{1e5 - 7, 1, 6}, ds: [][]int{
		[]int{0, 1, 0},
		[]int{1e5 - 7, 0, 6},
		[]int{0, 1, 5},
	}},
	// 4 big stars (plus some edges)
	Case{n: 1e5, k: 8000, ns: []int{1e5 - 8, 4, 4}, ds: [][]int{
		[]int{0, 1, 0},
		[]int{24998, 0, 4},
		[]int{0, 4, 3},
	}},
	// 4 big stars (plus some edges), most nodes are in 2 stars.
	Case{n: 1e5, k: 8000, ns: []int{1e5 - 8, 4, 4}, ds: [][]int{
		[]int{0, 2, 0},
		[]int{49996, 0, 4},
		[]int{0, 4, 3},
	}},
}

// cases is a set of miscellaneous cases
var cases = [...]Case{
	Case{n: 1e5, k: 8000, ns: []int{100000}, ds: [][]int{
		[]int{99999},
	}},
	Case{n: 1e5, k: 8000, ns: []int{99000, 1000}, ds: [][]int{
		[]int{98999, 1000},
		[]int{99000, 998},
	}},
	Case{n: 1e5, k: 8000, ns: []int{90000, 10000}, ds: [][]int{
		[]int{89998, 10000},
		[]int{90000, 9998},
	}},
	Case{n: 1e5, k: 8000, ns: []int{80000, 20000}, ds: [][]int{
		[]int{2000, 0},
		[]int{0, 19999},
	}},
	Case{n: 1e5, k: 8000, ns: []int{50000, 49950, 20, 30}, ds: [][]int{
		[]int{0, 0, 1, 0},
		[]int{0, 0, 0, 1},
		[]int{2500, 0, 19, 30},
		[]int{0, 1665, 20, 29},
	}},
	Case{n: 1e5, k: 8000, ns: []int{1e5 - 180, 180}, ds: [][]int{
		[]int{1, 0},
		[]int{0, 179},
	}},
	Case{n: 1e5, k: 8000, ns: []int{1e5 - 184, 184}, ds: [][]int{
		[]int{1, 0},
		[]int{0, 183},
	}},
	Case{n: 1e5, k: 8000, ns: []int{1e5 - 320, 320}, ds: [][]int{
		[]int{1, 0},
		[]int{0, 319},
	}},
	Case{n: 1e5, k: 8000, ns: []int{2e4, 2e4, 2e4, 2e4, 2e4}, ds: [][]int{
		[]int{1, 0, 0, 0, 0},
		[]int{0, 2, 0, 0, 0},
		[]int{0, 0, 3, 0, 0},
		[]int{0, 0, 0, 999, 0},
		[]int{0, 0, 0, 0, 19999},
	}},
}

func fail(msg string) {
	fmt.Fprintln(os.Stderr, msg)
	fmt.Println("-1")
	os.Exit(1)
}

func failfast(msg string) {
	fmt.Fprintln(os.Stderr, msg)
	os.Exit(1)
}

func watchSignals(c chan os.Signal) {
	for range c {
		fmt.Fprintln(os.Stderr, "got SIGPIPE")
		os.Exit(1)
	}
}

func main() {
	c := make(chan os.Signal)
	go watchSignals(c)
	signal.Notify(c, syscall.SIGPIPE)
	rand.Seed(time.Now().Unix())
	var r io.Reader = bufio.NewReader(os.Stdin)
	if debug {
		r = io.TeeReader(r, os.Stderr)
	}
	if _, err := fmt.Println(T); err != nil {
		failfast("couldn't write number of cases")
	}
	casesCorrect := 0
	fixedCase := 0
	if len(os.Args) == 2 {
		fmt.Sscan(os.Args[1], &fixedCase)
	}
	if fixedCase == -2 {
		// Run self-test.
		for cas := 1; cas <= T; cas++ {
			c := cases[cas%len(cases)]
			c.caseNum = cas
			if err := c.Validate(); err != nil {
				fmt.Fprintln(os.Stderr, err)
				fail("internal error")
			}
		}
		return
	}
	var allCases []Case
	for cas := 1; cas <= T; cas++ {
		var c Case
		// Equal parts cases1, cases2, and miscellaneous cases.
		if cas <= T/3 {
			c = cases1[cas%len(cases1)]
		} else if cas <= 2*T/3 {
			c = cases2[cas%len(cases2)]
		} else {
			c = cases[cas%len(cases)]
		}
		if fixedCase > 0 {
			c = cases[fixedCase-1]
		}
		allCases = append(allCases, c)
	}
	rand.Shuffle(T, func(i, j int) {
		allCases[i], allCases[j] = allCases[j], allCases[i]
	})
	for cas := 1; cas <= T; cas++ {
		var c Case
		c = allCases[cas-1]
		c.caseNum = cas
		if _, err := fmt.Printf("%d %d\n", c.n, c.k); err != nil {
			failfast("couldn't write N and K")
		}
		if err := c.Validate(); err != nil {
			fail(fmt.Sprintf("internal error in case %d: %v", cas, err))
		}
		where := rand.Intn(c.n) // NB we actually only promise an arbitrary starting point, not random.
		estimate, estimated := int64(0), false
		if _, err := fmt.Printf("%d %d\n", c.InternalToExternal(where), c.Degree(where)); err != nil {
			failfast("couldn't write current room and number of passages")
		}
		for round := 1; !estimated && round <= c.k+1; round++ {
			var command, roomstr string
			nscan, err := fmt.Fscanln(r, &command, &roomstr)
			if nscan == 0 {
				if err == io.EOF {
					fail("unexpected end-of-input from player")
				}
				fail("unexpected empty line from player")
			}
			switch command {
			case "W":
				if nscan != 1 {
					fail("player issued a walk command with extra arguments")
				}
				where = c.RandomNeighbour(where)
				if _, err := fmt.Printf("%d %d\n", c.InternalToExternal(where), c.Degree(where)); err != nil {
					failfast("couldn't write current room and number of passages")
				}
			case "T":
				if nscan == 1 {
					fail("player issued a teleport command without a room number")
				}
				if nscan, err = fmt.Sscan(roomstr, &where); nscan != 1 {
					fail("couldn't parse the room number in player's teleport command")
				}
				if where < 1 || c.n < where {
					fail("player issued a teleport command with an invalid room number")
				}
				where = c.ExternalToInternal(where)
				if _, err := fmt.Printf("%d %d\n", c.InternalToExternal(where), c.Degree(where)); err != nil {
					failfast("couldn't write current room and number of passages")
				}
			case "E":
				if nscan == 1 {
					fail("player issued an estimate command without an edge count")
				}
				if nscan, err = fmt.Sscan(roomstr, &estimate); nscan != 1 {
					fail("couldn't parse number of edges in player's estimate command")
				}
				estimated = true
			default:
				if nscan == 0 {
					fail("empty line in player's commands")
				}
				fail("couldn't understand player command")
			}
		}
		if !estimated {
			fail("player did not give an estimate")
		}
		correct := c.TotalEdges()
		if (2*correct+2)/3 <= estimate && estimate <= (correct*4)/3 {
			casesCorrect++
		} else {
			if cas-casesCorrect <= 3 {
				fmt.Fprintf(os.Stderr, "case %d incorrect: got %d want %d\n", cas, estimate, correct)
			} else if cas-casesCorrect == 4 {
				fmt.Fprintf(os.Stderr, "(further errors not listed)\n")
			}
		}
	}
	fmt.Fprintf(os.Stderr, "%d / %d cases correct\n", casesCorrect, T)
	var str string
	if nscan, _ := fmt.Fscanln(r, &str); nscan > 0 {
		fmt.Fprintln(os.Stderr, "extra input after interaction: "+str)
		os.Exit(1)
	}
	if casesCorrect < (90*T)/100 {
		// 90% of cases must be correct.
		os.Exit(1)
	}
}
