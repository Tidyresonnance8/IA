"""NAMES OF THE AUTHOR(S): Alice Burlats <alice.burlats@uclouvain.be>"""

from pycsp3 import *


def solve_minesweeper(clues: list[list[int]]) -> list[(int, int)]:
    n = len(clues)
    m = len(clues[0])
    #création du plateau de varables (0 = vide, 1=mine)
    mines = VarArray(size=[n,m], dom={0,1})   
    for i in range(n):
        for j in range(m):
            if clues[i][j] != -1:
                # on collecte ici les voisins valide
                neighbors = []
                for a in [-1,0,1]:
                    for b in [-1,0,1]:
                        if a == 0 and b == 0:
                            continue
                        x,y = i+a, j+b
                        if 0 <= x < n and 0 <= y < m:
                            neighbors.append(mines[x][y])
                # la somme des voisins égale à l'indice
                satisfy(mines[i][j] == 0, Sum(neighbors) == clues[i][j])
    if solve() is SAT:
        solution = []
        for i in range(n):
            for j in range(m):
                if mines[i][j].value == 1:
                    solution.append((i,j))
        return solution

    return None


def check_solution(clues: list[list[int]], solution: list[(int, int)]) -> bool:
    n = len(clues)
    m = len(clues[0])
    mines_count = [[0 for _ in range(m)] for _ in range(n)]
    for x, y in solution:
        if clues[x][y] != -1:
            print(f"A mine is placed on a clue at position ({x},{y}), invalid solution")
            return False

        for a in [-1, 0, 1]:
            for b in [-1, 0, 1]:
                if 0 <= x+a < n and 0 <= y + b < m and (a != 0 or b != 0):
                    mines_count[x + a][y + b] += 1

    for i in range(n):
        for j in range(m):
            if mines_count[i][j] != clues[i][j] and clues[i][j] != -1:
                print(f"The clue at position ({i},{j}) is not respected: there is {mines_count[i][j]} mines instead of {clues[i][j]}")
                return False

    return True


def parse_instance(input_file: str) -> list[list[int]]:
    with open(input_file) as input:
        lines = input.readlines()
    clues = []
    for line in lines:
        row = []
        for cell in line.strip().split(" "):
            row.append(int(cell))
        clues.append(row)
    return clues


if __name__ == '__main__':
    clues = parse_instance("instances/sat/i01.txt")
    solution = solve_minesweeper(clues)
    if solution is not None:
        if check_solution(clues, solution):
            print("The returned solution is valid")
        else:
            print("The returned solution is not valid")
    else:
        print("No solution found")
