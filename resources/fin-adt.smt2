(set-logic ALL)

;(set-option :finite-model-find true)

(set-option :fmf-bound true)
(set-option :fmf-fun true)
(set-option :produce-models true)


; Declare Variable Sort
(define-sort VarId () Int)

; Declare Unary Operators.
(declare-datatype UNARY_OP ( (NOT) (Y) (G) (H) (O) ))

; Declare Binary Operators.
(declare-datatype BINARY_OP ( (AND) (OR) (IMPLIES) (S) ))

; Formula Declaration.
(declare-datatype Formula (
  (Top)
  (Bottom) 
  (P (Id VarId))
  (Op1 (op1 UNARY_OP) (f Formula))
  (Op2 (op2 BINARY_OP) (f1 Formula) (f2 Formula))
  )
)

;Trace Constructs
(define-sort Trace () Int)
(define-sort Time () Int)

;%{1}

;%{2}

(define-fun-rec holds ((f Formula) (tr Trace) (t Time)) Bool
  (let ((tn (len tr))) 
    (and (<= 0 t tn)
       (match f (

         (Top true)
         
         (Bottom false)
       
         ((P i) (val tr t i))
      
         ((Op1 op g) 
           (match op (
             (NOT (not (holds g tr t))) 

             (Y (and (< 0 t) (holds g tr (- t 1))))    

             (H (and (holds g tr t) (or (= t 0) (holds f tr (- t 1)))))

             (O (or  (holds g tr t) (and (< 0 t) (holds f tr (- t 1)))))

             (G (and (holds g tr t) (or (= t tn) (holds f tr (+ t 1)))))

          )))

         ((Op2 op f1 g)     
           (match op (
             (AND (and (holds f1 tr t) (holds g tr t)))

             (OR  (or (holds f1 tr t) (holds g tr t)))

             (IMPLIES (or (not (holds f1 tr t)) (holds g tr t)))

;             (S  (or (holds g tr t) (ite (= t 0) false (and (holds f1 tr t) (holds f tr (- t 1))))))

             (S  (or (holds g tr t) (and (holds f1 tr t) (and (< 0 t) (holds f tr (- t 1))))))

         )))))
    )
  )
)


(declare-const phi Formula)

(define-fun-rec holds-for-all-traces ((tr Trace) (f Formula)) Bool
  (or (< tr 1)
    (and (holds (Op1 G f) tr 0)
         (holds-for-all-traces (- tr 1) f))
  )
)

;%{3}

(assert (holds-for-all-traces pos_tr phi))

(define-fun-rec fail-for-all-traces ((tr Trace) (f Formula)) Bool
  (or (<= tr pos_tr)
    (and (not (holds (Op1 G f) tr 0))
         (fail-for-all-traces (- tr 1) f))
  )
)

;%{4}

(check-sat)

(get-value (phi))

;(get-model)


