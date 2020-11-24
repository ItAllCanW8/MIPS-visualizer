def get_key(dict, val):
    for key, value in dict.items():
        if val == value:
            return key


def switch_funct(funct, machineCode):
    switcher = {
        "000000": "sll",
        "000010": "srl",
        "001000": "jr",
        "100000": "add",
        "100001": "addu",
        "100010": "sub",
        "100011": "subu",
        "100100": "and",
        "100101": "or",
        "100111": "nor",
        "101010": "slt",
        "101011": "sltu",
    }

    if machineCode:
        return switcher.get(funct, "Invalid func")
    else:
        return get_key(switcher, funct)


def switch_opcode(opcode, machineCode):
    switcher = {
        "000010": "j",
        "000011": "jal",
        "000100": "beq",
        "000101": "bne",
        "001000": "addi",
        "001001": "addiu",
        "001010": "slti",
        "001011": "sltiu",
        "001100": "andi",
        "001101": "ori",
        "001111": "lui",
        "100011": "lw",
        "101011": "sw",
    }

    if machineCode:
        return switcher.get(opcode, "Invalid opcode")
    else:
        return get_key(switcher, opcode)


def switch_reg_type(reg, machineCode):
    switcher = {
        "00000": "$zero",
        "00001": "$at",
        "00010": "$v0",
        "00011": "$v1",
        "00100": "$a0",
        "00101": "$a1",
        "00110": "$a2",
        "00111": "$a3",
        "01000": "$t0",
        "01001": "$t1",
        "01010": "$t2",
        "01011": "$t3",
        "01100": "$t4",
        "01101": "$t5",
        "01110": "$t6",
        "01111": "$t7",
        "10000": "$s0",
        "10001": "$s1",
        "10010": "$s2",
        "10011": "$s3",
        "10100": "$s4",
        "10101": "$s5",
        "10110": "$s6",
        "10111": "$s7",
        "11000": "$t8",
        "11001": "$t9",
        "11010": "$k0",
        "11011": "$k1",
        "11100": "$gp",
        "11101": "$sp",
        "11110": "$fp",
        "11111": "$ra",
    }

    if machineCode:
        return switcher.get(reg, "Invalid reg")
    else:
        return get_key(switcher, reg)


PC = - 4


