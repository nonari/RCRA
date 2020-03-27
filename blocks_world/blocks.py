#!/usr/bin/python3

from os import system, stat
import sys

HELP = "blocks filename [--exhaustive] [--noshift]"


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


def main(argv):
    exhaustive = False
    shift = True
    for i in range(2, len(argv)):
        if argv[i] == "--exhaustive":
            exhaustive = True
        if argv[i] == "--noshift":
            shift = False
    filename = argv[1]

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

    statinfo = stat('telingo_path.config')
    if statinfo.st_size > 0:
        path_file = open("telingo_path.config")
        telingo_path = path_file.readline()
        if telingo_path.endswith('\n'):
            telingo_path = telingo_path[0:-1]
        path_file.close()
    else:
        telingo_path = "telingo"
    system(telingo_path + " --verbose=0 encoding.txt instance.txt > result.txt 2> /dev/null")
    print(build_solution())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(HELP)
        exit(0)
    main(sys.argv)
