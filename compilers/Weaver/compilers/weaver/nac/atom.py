class Atom:
    def __init__(self, id: int, is_slm: bool, row: int, col: int):
        self.id = id
        self.is_slm = is_slm
        self.row = row
        self.col = col

    def assign_trap(self, is_slm: bool, row: int, col: int):
        self.is_slm = is_slm
        self.row = row
        self.col = col
        
        