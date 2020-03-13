#!/usr/bin/python3

from math import trunc, fabs
from os import system, stat
import sys


HOURS = 12
ADDER = 3
CARRY = ADDER - 1  # Do NOT modify!


def decode_cell_state(cols, number):
    nf = number - 1
    cell = trunc(nf / HOURS)
    hour = (nf % HOURS) + 1
    y = trunc(cell / cols)
    x = cell % cols
    return x, y, hour


def encode_cell_state(cols, x, y, hour):
    if hour < 1:
        hour = HOURS - int(fabs(hour))
    if hour > HOURS:
        hour = hour % HOURS

    return ((cols * y + x) * HOURS + (hour - 1)) + 1


def encode_carry(cols, rows, x, y, hour, num) -> int:
    return (rows * cols * HOURS) + (((cols * y + x) * HOURS + (hour - 1)) * CARRY + num) + 1


def encode_next(cols, rows, x, y, hour, num) -> int:
    return (rows * cols * HOURS * ADDER) + (((y * cols + x) * HOURS + (hour - 1)) * ADDER + num) + 1


def last_rule(cols, rows) -> int:
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


def parse_line(string, cols):
    line = []
    for c in string:
        if c != '\n':
            line.append(c)
    if len(line) < cols:
        for i in range(cols - len(line)):
            line.append(' ')
    return line


def to_matrix(labyrinth):
    matrix = []
    for row in labyrinth:
        r = []
        for elem in row:
            r.append(elem)
        matrix.append(r)
    return matrix


def rotate(labyrinth):
    cols = len(labyrinth[0])
    maze = [""] * cols
    for row in labyrinth:
        i = 0
        for w in row:
            maze[i] += w
            i += 1
    return maze


def sequence_rules(cols, labyrinth, trasp=False):
    maze = to_matrix(labyrinth)
    inner = []
    rules = []
    for line in labyrinth:
        inner += line
    width = (cols * 2 - 1)
    height = int(len(inner) / (cols * 2 - 1))
    rows = int(height / 2) + 1
    for y in range(0, height):
        if y % 2 != 0:
            continue
        for x in range(0, width - 1):
            if x % 2 != 0:
                continue
            c = maze[y][x]
            if c == 'x':
                c = None
            else:
                c = int(f'0x{c}', 16)
            w = maze[y][x+1]
            if w == '|' or w == '-':
                continue
            if x < width:
                cn = maze[y][x+2]
                if cn == 'x':
                    cn = None
                else:
                    cn = int(f'0x{cn}', 16)
                if trasp:
                    adjacency_pair_rules(rules, rows, int(y / 2), int(x / 2), int(y / 2), int(x / 2 + 1), c, cn)
                else:
                    adjacency_pair_rules(rules, cols, int(x / 2), int(y / 2), int(x / 2 + 1), int(y / 2), c, cn)
    return rules


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


def sum_rules(cols, rows):
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
    solution = []
    statinfo = stat('result.txt')
    if statinfo.st_size < 17:
        print("UNSATISFIABLE")
        exit(0)
    file = open("result.txt", "r")
    while True:
        line = file.readline()
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
                        solution.append(decode_cell_state(cols, int(number))[2])
                    number = ""
                    negate = False
                    continue
                if c == '-':
                    negate = True
                else:
                    number += c
    checkerboard = []
    line = []
    i = 0
    for v in solution:
        line.append(f'{hex(v)[2:]}'.capitalize())
        i += 1
        if i == cols:
            checkerboard.append(line)
            i = 0
            line = []

    return checkerboard


def compress(solution, cols, rows):
    final_form = []
    for y in range(0, rows):
        for x in range(0, cols):
            final_form.append(solution[y][x])
        final_form.append('\n')
    return ''.join(final_form)


def main(filename):
    cls, rws, lab = read_labyrinth(filename)
    rules1 = sequence_rules(cls, lab)
    rules2 = sequence_rules(rws, rotate(lab), True)
    rules3 = sum_rules(cls, rws)
    rules4 = final_rules(cls, rws)
    rules5 = unicity_rules(rws, cls)

    rules_tot = rules1 + rules2 + rules3 + rules4 + rules5
    f = open("SATproblem.txt", "w")
    total = cls * rws * HOURS * (ADDER * 2)
    f.write(f"p cnf {total} {len(rules_tot)}\n")
    f.write(''.join(rules_tot))
    f.close()

    system("clasp --verbose=0 SATproblem.txt > result.txt")
    sol = build_solution(cls, rws)
    print(compress(sol, cls, rws))


if __name__ == "__main__":
    main(sys.argv[1])
