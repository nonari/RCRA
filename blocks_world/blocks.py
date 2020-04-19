#!/usr/bin/python3

from os import system
import sys, re

MOV_PATTERN = re.compile('mov\(([0-9]+),([0-9]+)\)')

HELP = "blocks filename [-heuristic] [-telpath <path>]"


def list_to_dict(stacks):
    dic = dict()
    for stack in stacks:
        if len(stack) > 0:
            fst_block = stack[0]
            dic[fst_block] = stack
    return dic


def translate(movs, initial, final):
    translated = []
    for mov in movs:
        block = mov[0]
        dest = mov[1]

        found = False
        for k in initial.keys():
            if len(initial[k]) > 0 and initial[k][-1] == block:
                found = True
                initial[k].remove(block)
        if not found:
            print(f'block {block} is not at any peak')
        if block == dest:
            translated.append(f'm{block, 0}\n')
            initial[block] = [block]
        else:
            translated.append(f'm{block, initial[dest][-1]}\n')
            initial[dest].append(block)

    fail = False
    for k in initial.keys():
        if k in final:
            if len(final[k]) == len(initial[k]):
                if len(final[k]) == 0:
                    continue
                if len(initial[k]) != 0:
                    for j in range(0, len(initial[k])):
                        if initial[k][j] != final[k][j]:
                            fail = True
            else:
                fail = True
                pass
    if fail:
        print("Final state not reached")
        exit(1)

    return ''.join(translated)


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


def final_stack_facts(stacks):
    facts = []
    for stack in stacks:
        lv = 1
        s = stack[0]
        for block in stack:
            facts.append(f'fn({s},{lv},{block})')
            lv += 1
        s += 1
    return facts


def stack_facts(stacks):
    facts = []
    for stack in stacks:
        lv = 1
        s = stack[0]
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
    exhaustive = True
    telingo_path = "telingo"

    if len(argv) > 2:
        curr = 2
        while curr < len(argv):
            if argv[curr] == "-heuristic":
                exhaustive = False
            if argv[curr] == "-telpath":
                if len(argv) < curr + 2:
                    print(HELP)
                    exit(0)
                curr += 1
                telingo_path = argv[curr]
            curr += 1

    return filename, exhaustive, telingo_path


def main():
    filename, exhaustive, telingo_path = process_args()

    n, initial, final = get_problem_states(filename)
    facts1 = stack_facts(initial)

    facts2 = stack_facts(final)
    facts3 = final_stack_facts(final)

    problem_file = open("instance.txt", "w")
    problem_file.write(f"#const n = {n}.\n")
    if exhaustive:
        problem_file.write("#program initial.\n exhaustive.\n")
    problem_file.write(format_initial(facts1 + facts3))
    problem_file.write(format_final(facts2))
    problem_file.close()

    system(telingo_path + " --verbose=0 encoding.txt instance.txt > result.txt 2> /dev/null")
    movs = build_solution()
    translated = translate(parse_movements(movs), list_to_dict(initial), list_to_dict(final))
    print(translated)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(HELP)
        exit(0)
    main()
