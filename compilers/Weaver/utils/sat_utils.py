import random

random.seed()

def uniformly_random_independent_clauses(num_clauses: int, start_literal_id: int=1) -> list[tuple[int]]:
    literal = start_literal_id
    clauses = []
    for _ in range(num_clauses):
        signs = list(map(lambda s: 1 if s == 1 else -1, [random.getrandbits(1) for _ in range(3)]))
        clause = [signs[i] * (literal + i) for i in range(3)]
        clauses.append(tuple(clause))
        literal += 3
    return clauses