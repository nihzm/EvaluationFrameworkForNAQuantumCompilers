import random
from heapq import heappush, heappop
from pysat.formula import CNF

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

def get_graph(formula: CNF) -> tuple[list[int], list[set[int]]]:
    N = len(formula.clauses)
    V = [i for i in range(N)]
    E = [set() for _ in range(N)]
    for u in range(N):
        for v in range(u + 1, N):
            literal_set1 = set(map(abs, formula.clauses[u]))
            literal_set2 = set(map(abs, formula.clauses[v]))
            if len(literal_set1 & literal_set2) > 0:
                E[u].add(v)
                E[v].add(u) 
    return V, E

def _build_saturation_heap(uncolored: set[int], colored: set[int], edge_map: list[set[int]]) -> list[tuple[int, int, bool]]:
    pass

def get_color_map(formula: CNF) -> list[int]:
    V, E = get_graph(formula)
    color_map = [None for clause in formula.clauses]
    color_map[0] = 0
    colored = set([0])
    uncolored = set(i for i in range(1, len(formula.clauses)))
    num_colors = 1
    while len(uncolored) > 0:
        chosen, curr_saturation = -1, -1
        for clause in uncolored:
            saturation = 0
            for neighbor in E[clause]:
                if neighbor in colored:
                    saturation += 1
            if saturation > curr_saturation:
                chosen = clause
                curr_saturation = saturation
        colored_neighbors = filter(lambda v: color_map[v] is not None, E[chosen])
        used_colors = list(map(lambda v: color_map[v], colored_neighbors))
        used_colors.sort()
        color_map[chosen] = used_colors[-1] + 1 if len(used_colors) > 0 else 0
        prev_used_color = -1
        for curr_used_color in used_colors:
            if curr_used_color - prev_used_color > 1:
                color_map[chosen] = prev_used_color + 1
                break
            prev_used_color = curr_used_color
        colored.add(chosen)
        uncolored.remove(chosen)
        num_colors = max(num_colors, color_map[chosen] + 1)
    return num_colors, color_map