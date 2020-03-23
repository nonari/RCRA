import re
from os import system
import sys


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
    pass


def stack_facts(stacks):
    facts = []
    s = 1
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
    return ''.join(reformated)


def format_final(facts):
    reformated = []
    for fact in facts:
        reformated.append(fact + ",")
    return "goal :-" + ''.join(reformated)[0:-1] + ".\n:- not goal"


def main(filename):
    n, initial, final = get_problem_states(filename)
    facts1 = stack_facts(initial)
    facts2 = stack_facts(final)

    problem_file = open("instance.txt", "w")
    problem_file.write(f"#const n = {n}.\n")
    problem_file.write(format_initial(facts1))
    problem_file.write(format_final(facts2))
    problem_file.close()
    system("telingo --verbose=0 encoding.txt instance.txt > result.txt")
    print(build_solution())


if __name__ == "__main__":
    main(sys.argv[1])
