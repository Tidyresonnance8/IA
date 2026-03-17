"""NAMES OF THE AUTHOR(S): Alice Burlats <alice.burlats@uclouvain.be>"""

from pycsp3 import *

def solve_sudoku(clues):
    # x[i][j] is the value at row i and col j
    x = VarArray(size=[9, 9], dom=range(1, 10))

    satisfy(
    # constraint 1
    [AllDifferent(x[i]) for i in range(9)],

    # constraint 2
    [AllDifferent(x[:, j]) for j in range(9)],

    # constraint 3
    [AllDifferent(x[i:i + 3, j:j + 3]) for i in [0, 3, 6] for j in [0, 3, 6]],

    # constraint 4
    [x[i][j] == clues[i][j] for i in range(9) for j in range(9) if clues and clues[i][j] > 0],

    # ADD YOUR SUPPLEMENTARY CONSTRAINT HERE
    
    )

    # Solve the problem and print the solution if found
    if solve(solver=CHOCO) is SAT:
        print("SATISFIABLE")
        vals = values(x)
        solution = [vals[i*9:(i+1)*9] for i in range(9)]
        return solution
    else:
        print("UNSATISFIABLE")
        return None


if __name__ == "__main__":
    # Definition of the initial sudoku grid
    clues = [[0, 3, 0, 0, 5, 0, 0, 9, 0],
             [0, 0, 5, 0, 0, 8, 0, 0, 1],
             [6, 0, 0, 0, 7, 1, 0, 2, 0],
             [0, 0, 7, 2, 9, 0, 0, 0, 3],
             [0, 0, 2, 0, 0, 4, 7, 0, 9],
             [4, 0, 0, 0, 1, 0, 2, 5, 6],
             [0, 7, 0, 0, 0, 9, 0, 8, 2],
             [8, 0, 0, 1, 0, 7, 0, 0, 4],
             [0, 2, 0, 0, 3, 0, 1, 6, 0]]

    solution = solve_sudoku(clues)
    for row in solution:
        print(row)
