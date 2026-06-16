def is_safe(board, row, col, n):
    # بررسی ستون
    for i in range(col):
        if board[row][i] == 1:
            return False

    # بررسی قطر بالا سمت چپ
    for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
        if board[i][j] == 1:
            return False

    # بررسی قطر پایین سمت چپ
    for i, j in zip(range(row, n, 1), range(col, -1, -1)):
        if board[i][j] == 1:
            return False

    return True

def solve_n_queens(board, col, n):
    if col >= n:
        return True

    for i in range(n):
        if is_safe(board, i, col, n):
            board[i][col] = 1
            if solve_n_queens(board, col + 1, n):
                return True
            board[i][col] = 0

    return False

def print_board(board):
    for row in board:
        print(" ".join(str(x) for x in row))

def n_queens(n):
    board = [[0 for _ in range(n)] for _ in range(n)]
    if not solve_n_queens(board, 0, n):
        print("No solution exists")
        return
    print_board(board)

n = int(input("Enter the value of n: "))
n_queens(n)
