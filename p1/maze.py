from math import trunc, fabs
from os import system
import time

import numpy as np


HOURS = 12
ADDER = 3
CARRY = ADDER - 1  # Do NOT modify!

comments = 0


def decode_cell_state(cols: int, number: int):
    nf = number - 1
    cell = trunc(nf / HOURS)
    hour = (nf % HOURS) + 1
    y = trunc(cell / cols)
    x = cell % cols
    return x, y, hour


def encode_cell_state(cols: int, x: int, y: int, hour: int):
    if hour < 1:
        hour = HOURS - int(fabs(hour))
    if hour > HOURS:
        hour = hour % HOURS

    return int((cols * y + x) * HOURS + (hour - 1)) + 1


def encode_carry(cols: int, rows: int, x: int, y: int, hour: int, num: int):
    return (rows * cols * HOURS) + (((cols * y + x) * HOURS + (hour - 1)) * CARRY + num) + 1


def encode_next(cols: int, rows: int, x: int, y: int, hour: int, num: int):
    return (rows * cols * HOURS * ADDER) + (((y * cols + x) * HOURS + (hour - 1)) * ADDER + num) + 1


def last_rule(cols, rows):
    return cols * rows * HOURS * (ADDER * 2)


def read_labyrinth(name):
    labyrinth = []
    file = open(name, "r")
    cols = int(file.readline())
    rows = int(file.readline())
    while True:
        line = file.readline()
        if not line:
            break
        labyrinth.append(parse_line(line, cols * 2 - 1))
    return cols, rows, labyrinth


def parse_line(string, cols: int):
    line = []
    for c in string:
        if c != '\n':
            line.append(c)
    if len(line) < cols:
        for i in range(cols - len(line)):
            line.append(' ')
    return line


def sequence_rules(cols, labyrinth):
    inner = []
    rules = []
    for line in labyrinth:
        inner += line
    lmap = np.array(inner)
    lines_number = int(len(inner) / (cols * 2 - 1))
    lmap = lmap.reshape((lines_number, cols * 2 - 1))
    width = lmap.shape[1]
    height = lmap.shape[0]
    for y in range(0, height):
        if y % 2 != 0:
            continue
        for x in range(0, width - 1):
            if x % 2 != 0:
                continue
            c = lmap[y][x]
            if c == 'x':
                c = None
            else:
                c = int(f'0x{c}', 16)
            w = lmap[y][x+1]
            if w == '|':
                continue
            if x < width:
                cn = lmap[y][x+2]
                if cn == 'x':
                    cn = None
                else:
                    cn = int(f'0x{cn}', 16)
                adjacency_pair_rules(rules, cols, x / 2, y / 2, x / 2 + 1, y / 2, c, cn)
    return rules


def sequence_rules_v(cols, labyrinth):
    inner = []
    rules = []
    for line in labyrinth:
        inner += line
    lmap = np.array(inner)
    lines_number = int(len(inner) / (cols * 2 - 1))
    lmap = lmap.reshape((lines_number, cols * 2 - 1))
    width = lmap.shape[1]
    height = lmap.shape[0]
    for x in range(0, width):
        if x % 2 != 0:
            continue
        for y in range(0, height-1):
            if y % 2 != 0:
                continue
            c = lmap[y][x]
            if c == 'x':
                c = None
            else:
                c = int(c, 16)
            w = lmap[y+1][x]
            if w == '|' or w == '-':
                continue
            if y < height:
                cn = lmap[y+2][x]
                if cn == 'x':
                    cn = None
                else:
                    cn = int(cn, 16)
                adjacency_pair_rules(rules, cols, x / 2, y / 2, x / 2, y / 2 + 1, c, cn)
    return rules


def write_comment(rules, comm):
    rules.append(f'{comm}')
    s = comments + 1


def adjacency_pair_rules(rules, cols, x1, y1, x2, y2, h1, h2):
    for i in range(1, HOURS + 1):
        s1 = encode_cell_state(cols, x1, y1, i)
        s2 = encode_cell_state(cols, x2, y2, i + 1)
        s3 = encode_cell_state(cols, x2, y2, i - 1)
        rules.append(f'-{s1} {s2} {s3} 0\n')
        s1 = encode_cell_state(cols, x2, y2, i)
        s2 = encode_cell_state(cols, x1, y1, i + 1)
        s3 = encode_cell_state(cols, x1, y1, i - 1)
        rules.append(f'-{s1} {s2} {s3} 0\n')
    # Cell hours facts
    if h1 is not None:
        if h2 is None:
            rules.append(f'{encode_cell_state(cols, x1, y1, h1)} 0\n')
        else:
            rules.append(f'{encode_cell_state(cols, x1, y1, h1)} 0\n')
            rules.append(f'{encode_cell_state(cols, x2, y2, h2)} 0\n')
    else:
        if h2 is not None:
            rules.append(f'{encode_cell_state(cols, x2, y2, h2)} 0\n')


