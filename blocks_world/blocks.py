#!/usr/bin/python3

from os import system
import sys, re

MOV_PATTERN = re.compile('mov\(([0-9]+),([0-9]+)\)')

HELP = "blocks filename [-exhaustive] [-noshift] [-telpath <path>] [-check]"


def adjust(initial, final, offset=0):
    for i in range(offset):
        final.insert(0, [])
    diff = len(initial) - len(final)
    absdiff = abs(diff)
    if diff < 0:
        for i in range(absdiff):
            initial.append([])
    if diff > 0:
        for i in range(absdiff):
            final.append([])


def check(offset, movs, initial, final):
    adjust(initial, final, offset)
    n = len(initial)
    table = set()
    for mov in movs:
        block = mov[0]
        dest = mov[1]
        found = False
        if block in table:
            found = True
            table.remove(block)
        else:
            for stack in initial:
                if len(stack) > 0 and stack[-1] == block:
                    stack.remove(block)
                    found = True
                    break

        if not found:
            print(f'Block {block} is not at any peak')
            exit(-1)
        if dest == 0:
            table.add(block)
        else:
            if dest > n:
                print(f'Destination {dest} is out of range 1-{n}')
                exit(-1)
            initial[dest-1].append(block)
    fail = False
    for i in range(1, n):
        si = initial[i]
        sf = final[i]
        if len(sf) != len(si):
            fail = True
            break
        if len(sf) != 0:
            for j in range(0, len(sf)):
                if sf[j] != si[j]:
                    fail = True
    if fail:
        print("Final state not reached")
        exit(-1)


def parse_movements(movs):
    result = []
    movs = movs.split('\n')
    for mov in movs:
        if mov == '':
            continue
        res = MOV_PATTERN.search(mov)
        block = int(res.group(1))
        dest = int(res.group(2))
        result.append((block, dest))
    return result


def parse_stack(line):
    stack = []
    res = line.split(' ')
    for block in res:
        try:
            stack.append(int(block))
        except ValueError:
            break
    return stack


def get_problem_states(filename):
    states = [[], []]

    f = open(filename, "r")
    num_of_blocks = f.readline()

    for state in range(0, 2):
        while True:
            line = f.readline()
            if not line or line == "\n":
                break
            states[state].append(parse_stack(line))
        state += 1

    return int(num_of_blocks), states[0], states[1]


def build_solution():
    solution = []
    file = open("result.txt", "r")
    while True:
        line = file.readline()
        if not line:
            break
        if line.find("mov(") > -1:
            solution.append(line.strip() + "\n")
    file.close()
    return ''.join(solution)


def final_stack_facts(stacks, offset):
    facts = []
    s = 1 + offset
    for stack in stacks:
        lv = 1
        for block in stack:
            facts.append(f'fn({s},{lv},{block})')
            lv += 1
        s += 1
    return facts


def stack_facts(stacks, offset=0):
    facts = []
    s = 1 + offset
    for stack in stacks:
        h = len(stack)
        facts.append(f'height({s},{h})')
        lv = 1
        for block in stack:
            facts.append(f'on({s},{lv},{block})')
            lv += 1
        s += 1
    return facts


def format_initial(facts):
    reformated = []
    for fact in facts:
        reformated.append(fact + ".\n")
    return "#program initial.\n" + ''.join(reformated)


def format_final(facts):
    reformated = []
    for fact in facts:
        reformated.append(fact + ",")
    return "#program final.\ngoal :-" + ''.join(reformated)[0:-1] + ".\n:- not goal."


def process_args():
    argv = sys.argv

    filename = argv[1]
    exhaustive = False
    shift = True
    checkplan = False
    telingo_path = "telingo"

    if len(argv) > 2:
        curr = 2
        while curr < len(argv):
            if argv[curr] == "-check":
                checkplan = True
            if argv[curr] == "-exhaustive":
                exhaustive = True
            if argv[curr] == "-noshift":
                shift = False
            if argv[curr] == "-telpath":
                if len(argv) < curr + 2:
                    print(HELP)
                    exit(0)
                curr += 1
                telingo_path = argv[curr]
            curr += 1

    return filename, exhaustive, shift, telingo_path, checkplan


def main(argv):
    filename, exhaustive, shift, telingo_path, checkplan = process_args()

    n, initial, final = get_problem_states(filename)
    facts1 = stack_facts(initial)
    initial_stacks = len(initial)
    total_stacks = initial_stacks + len(final)

    offset = 0
    if shift:
        offset = initial_stacks
    facts2 = stack_facts(final, offset)
    facts3 = final_stack_facts(final, offset)

    problem_file = open("instance.txt", "w")
    problem_file.write(f"#const n = {n}.\n")
    problem_file.write(f"#const s = {total_stacks}.\n")
    if exhaustive:
        problem_file.write("#program initial.\n exhaustive.\n")
    problem_file.write(format_initial(facts1 + facts3))
    problem_file.write(format_final(facts2))
    problem_file.close()

    system(telingo_path + " --verbose=0 encoding.txt instance.txt > result.txt 2> /dev/null")
    movs = build_solution()
    if checkplan:
        check(offset, parse_movements(movs), initial, final)
    print(movs)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(HELP)
        exit(0)
    main(sys.argv)
