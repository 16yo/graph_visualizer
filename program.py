from graph import *

li = [
    [1, 2],
    [1, 3],
    [2, 3],
    [2, 4],
    [3, 4],
    [3, 5],
    [4, 5],
    [1, 5],
    [1, 6],
    [6, 5],
    [6, 3]
]

G = Graph(li, InputType.EDGE_LIST, scale=300, size=30)

print(G.gamils_way())

print(G.E)