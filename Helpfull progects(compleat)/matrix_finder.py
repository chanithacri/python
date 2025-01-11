import re


class MatrixFiller:
    def __init__(self, _row, _col, matrix):
        self._row = _row
        self.col = _col
        self.matrix = matrix
        self.issue_report = ""

    @classmethod
    def matrix_builder(cls):
        errors = ("Incorrect format, try again...",
                  "Ups... only square matrix can be symmetric.\n square matrix should have equal number of rows and colums",
                  "it doesn't make any sense...",
                  )

        def obtain_params():
            params = input("Enter the matrix size like: 3 3:\n")
            if not re.match(r"\A\d+ \d+$", params.strip()):
                print(errors[0])
                return main()
            row, col = params.split()
            row, col = int(row), int(col)

            if row != col:
                print(errors[1])
                return main()

            if row == "1":
                print(errors[2])
                return main()
            return row, col

        def input_check():
            mb = input("prease provide matrix values in one row,\nall denote empty values with '_' like: 1 2 0 _ _ _ 3 4 0 _ _ _ 0 8 6 7 _ _ -9 0 5 -1 _ _ 7\n").strip().split()
            if len(mb) != _row * _col:
                print("Invalid length! Please try again.\n")
                return input_check()
            return mb

        _row, _col = obtain_params()
        matrix_body = input_check()
        m1 = []
        x = 0
        while x != len(matrix_body):
            m1.append([element for element in matrix_body[x: x + _col]])
            x = x + _col
        matrix = m1
        print("Matrix successfully created:\n")
        print(*matrix, sep="\n")
        return cls(_row, _col, matrix)

    def is_symmetric(self):
        for row in range(self._row):
            for col in range(self._row):
                if all([self.matrix[row][col] != "_", self.matrix[col][row] != "_",  self.matrix[row][col] != self.matrix[col][row]]):
                    self.issue_report += f"{self.matrix[row][col]} in row {row} col {col} != {self.matrix[col][row]} in row {col} col {row}\n\n"
        if self.issue_report:
            return False
        return True

    def fill_symmetric_values(self):
        for row in range(len(self.matrix)):
            for column in range(len(self.matrix)):
                if self.matrix[row][column] != self.matrix[column][row]:
                    if self.matrix[row][column] == "_" and self.matrix[column][row].lstrip("-").isdigit():
                        self.matrix[row][column] = self.matrix[column][row]
                    elif self.matrix[column][row] == "_" and self.matrix[row][column].lstrip("-").isdigit():
                        self.matrix[column][row] = self.matrix[row][column]


def main():
    matrix = MatrixFiller.matrix_builder()

    print("Checking if your matrix is symmetric...:\n")
    if matrix.is_symmetric():
        print("Success!")
        matrix.fill_symmetric_values()
        print('\nThe result is below:\n', *matrix.matrix, sep="\n")
    else:
        print("Sorry, but your matrix is not symmetric, please find the report below:\n", matrix.issue_report)


if __name__ == '__main__':
    main()