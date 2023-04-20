import Foundation

let T = Int(readLine()!)!
for ti in (1...T) {
  let line = readLine()!.components(separatedBy: " ")
  let N = Int(line[0])!
  let M = Int(line[1])!
  let C = readLine()!.components(separatedBy: " ").map { Int($0)! }
  var sum = 0
  for Ci in C {
    sum += Ci
  }
  let modulo = sum % M
  print("Case #\(ti): \(modulo)")
}