class Instruction:

    def __init__(self, codedInstr, machineCode):

        if machineCode:
            self.machine_fetch(codedInstr)
        else:
            self.asm_fetch(codedInstr)

        global PC
        PC = self.NPC

    def machine_fetch(self, codedInstr):
        global PC
        self.NPC = PC + 4

        self.instr = codedInstr
        self.opcode = codedInstr[0:6]

        if self.opcode == "000000":
            self.type = "R"
        elif self.opcode == "000010" or self.opcode == "000011":
            self.type = "J"
        else:
            self.type = "I"

        if self.type == "J":
            self.address = self.instr[6:32]
            self.name = switch_opcode(self.opcode, True)
            self.decodedInstr = self.name + " " + str(int(self.address, 2))
        elif self.type == "R":
            self.rs = self.instr[6:11]
            self.rt = self.instr[11:16]
            self.rd = self.instr[16:21]
            self.sa = self.instr[21:26]
            self.funct = self.instr[26:32]
            self.name = switch_funct(self.funct, True)
            self.rsName = switch_reg_type(self.rs, True)
            self.rtName = switch_reg_type(self.rt, True)
            self.rdName = switch_reg_type(self.rd, True)

            if self.name == "jr":
                self.decodedInstr = self.name + " " + self.rsName
            elif self.name == "sll" or self.name == "srl":
                self.decodedInstr = self.name + " " + self.rdName + ", " + self.rtName + ", " + str(int(self.sa, 2))
            else:
                self.decodedInstr = self.name + " " + self.rdName + ", " + self.rsName + ", " + self.rtName

        else:
            self.rs = self.instr[6:11]
            self.rt = self.instr[11:16]
            self.immediate = self.instr[16:32]
            self.name = switch_opcode(self.opcode, True)
            self.rsName = switch_reg_type(self.rs, True)
            self.rtName = switch_reg_type(self.rt, True)

            if self.name == "lui":
                self.decodedInstr = self.name + " " + self.rtName + ", " + str(int(self.immediate, 2))
            elif self.name == "lw" or self.name == "sw":
                self.decodedInstr = self.name + " " + self.rtName + ", " + str(int(self.immediate, 2)) \
                                    + "(" + self.rsName + ")"
            elif self.name == "beq" or self.name == "bne":
                self.decodedInstr = self.name + " " + self.rsName + ", " + self.rtName + ", " \
                                    + str(int(self.immediate, 2))
            else:
                self.decodedInstr = self.name + " " + self.rtName + ", " + self.rsName + ", " \
                                    + str(int(self.immediate, 2))


    def asm_fetch(self, codedInstr):
        global PC
        self.NPC = PC + 4

        if codedInstr[-1] == ":":
            print("kek")
        else:
            self.fullInstr = codedInstr
            self.data = codedInstr.split(" ")
            self.name = self.data[0]

            if switch_opcode(self.data[0], False):
                self.opcode = switch_opcode(self.data[0], False)
                if int(self.opcode, 2) > 3:
                    self.type = "I"

                    if self.name == "lui":
                        self.rtName = self.data[1][0:-1]
                        self.rt = switch_reg_type(self.rtName, False)
                        self.rs = "00000"
                        self.immediate = bin(int(self.data[2])).replace("0b", "")
                    elif self.name == "lw" or self.name == "sw":
                        self.rtName = self.data[1][0:-1]
                        self.rt = switch_reg_type(self.rtName, False)
                        temp = self.data[2].split("(")
                        self.immediate = bin(int(temp[0])).replace("0b", "")
                        self.rsName = temp[1][0:-1]
                        self.rs = switch_reg_type(self.rsName, False)
                    elif self.name == "beq" or self.name == "bne":
                        self.rsName = self.data[1][0:-1]
                        self.rs = switch_reg_type(self.rsName, False)
                        self.rtName = self.data[2][0:-1]
                        self.rt = switch_reg_type(self.rtName, False)
                        self.immediate = bin(int(self.data[3])).replace("0b", "")
                    else:
                        self.rtName = self.data[1][0:-1]
                        self.rt = switch_reg_type(self.rtName, False)
                        self.rsName = self.data[2][0:-1]
                        self.rs = switch_reg_type(self.rsName, False)
                        self.immediate = bin(int(self.data[3])).replace("0b", "")

                else:
                    self.type = "J"
                    self.address = bin(int(self.data[1])).replace("0b", "")

            elif switch_funct(self.data[0], False):
                self.funct = switch_funct(self.data[0], False)
                self.type = "R"
                self.opcode = "000000"

                if self.name == "jr":
                    self.rsName = self.data[1]
                    self.rs = switch_reg_type(self.rsName, False)
                    self.rt = "00000"
                    self.rd = "00000"
                    self.sa = "00000"
                elif self.name == "sll" or self.name == "srl":
                    self.rs = "00000"
                    self.sa = "00000"
                    self.rdName = self.data[1][0:-1]
                    self.rd = switch_reg_type(self.rdName, False)
                    self.rtName = self.data[2][0:-1]
                    self.rt = switch_reg_type(self.rtName, False)
                    self.sa = bin(int(self.data[3])).replace("0b", "")
                else:
                    self.rdName = self.data[1][0:-1]
                    self.rd = switch_reg_type(self.rdName, False)
                    self.rsName = self.data[2][0:-1]
                    self.rs = switch_reg_type(self.rsName, False)
                    self.rtName = self.data[3]
                    self.rt = switch_reg_type(self.rtName, False)
                    self.sa = "00000"