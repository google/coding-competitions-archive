package main

import (
	"fmt"
)

func remainingPieces() int {
	var (
		N   int
		M   int
		sum int
	)
	fmt.Scanf("%d %d", &N, &M)
	for i := 0; i < N; i++ {
		var Ci int
		fmt.Scan(&Ci)
		sum += Ci
	}
	return sum % M
}

func main() {
	var T int
	fmt.Scanf("%d", &T)
	for caseNumber := 1; caseNumber <= T; caseNumber++ {
		output := remainingPieces()
		fmt.Printf("Case #%d: %d\n", caseNumber, output)
	}
}