def sum_rules(cols: int, rows: int):
    rules = []
    for x in range(0, cols):
        for y in range(0, rows):
            for h in range(1, HOURS + 1):
                for n in range(0, ADDER):
                    y_l = y
                    if x == 0:
                        x_l = cols - 1
                        y_l = y - 1
                    else:
                        x_l = x - 1

                    c1 = encode_carry(cols, rows, x, y, h, n)
                    s0 = encode_next(cols, rows, x, y, h, n)
                    last_s0 = encode_next(cols, rows, x_l, y_l, h, n)
                    c0 = encode_carry(cols, rows, x, y, h, n - 1)
                    if n == 0:
                        cell = encode_cell_state(cols, x, y, h)
                        if x == 0 and y == 0:
                            rules.append(f'-{c1} 0\n')
                            rules.append(f'-{cell} {s0} 0\n')
                        else:
                            rules.append(f'-{last_s0} -{cell} {c1} 0\n')
                            rules.append(f'-{last_s0} {cell} {s0} 0\n')
                            rules.append(f'{last_s0} -{cell} {s0} 0\n')
                    elif n < ADDER - 1:
                        if x == 0 and y == 0:
                            rules.append(f'-{c0} 0\n')
                            rules.append(f'-{s0} 0\n')
                            continue
                        else:
                            c1 = encode_carry(cols, rows, x, y, h, n)
                            last_s0 = encode_next(cols, rows, x_l, y_l, h, n)
                            rules.append(f'-{last_s0} -{c0} {c1} 0\n')
                            rules.append(f'-{last_s0} {c0} {s0} 0\n')
                            rules.append(f'{last_s0} -{c0} {s0} 0\n')
                    else:
                        if x == 0 and y == 0:
                            rules.append(f'-{s0} 0\n')
                            continue
                        else:
                            rules.append(f'-{last_s0} -{c0} 0\n')  # Failure rule
                            rules.append(f'-{last_s0} {c0} {s0} 0\n')
                            rules.append(f'{last_s0} -{c0} {s0} 0\n')
    return rules


def unicity_rules(rows, cols):
    rules = []
    # Just one hour for a cell
    for x in range(0, cols):
        for y in range(0, rows):
            for h1 in range(1, HOURS + 1):
                for h2 in range(h1 + 1, HOURS + 1):
                    cell_h1 = encode_cell_state(cols, x, y, h1)
                    cell_h2 = encode_cell_state(cols, x, y, h2)
                    rules.append(f'-{cell_h1} -{cell_h2} 0\n')

    # Avoid all 0 solutions
    for x in range(0, cols):
        for y in range(0, rows):
            ors = []
            for h1 in range(1, HOURS + 1):
                ors.append(f'{encode_cell_state(cols, x, y, h1)} ')
            rules.append(f'{"".join(ors)} 0\n')
    return rules


def final_rules(rows, cols):
    rules = []
    bits = bin(int(rows * cols / HOURS))[2:][::-1]
    for h in range(1, HOURS + 1):
        for n in range(0, ADDER):
            if n >= len(bits):
                b = ''
            else:
                b = bits[n]
            if b == '1':
                rules.append(f'{encode_next(rows, cols, rows - 1, cols - 1, h, n)} 0\n')
            else:
                rules.append(f'-{encode_next(rows, cols, rows - 1, cols - 1, h, n)} 0\n')
            n += 1
    return rules


def build_solution(cols, rows):
    checkerboard = []

    f = open("result.txt", "r")
    while True:
        line = f.readline()
        if not line:
            break
        if line[0] == 'v':
            negate = False
            number = ""
            for c in line[2:]:
                if c == " " or c == "\n":
                    if int(number) > (rows * cols * HOURS):
                        break
                    if not negate:
                        checkerboard.append(decode_cell_state(cols, int(number))[2])
                    number = ""
                    negate = False
                    continue
                if c == '-':
                    negate = True
                else:
                    number += c
    to_hex = np.vectorize(lambda x: f'{hex(x)[2:]}'.capitalize())
    hex_sol = to_hex(np.array(checkerboard).reshape((rows, cols)))
    return hex_sol


def compress(solution):
    final_form = []
    height, width = solution.shape
    for y in range(0, height):
        for x in range(0, width):
            final_form.append(solution[y, x])
        final_form.append('\n')
    return ''.join(final_form)


cls, rws, lab = read_labyrinth("./examples/dom47.txt")
hours = cls * rws / HOURS
rules1 = sequence_rules(cls, lab)
rules2 = sequence_rules_v(cls, lab)
rules3 = sum_rules(cls, rws)
rules4 = final_rules(cls, rws)
rules5 = unicity_rules(rws, cls)

rules_tot = rules1 + rules2 + rules3 + rules4 + rules5
f = open("satfile.txt", "w")
total = cls * rws * HOURS * (ADDER * 2)
f.write(f"p cnf {total} {len(rules_tot)}\n")
f.write(''.join(rules_tot))
f.close()

system("clasp --verbose=0 satfile.txt > result.txt")
sol = build_solution(cls, rws)
print(sol)
print(compress(sol))
