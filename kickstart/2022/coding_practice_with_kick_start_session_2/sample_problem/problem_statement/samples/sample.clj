(require '[clojure.string :as str])

; Helper functions to read from stdin.
(defn str-from-input [] (str/trim (read-line)))
(defn array-from-input [] (str/split (str-from-input) #"\s"))

; Main solve function.
(defn solve [candies m]
  (rem (reduce + candies) m))

; Number of cases.
(def t (Integer/parseInt (str-from-input)))

(doseq [case-num (range t)]
  ; We are reading N and M from the single line.
  (let [[n m] (map #(Integer/parseInt %) (array-from-input))
        case-num (inc case-num)
        candies (map #(Integer/parseInt %) (array-from-input))
        result (solve candies m)]
    (printf "Case #%d: %d\n" case-num result)))
