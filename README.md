# SySLite 
<sub>Syntax-Guided Past-time LTL Synthesizer & Enumerator</sub>

SysLite makes use of decision and synthesis procedures (\ie SAT, SMT, and SyGuS) to learn PLTL formulas from a finite set of example traces. These example traces describe the intended and unintended behavior in terms of positive and negative traces that can come from various application domains (i.e, security policy logs, protocols, and execution of the system or design, etc.). 

## Build & Test

1. To build: `./tool-setup` 

2. To run: `./Driver --help`

## Usage

An example trace file contains a set of positive and negative traces to learn an emergency alert system (eas) formula. 
The trace file use a format that is described below and exists under the repository:
[SySLite/eas-example/](https://github.com/CLC-UIowa/SySLite/tree/master/eas-example)

Please use the command to run eas trace example using bit-vector SyGuS encoding:

`./Driver.py -n 5 -r t.txt -a bv_sygus -dict -t eas-example/eas.trace`

Please use the command to run eas trace example using ADT SyGuS encoding:

`./Driver.py -n 5 -r t.txt -a adt_sygus -dict -t eas-example/eas.trace`

Please use the command to run eas trace example using ADT SMT2 encoding:

`./Driver.py -n 5 -r t.txt -a fin_adt -dict -t eas-example/eas.trace`

Please use the command to run eas trace example using SAT-encoding with enumeration mode on:

`./Driver.py -n 5 -r t.txt -a sat_enum -dict -t eas-example/eas.trace`

Please use the command to run eas trace example using SAT-encoding with enumeration mode off:

`./Driver.py -s 7 -r t.txt -a sat -dict -t eas-example/eas.trace`

Please use the command to run eas trace example using Guided SAT Enumerator enumeration mode on:

`./Driver.py -n 5 -r t.txt -a guided_sat_enum -dict -t eas-example/eas.trace` 

Please use the command to run eas trace example using Guided SAT Enumerator wiht enumeration mode off:

`./Driver.py -s 3 -r t.txt -a guided_sat -t eas-example/eas.trace` 

The Default Solver is (Z3) but user can switch to any other solver supported by py-smt:

`./Driver.py -n 10 -r t.txt -a sat_enum -dict -t eas-example/eas.trace -solver msat`

The tool currently supports a list of algorithms and options:

1. SyGus + BitVector + enumeration `bv_sygus`  
2. SyGuS + ADT + enumeration `adt_sygus` 
3. SMT + ADT + enumeration `fin_adt`
4. SAT - enumeration `sat`  
5. SAT + enumeration `sat_enum` 
6. SAT + Graph Topological - enumeration `guided_sat`  
7. SAT + Graph Topological + enumeration `guided_sat_enum`  

Example Encoding Files:
-----------------------
All the proposed encoding files exist under the repository: [SySLite/eas-example/](https://github.com/CLC-UIowa/SySLite/tree/master/eas-example)
1. [eas-adt-enc.sy](https://github.com/CLC-UIowa/SySLite/blob/master/eas-example/eas-adt-enc.sy) (\* ADT with SyGuS \*)
2. [eas-bv-enc.sy](https://github.com/CLC-UIowa/SySLite/blob/master/eas-example/eas-bv-enc.sy) (\* Bitvector with SyGuS \*)
3. [eas-fnf-enc.smt2](https://github.com/CLC-UIowa/SySLite/blob/master/eas-example/eas-fnf-enc.smt2) (\* ADT using Finite Model Finding \*) 

These encodings can be tested using off-the-shelf [CVC4SY](https://github.com/CLC-UIowa/SySLite/blob/master/resources/cvc4) solver using the commands:

`./cvc4 --lang=sygus2 --sygus-stream --sygus-sym-break-pbe FILENAME.sy`

`./cvc4 FILENAME.smt2`

##Input File Format:
An example trace file is provided in file `eas.trace`.

The input traces files contains alphabets, positive and negative example traces, supported operators 
separated by `---`. 
```
p,q	//Atomic Propositions
---
1,1;0,0	(\* Positive Traces \*)
1,0;1,0
---
1,0;0,0	(\* Negative Traces \*)
---
!,Y,O,H	(\* Enable Unary Operators in Final Formula (Optional) \*)
---
S,&,|,=> (\* Enable Binary Operators in Final Formula (Optional) \*)
---
3	(\* Synthesized Formula Size (Optional) \*)
---
S(Y(p2),p2)	(\* Target Formula for Match (Optional) \*)
```

## Experiments:

The details about the experiments are described in the undermentioned paper. The training and test data include results are contained in [Experiments](https://github.com/CLC-UIowa/SySLite/tree/master/experiments)

### Reference:

"SYSLITE: Syntax-Guided Synthesis of PLTL Formulas from Finite Traces", FMCAD20 [under review]



