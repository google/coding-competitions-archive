(defun test ()
  (let ((N (read))
	(M (read))
	(C (read-from-string (concatenate 'string "(" (read-line) ")"))))
    (mod (reduce '+ C) M)
  ))

(defvar TT (read))
(dotimes (i TT)
  (format T "Case #~d: ~d~%" (+ i 1) (test))
  )

