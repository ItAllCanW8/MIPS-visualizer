# MIPS Pipeline Visualizer v 2.0

Consider a pipeline with full forwarding and typical 5-stage **IF,ID,EX,MEM,WB** MIPS design. Assume that the second half of the decode stage performs a read of source registers and the first half of the write-back stage writes to the register file.

## Supported instructions

* R-format: add,addu,sub,subu,and,or,nor,slt,sltu,sll,srl
* I-format: beq,bne,addi,addiu,andi,ori,slti,sltiu,lui,lw,sw

branches & jumps can be implemented in the future (or not =) )

## v 2.0: added visualising of JSON dump log (MIPS-MIPT)

### Sources
* Computer Architecture A Quantitative Approach (5th edition) - John L. Hennessy, David A Patterson 2012
* MIPS32™ Architecture For Programmers Volume II: The MIPS32™ Instruction Set March 12, 2001, MIPS Technologies, Inc.1225 Charleston RoadMountain View, CA 94043-1353
* https://chortle.ccsu.edu/AssemblyTutorial/index.html
