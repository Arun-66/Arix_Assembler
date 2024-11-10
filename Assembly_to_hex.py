import re
import os

def str_num(value):
    match = re.match(r"x(\d+)$", value)
    if match:
        number = int(match.group(1))
        return number
    return None

rtype = ['add', 'sub', 'and', 'or', 'xor', 'sll', 'srl', 'sra', 'slt', 'sltu', 'mul', 'mulh', 'mulsu', 'mulu', 'div', 'divu', 'rem', 'remu']
itype = ['addi', 'andi', 'ori', 'xori', 'slli', 'srli', 'srai', 'slti', 'sltui']
ltype = ['lb', 'lh', 'lw', 'lbu', 'lhu']
stype = ['sb', 'sh', 'sw']
btype = ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']
jtype = ['jal', 'jalr']
utype = ['lui', 'auipc']

f37_rtype = {
    'add': [0, 0], 'sub': [0, 0x20], 'and': [0x7, 0], 'or': [0x6, 0],
    'xor': [0x4, 0], 'sll': [0x1, 0], 'srl': [0x5, 0], 'sra': [0x5, 0x20],
    'slt': [0x2, 0], 'sltu': [0x3, 0], 'mul': [0x00, 0x01], 'mulh': [0x1, 0x01],
    'mulsu': [0x2, 0x01], 'mulu': [0x3, 0x01], 'div': [0x4, 0x01], 'divu': [0x5, 0x01],
    'rem': [0x6, 0x01], 'remu': [0x7, 0x01]
}
f37_itype = {
    'addi': [0, 0], 'andi': [0x7, 0], 'ori': [0x6, 0], 'xori': [0x4, 0],
    'slli': [0x1, 0], 'srli': [0x5, 0], 'srai': [0x5, 0x20], 'slti': [0x2, 0], 'sltui': [0x3, 0x0]
}
f37_ltype = {
    'lb': [0, 0], 'lh': [0x1, 0], 'lw': [0x2, 0],
    'lbu': [0x4, 0], 'lhu': [0x5, 0]
}

f37_stype = {
    'sb': [0, 0], 'sh': [0x1, 0], 'sw': [0x2, 0],
}

script_dir = os.path.dirname(os.path.abspath(__file__))
f =  open(os.path.join(script_dir, "Assembly.txt"), "r")
codes = f.read()

codes = codes.splitlines()
codes = [line.strip() for line in codes if line.strip()]
codes = [re.split(r'[ ,]+', line) for line in codes]
print(codes)

codes_pc = {}
pc = 0
skips = {}
for inst in codes:
    mnemonic = inst[0]
    if mnemonic in rtype+itype+ltype+stype+jtype+btype+utype:
        codes_pc[pc] = inst
        pc += 4
    else:
        skips[mnemonic] = pc+4

print(codes_pc)
print(skips)
for addr in codes_pc:
    inst = codes_pc[addr]
    mnemonic = inst[0]
    
    if mnemonic in rtype:
        f37 = f37_rtype[mnemonic]
        rs1 = format(str_num(inst[2]), '05b')
        rs2 = format(str_num(inst[3]), '05b')
        rd = format(str_num(inst[1]), '05b')
        
        out_bin = f"{f37[1]:07b}{rs2}{rs1}{f37[0]:03b}{rd}{int('0110011', 2):07b}"
        out_hex = hex(int(out_bin, 2))[2:].zfill(8).upper()
        print(f"{mnemonic} at {addr:#08x}: {out_hex}")
    
    elif mnemonic in itype:
        opcode = '0010011'
        func3 = f37_itype[mnemonic][0]
        rs1 = format(str_num(inst[2]), '05b')
        imm = format(int(inst[3], 16), '012b')
        rd = format(str_num(inst[1]), '05b')
        out_bin = f"{imm}{rs1}{func3:03b}{rd}{opcode}"
        out_hex = hex(int(out_bin, 2))[2:].zfill(8).upper()
        print(f"{mnemonic} at {addr:#08x}: {out_hex}")
        
    elif mnemonic in ltype:
        opcode = '0000011'
        func3 = f37_ltype[mnemonic][0]
        rs1 = format(str_num(inst[2]), '05b')
        imm = format(int(inst[3], 16), '012b')
        rd = format(str_num(inst[1]), '05b')
        out_bin = f"{imm}{rs1}{func3:03b}{rd}{opcode}"
        out_hex = hex(int(out_bin, 2))[2:].zfill(8).upper()
        print(f"{mnemonic} at {addr:#08x}: {out_hex}")

    elif mnemonic in stype:
        opcode = '0100011'
        func3 = f37_stype[mnemonic][0]
        rs1 = format(str_num(inst[1]), '05b')
        imm = format(int(inst[3], 16), '012b')
        rs2 = format(str_num(inst[2]), '05b')
        imm1 = imm[11:5]
        imm2 = imm[4:0]
        out_bin = f"{imm1}{rs2}{rs1}{imm2}{opcode}"
        out_hex = hex(int(out_bin, 2))[2:].zfill(8).upper()
        print(f"{mnemonic} at {addr:#08x}: {out_hex}")

    elif mnemonic in btype:
        opcode = '1100011'
        func3 = f37_stype[mnemonic][0]
        rs1 = format(str_num(inst[1]), '05b')
        rs2 = format(str_num(inst[2]), '05b')
        offset = skips(inst[3]) - addr
        imm = format(int(offset),'12b')
        imm1 = imm[11]
        imm2 = imm[9:4]
        imm3 = imm[3:0]
        out_bin = f"{imm1}{imm2}{rs2}{rs1}{imm3}{imm[10]}{opcode}"
        out_hex = hex(int(out_bin, 2))[2:].zfill(8).upper()
        print(f"{mnemonic} at {addr:#08x}: {out_hex}")

    elif mnemonic == "jal":
        opcode = '1101111'
        offset = skips(inst[1])-addr
        rd = format(str_num(inst[0]), '05b')
        imm = format(int(offset),'20b')
        imm1 = imm[20]
        imm2 = imm[10:1]
        imm3 = imm[11]
        imm4 = imm[19:12]  
        out_bin = f"{imm1}{imm2}{imm3}{imm4}{rd}{opcode}"
        out_hex = hex(int(out_bin, 2))[2:].zfill(8).upper()
        print(f"{mnemonic} at {addr:#08x}: {out_hex}")

    elif mnemonic == "jalr":
        opcode = '1100111'
        opcode = '0010011'
        func3 = f37_itype[mnemonic][0]
        rs1 = format(str_num(inst[2]), '05b')
        imm = format(int(inst[3], 16), '012b')
        rd = format(str_num(inst[1]), '05b')
        out_bin = f"{imm}{rs1}{func3:03b}{rd}{opcode}"
        out_hex = hex(int(out_bin, 2))[2:].zfill(8).upper()
        print(f"{mnemonic} at {addr:#08x}: {out_hex}")

    elif mnemonic == "lui":
        opcode = '0110111'
        rd = format(str_num(inst[0]), '05b')
        imm = format(int(inst[1]),'20b')
        out_bin = f"{imm}{rd}{opcode}"
        out_hex = hex(int(out_bin, 2))[2:].zfill(8).upper()
        print(f"{mnemonic} at {addr:#08x}: {out_hex}")

    elif mnemonic == "auipc":
        opcode = '0010111'
        rd = format(str_num(inst[0]), '05b')
        imm = format(int(inst[1]),'20b')
        out_bin = f"{imm}{rd}{opcode}"
        out_hex = hex(int(out_bin, 2))[2:].zfill(8).upper()
        print(f"{mnemonic} at {addr:#08x}: {out_hex}")
