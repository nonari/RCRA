#!/usr/bin/python3

from os import system, stat
import sys
import re

ITEM_RE = re.compile('ch\(c\(([0-9]+)\),h\(([0-9]+)\)\)')

HOURS = 12


def encode_cell_state(cols, x, y):
    return int(cols * y + x)


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


def neighbours(cols, labyrinth, trasp=False):
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
                    adjacency_pair_rules(rules, rows, y / 2, x / 2, y / 2, x / 2 + 1, c, cn)
                else:
                    adjacency_pair_rules(rules, cols, x / 2, y / 2, x / 2 + 1, y / 2, c, cn)
    return rules


def adjacency_pair_rules(rules, cols, x1, y1, x2, y2, h1, h2):
    rules.append(f'nh(c({encode_cell_state(cols, x1, y1)}), c({encode_cell_state(cols, x2, y2)})).\n')

    # Cell hours facts
    if h1 is not None:
        if h2 is None:
            rules.append(f'ch(c({encode_cell_state(cols, x1, y1)}), h({h1-1})).\n')
        else:
            rules.append(f'ch(c({encode_cell_state(cols, x1, y1)}), h({h1-1})).\n')
            rules.append(f'ch(c({encode_cell_state(cols, x2, y2)}), h({h2-1})).\n')
    else:
        if h2 is not None:
            rules.append(f'ch(c({encode_cell_state(cols, x2, y2)}), h({h2-1})).\n')


def parse_result_item(item):
    res = ITEM_RE.search(item)
    cell = int(res.group(1))
    hour = res.group(2)
    return cell, hour


def parse_result_line(line):
    cells_and_hours = []
    items = line.split(' ')
    for item in items:
        cells_and_hours.append(parse_result_item(item))
    return cells_and_hours


def build_solution(cols, rows):
    solution = []
    cells_and_hours = []
    statinfo = stat('result.txt')
    if statinfo.st_size < 15:
        print("UNSATISFIABLE")
        exit(0)
    file = open("result.txt", "r")
    while True:
        line = file.readline()
        if not line:
            break
        if line.find("SATISFIABLE") != -1:
            break
        cells_and_hours += parse_result_line(line)

    cells_and_hours.sort(key=lambda cell_state: cell_state[0])

    line = []
    i = 0
    for state in cells_and_hours:
        line.append(f'{hex(int(state[1]) + 1)[2:]}'.capitalize())
        i += 1
        if i == cols:
            solution.append(line)
            i = 0
            line = []

    return compress(solution, cols, rows)


def compress(solution, cols, rows):
    final_form = []
    for y in range(0, rows):
        for x in range(0, cols):
            final_form.append(solution[y][x])
        final_form.append('\n')
    return ''.join(final_form)


def main(filename):
    cls, rws, lab = read_labyrinth(filename)
    rules1 = neighbours(cls, lab)
    rules2 = neighbours(rws, rotate(lab), True)
    total = cls * rws

    rules_tot = rules1 + rules2
    problem_file = open("instance.txt", "w")
    problem_file.write(f"#const t = {total}.\n")
    problem_file.write(f"#const l = {HOURS}.\n")
    problem_file.write(f"#const r = {int(total/HOURS)}.\n")
    problem_file.write(''.join(rules_tot))
    problem_file.close()
    system("cat encoding.txt >> instance.txt")
    system("clingo --verbose=0 instance.txt > result.txt")
    print(build_solution(cls, rws))


if __name__ == "__main__":
    main(sys.argv[1])
