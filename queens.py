from math import trunc, fabs
from os import system

n = 8


def enc_queen(x: int, y: int):
    return y * n + x + 1


def generate_lines(clauses):
    for k in range(0, n):
        for x in range(0, n):
            for x_p in range(x + 1, n):
                qs1 = str(enc_queen(x, k))
                qs2 = str(enc_queen(x_p, k))
                qs3 = str(enc_queen(k, x))
                qs4 = str(enc_queen(k, x_p))
                clauses.append(f'-{qs1} -{qs2} 0\n-{qs3} -{qs4} 0\n')


def generate_diagonals(clauses):
    n_c = n - 1
    for k in range(0, n):
        x = 0
        for y in range(k, n):
            x_p = x + 1
            for y_p in range(y + 1, n):
                q1 = enc_queen(x, y)
                q2 = enc_queen(x_p, y_p)
                q3 = enc_queen(-x + n_c, y)
                q4 = enc_queen(-x_p + n_c, y_p)
                q5 = enc_queen(y, x)
                q6 = enc_queen(y_p, x_p)
                q7 = enc_queen(-y + n_c, x)
                q8 = enc_queen(-y_p + n_c, x_p)
                clauses.append(f'-{q1} -{q2} 0\n-{q3} -{q4} 0\n-{q5} -{q6} 0\n-{q7} -{q8} 0\n')
                x_p += 1
            x += 1


def non_void_rules(clauses):
    for y in range(0, n):
        line = []
        for x in range(0, n):
            line.append(f'{enc_queen(x, y)} ')
        line.append('0\n')
        clauses.append(''.join(line))


def generate_clauses():
    clauses = []

    generate_lines(clauses)

    generate_diagonals(clauses)

    non_void_rules(clauses)

    return clauses


def write(clauses):
    f = open("satfile.txt", "w")
    f.write(f"p cnf {n*n} {len(clauses)}\n")
    f.write(''.join(clauses))
    f.close()


def send():
    system("clasp --verbose=0 satfile.txt > result.txt")


def build_checkerboard():
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
                    add_number(checkerboard, negate, number)
                    number = ""
                    negate = False
                    continue
                if c == '-':
                    negate = True
                else:
                    number += c
    return checkerboard


def add_number(checkerboard, negate, number):
    state = int(number)
    if negate:
        state = -state
    checkerboard.append(state)


def display(checkerboard):
    i = 0
    line = []
    for s in checkerboard:
        if s > 0:
            line.append("Q ")
        else:
            line.append("x ")
        i += 1
        if i % n == 0:
            print(''.join(line))
            line = []


claus = generate_clauses()
write(claus)
send()
checker = build_checkerboard()
display(checker)
