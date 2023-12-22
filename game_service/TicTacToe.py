class TicTacToe:
    def __init__(self, n: int = 3):
        self.n = n
        self.board = [[None for _ in range(n)] for _ in range(n)]
        self.rows = [0]*n
        self.cols = [0]*n
        self.diag = 0
        self.anti_diag = 0
        self.tiles_left = n*n

        self.player1 = None
        self.player2 = None

        self.current_player = None

    def get_state(self):
        return self.board

    def move(self, row: int, col: int, player: str) -> int:
        if self.board[row][col] != None or row < 0 or row >= self.n or col < 0 or col >= self.n:
            return None
        
        self.board[row][col] = 1 if player == self.player1 else 2
        self.tiles_left -= 1

        if player == self.player1:
            x = 1
        else:
            x = -1

        self.rows[row] += x
        self.cols[col] += x

        if row - col == 0:
            self.diag += x

        if row + col == self.n-1:
            self.anti_diag += x

        if self.rows[row] == self.n or self.cols[col] == self.n or self.diag == self.n or self.anti_diag == self.n:
            return 1
        
        if self.rows[row] == -self.n or self.cols[col] == -self.n or self.diag == -self.n or self.anti_diag == -self.n:
            return 2

        if self.tiles_left == 0:
            return -1

        return 0