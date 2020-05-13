SySLite (Syntax-Guided Past-time LTL Synthesis & Enumerator):
------------------------------------------------------------
SySLite is past-time LTL synthesis program that support a number of
decision procedures (i.e. SAT/SMT/SyGuS based) to learn formulas from a
given set of finite traces. 

The tool currently supports a list of algorithms:

[1] bv_sygus -- SyGus + BitVector + enumeration

[2] adt_sygus -- SyGuS + ADT + enumeration

[3] fin_adt -- SMT + ADT + enumeration

[4] sat -- SAT - enumeration

[4a] sat_enum -- SAT + enumeration

[5] guided_sat -- SAT + Graph Topological - enumeration 

[5a] guided_sat_enum -- SAT + Graph Topological + enumeration

An example trace file contains a set of positive and negative traces to learn an emergency alert system (eas) formula. 
The trace file use a format that is described below and exists under the repository:
'SySLite/eas-example/eas.trace'

Please use the command to run eas trace example using bit-vector SyGuS encoding:
\#./Driver.py -n 5 -r t.txt -a bv_sygus -dict -t eas-example/eas.trace

Please use the command to run eas trace example using ADT SyGuS encoding:
\#./Driver.py -n 5 -r t.txt -a adt_sygus -dict -t eas-example/eas.trace

Please use the command to run eas trace example using ADT SMT2 encoding:
\#./Driver.py -n 5 -r t.txt -a fin_adt -dict -t eas-example/eas.trace

Please use the command to run eas trace example using SAT-encoding with enumeration mode on:
Running an toy trace using SAT (size) Enumerator:
\#./Driver.py -n 5 -r t.txt -a sat_enum -dict -t eas-example/eas.trace

Please use the command to run eas trace example using SAT-encoding without enumeration mode on:
\#./Driver.py -s 7 -r t.txt -a sat -dict -t eas-example/eas.trace

Please use the command to run eas trace example using Guided SAT Enumerator enumeration mode on:
Running an toy trace using Guided SAT Enumerator:
\#./Driver.py -n 5 -r t.txt -a guided_sat_enum -dict -t eas-example/eas.trace 

Running an toy trace using SAT (without size enumeration that required specific size parameter):
\#./Driver.py -s 3 -r t.txt -a guided_sat -t eas-example/eas.trace 

The Default Solver is (Z3) but user can switch to any other solver supported by py-smt:
\#./Driver.py -n 10 -r t.txt -a sat_enum -dict -t eas-example/eas.trace -solver msat

Example Encoding Files:
-----------------------
All the proposed encoding files exist under the repository: 'SySLite/eas-example/'
[1] eas-adt-enc.sy (\* ADT with SyGuS \*)
[2] eas-bv-enc.sy (\* Bitvector with SyGuS \*)
[3] eas-fnf-enc.smt2 (\* ADT using Finite Model Finding \*) 

These encodings can be tested using off-the-shelf CVC4-SyS solver using the command.
\#./cvc4 --lang=sygus2 --sygus-stream --sygus-sym-break-pbe FILENAME.sy
\#./cvc4 FILENAME.smt2

Input File Format:
-----------------
The input traces files contains alphabets, positive and negative example traces, supported operators 
separated by '---'. Here is an example format annotated with comments:

p,q	//Atomic Propositions

\---

1,1;0,0	(\* Positive Traces \*)

1,0;1,0

\---

1,0;0,0	(\* Negative Traces \*)

\---

!,Y,O,H	(\* Enable Unary Operators in Final Formula (Optional) \*)

\---

S,&,|,=> (\* Enable Binary Operators in Final Formula (Optional) \*)

\---

3	(\* Synthesized Formula Size (Optional) \*)

\---

S(Y(p2),p2)	(\* Target Formula for Match (Optional) \*)


Experiments:
-----------

Reference:
"SYSLITE: Syntax-Guided Synthesis of PLTL Formulas from Finite Traces", FMCAD20 [under review]



