from clause import *

"""
For the color grid problem, the only code you have to do is in this file.

You should replace

# your code here

by a code generating a list of clauses modeling the grid color problem
for the input file.

You should build clauses using the Clause class defined in clause.py

Read the comment on top of clause.py to see how this works.
"""


def get_expression(size, points=None):
    expression = []
    n = size
    E = range(n)

    for i in E:
        for j in E:  # each cell has to be colored
            color_clause = Clause(n)
            for k in E:
                color_clause.add_positive(i, j, k)
            expression.append(color_clause)

    for k in E:
        for i in E:
            for j in E:
                for j2 in E:  # line clause
                    if j2 != j:
                        line_clause = Clause(n)
                        line_clause.add_negative(i, j, k)
                        line_clause.add_negative(i, j2, k)
                        expression += [line_clause]

                for i2 in E:  # row clause
                    if i2 != i:
                        row_clause = Clause(n)
                        row_clause.add_negative(i, j, k)
                        row_clause.add_negative(i2, j, k)
                        expression += [row_clause]

                for l in range(1, n):  # diagonal clause
                    diag_clause = Clause(n)
                    diag_clause.add_negative(i, j, k)
                    diag_clause.add_negative((i + l) % n, (j + l) % n, k)
                    expression += [diag_clause]

                    anti_diag_clause = Clause(n)
                    anti_diag_clause.add_negative(i, j, k)
                    anti_diag_clause.add_negative((i + l) % n, (j - l) % n, k)
                    expression += [anti_diag_clause]

    if points is not None:
        for point in points: # respect points cell
            point_clause = Clause(n)
            point_clause.add_positive(point[0], point[1], point[2])
            expression += [point_clause]

    return expression

if __name__ == '__main__':
    expression = get_expression(5)
    for clause in expression:
        print(clause)
