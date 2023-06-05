
from enum import Enum
from random import randrange
from queue import Queue

class EdgeOrType(Enum):
    ORIENTED   = 0
    UNORIENTED = 1

class EdgeWType(Enum):
    WEIGHTED   = 0
    UNWEIGHTED = 1

class InputType(Enum):
    EDGE_LIST           = 0
    CONNECTIVITY_LIST   = 1
    CONNECTIVITY_MATRIX = 2
    INIDENCE_MATRIX     = 3
    NO_INPUT            = 4

class Point:

    def __init__(self, x:float=0, y:float=0):
        self.x = x
        self.y = y

    def copy(self):
        return Point(self.x, self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __imul__(self, l:float):
        self.x *= l
        self.y *= l
        return self
    
    def __mul__(self, l:float):
        return self.copy().__imul__(l)
    
    def __idiv__(self, l:float):
        self.x /= l
        self.y /= l
        return self
    
    def __truediv__(self, l:float):
        return self.copy().__idiv__(l)
    
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self
    
    def __add__(self, other):
        return self.copy().__iadd__(other)
    
    def __neg__(self):
        return Point(-self.x, -self.y)
    
    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self
    
    def __sub__(self, other):
        return self.copy().__isub__(other)
    
    def scalar(self, other):
        return self.x * other.x + self.y * other.y
    
    def len(self):
        return self.scalar(self)**(1/2)
    
    def pos(self):
        return (int(self.x), int(self.y))
    
    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'
    
    def _repr__(self):
        return str(self)

class Vertex:
    count: int = 0
    def __init__(self, name, R:int=0, stable:bool=False, degree:int=0,  \
                                      r:Point=Point(),    \
                                      v:Point=Point(),    \
                                      a:Point=Point(), color:tuple=(255, 255, 255),):
        self.name = str(name)
        self.R = R
        self.stable = stable
        self.r = r.copy()
        self.v = v.copy()
        self.a = a.copy()
        self.color = color
        self.index = Vertex.count
        Vertex.count += 1
        self.degree = degree


    def copy(self):
        return Vertex(self.name, self.R, self.stable, self.degree, self.r, self.v, self.a)

    def __eq__(self, other):
        return self.name == other.name
    
    def __neq__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return self.name < other.name
    
    def __hash__(self):
        return hash(self.name)
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def move(self, dt: float, edges, size):
        if not self.stable:
            if (0 < self.r.x - edges[0].x - size  < 20 and self.v.x < 0) or \
               (0 < edges[1].x + edges[0].x - size - self.r.x < 20 and self.v.x > 0):
                self.v -= Point(self.v.x, 0) * 2
            if (0 < self.r.y - edges[0].y - size < 20 and self.v.y < 0) or \
                 (0 < edges[1].y + edges[0].y - size - self.r.y < 20 and self.v.y > 0):
                self.v -= Point(0, self.v.y) * 2
            self.r += self.v * dt + self.a * dt**2/2
            self.v += self.a * dt
            if self.v.len() > 200:
                self.v = self.v * 200 / self.v.len()

    def pos(self):
        return self.r.pos()

class Edge:
    count: int = 0

    def __init__(self, v:Vertex, u:Vertex, name:str='', weighted:bool=False, w:float=0, color:tuple=(0,0,0)):
        self.index = Edge.count
        Edge.count += 1
        self.v = v
        self.u = u
        self.name = name
        self.weighted = weighted
        self.color = color
        if self.weighted:
            self.w = w
        else:
            self.w = 0

    def copy(self):
        return Edge(self.v.copy(), self.u.copy(), self.name, self.weighted, self.w)

    def __eq__(self, other):
        return  self.name == other.name and \
                self.v == other.v and \
                self.u == other.u and \
                self.weighted == other.weighted and \
                self.w == other.w
    
    def __neq__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return self.v < other.v or self.u.name < other.u.name or self.w < other.w

    def __hash__(self):
        return hash((self.name, self.u.name, self.name, self.weighted, self.w, self.index))
    
    def __str__(self):
        if self.weighted:
            return '<' + str(self.v) + ',' + str(self.u) + ',' + str(self.w) + '>'
        else:
            return '<' + str(self.v) + ',' + str(self.u) + '>'
    
    def __repr__(self):
        return str(self)

    def reverse(self): 
        return Edge(self.u, self.v, self.name, self.weighted, self.w)

class Graph:
    
    def __init__(self, input, type:InputType, wtype: EdgeWType=EdgeWType.UNWEIGHTED, ortype: EdgeOrType=EdgeOrType.UNORIENTED, scale=300, size=15, edges=(Point(), Point(1000,1000))):
        self.V = set()
        self.E = set()
        self.ortype = ortype
        self.wtype = wtype
        self.is_coherent = None
        self.delta = float('inf')
        if type == InputType.EDGE_LIST:
            for i in input:
                if len(i) < 2:
                    self.V.add(Vertex(i[0]))
                else:
                    self.V.update([Vertex(i[0]), Vertex(i[1])])

            for i in input:
                if len(i) < 2:
                    continue
                v = Vertex(i[0])
                u = Vertex(i[1])
                for j in self.V:
                    if j == v:
                        v = j
                    if j == u:
                        u = j
                v.degree += 1
                if ortype == EdgeOrType.UNORIENTED:
                    u.degree += 1

                if wtype == EdgeWType.WEIGHTED:
                    e = Edge(v, u, weighted=True, w=i[2])
                else:
                    e = Edge(v, u)
                self.E.add(e)
                if v != u and ortype == EdgeOrType.UNORIENTED:
                    self.E.add(e.reverse())
            self.is_coherent = self.coherent()
        self.n = len(self.V)
        self.m = len(self.E)
        self.scale = scale
        self.size = size
        self.edges = edges

    def clear(self):
        self.V.clear()
        self.E.clear()
        self.ortype=EdgeOrType.UNORIENTED
        self.wtype=EdgeWType.UNWEIGHTED
        self.scale = 0
        self.size = 0
        self.edges = (Point(0, 0), Point(0, 0))

    def copy(self):
        _G = Graph(InputType.NO_INPUT, [], wtype=self.wtype, ortype=self.ortype, scale=self.scale, size=self.size, edges=self.edges)
        _G.V = self.copy_vertexs()
        for e in self.E:
            v = _G.find_vertex(e.v)
            u = _G.find_vertex(e.u)
            _G.E.add(Edge(v, u, e.name, e.weighted, e.w))
        _G.n = self.n
        _G.m = self.m
        return _G

    def find_edge(self, v, u, name='', weighted=False, w=0):
        e = Edge(v, u, name, weighted, w)
        for _e in self.E:
            if e == _e:
                return _e
        return None

    def find_vertex(self, v):
        for _v in self.V:
            if v == _v:
                return _v
        return None

    def __eq__(self, other):
        return self.V == other.V and self.E == other.E
    
    def __neq__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        s = '{'
        for e in self.E:
            s += str(e) + ','
        return s[:-1] + '}'
    
    def __repr__(self):
        return str(self)

    def generate_positions(self, edges = (Point(0, 0), Point(1000, 1000))):
        for v in self.V:
            r = Point(0, 0)
            while r in [v.r for v in self.V]:
                r = Point(randrange(int(1.2*edges[0].x + self.size), int(0.8*edges[1].x - self.size)), \
                            randrange(int(1.2*edges[0].y + self.size), int(0.8*edges[1].y - self.size)))
            v.r = r

    def copy_vertexs(self):
        _V = set()
        for v in self.V:
            _V.add(v.copy())
        return _V

    def remove_edges(self, E:set):
        _G = self.copy()
        _G.remove_edges_update(E)
        return _G
    
    def remove_nodes(self, V:set):
        _G = self.copy()
        _G.remove_nodes_update(V)
        return _G

    def remove_edges_update(self, E:set):
        self.is_coherent = None
        self.delta = float('inf')
        _E = set([self.find_edge(e.v, e.u, e.name, e.weighted, e.w) for e in E]).copy()
        if self.ortype == EdgeOrType.UNORIENTED:
            for e in E:
                _E.add(self.find_edge(e.u, e.v, e.name, e.weighted, e.w))
        for v in self.V:
            for e in _E:
                if v == e.v and v != e.u:
                    v.degree -= 1
        self.E.difference_update(_E)
        self.m = len(self.E)

    def remove_nodes_update(self, V:set):
        self.is_coherent = None
        self.delta = float('inf')
        _V = set()
        _E = set()
        for v in V:
            _V.add(self.find_vertex(v))
            for e in self.E:
                if v == e.u:
                    _e = self.find_edge(e.v, e.u, e.name, e.weighted, e.w)
                    _E.add(_e)
                    _e.v.degree -= 1
        self.V.difference_update(_V)
        self.E.difference_update(_E)
        self.n = len(self.V)
        self.m = len(self.M)


    def coherent(self, v=None, marked=None):
        if marked == None:
            md = {v.index : False for v in self.V}
        else:
            md = marked
        if v is None:
            v = next(iter(self.V))
            md[v.index] = True
        for u in [e.u for e in self.E if v == e.v]:
            if not md[u.index]:
                md[u.index] = True
                self.coherent(u, md)
        if marked == None:
            for v in md:
                if md[v] == False:
                    return False
            return True
        return None

    def cg(self) -> Point:
        r = Point()
        for v in self.V:
            r += v.r
        return r / len(self.V)

    def update_positions(self, dt:float):
        for v in self.V:
            v.a = Point(0, 0)
            for u in self.V:
                if not u is v:
                    r = v.r - u.r
                    if abs(r.len() - self.scale) < 10:
                        v.v += -r*Point.scalar(v.v, r)/r.len()**2
                        v.a += -r*Point.scalar(v.a, r)/r.len()**2 * 0.7
                    elif r.len() > self.scale:
                        v.a += -r / (r.len() / self.scale)**3 / 10**3
                    else:
                        v.a += r / (r.len() / self.scale)**3 / 10**3

                    
        for v in self.V:
            v.move(dt, self.edges, self.size)

    def eq_classes(self):
        eqc = []
        for e in self.E:
            placed = False
            for X in eqc:
                for x in X:
                    if x is e:
                        placed = True
                        continue
                if placed:
                    break
                if e == X[0]:
                    X.append(e)
                    placed = True
                    break
            if placed:
                continue
            else:
                eqc.append([e])
        return eqc

    

    def eulers_way(self, vs=None):
        if self.is_coherent == None and self.m > 0:
            self.is_coherent = self.coherent()
        if self.is_coherent and len([v for v in self.V if v.degree % 2 == 1]) != 2:
            return []
        else:
            eulers_way = []
            _G = self.copy()
            st = list()
            if vs is None:
                for v in _G.V:
                    if v.degree % 2 == 1:
                        st.append(v)
                        break
            else:
                st.append(_G.find_vertex(vs))
            while len(st) > 0:
                v = st[-1]
                if v.degree == 0:
                    eulers_way.append(v)
                    st.pop(-1)
                else:
                    for _e in _G.E:
                        if v == _e.v:
                            e = _e
                            break
                    st.append(e.u)
                    _G.remove_edges_update(set([e]))   
        return eulers_way

    def eulers_cycle(self):
        if self.is_coherent == None and self.m > 0:
            self.is_coherent = self.coherent()
        if self.is_coherent and len([v for v in self.V if v.degree % 2 == 1]) > 0:
            return []
        else:
            bridge = next(iter(self.E))
            v = bridge.v
            _G = self.remove_edges(set([bridge]))
            eulers_cycle = _G.eulers_way(bridge.u)
            eulers_cycle.append(v)
        return eulers_cycle

    def is_graph(self):
        for e in self.E:
            if e.v == e.u or e in self.E.difference([e]):
                return False
        return True

    def least_degree(self):
        return min([v.degree for v in self.V])
    
    def is_gamiltons_graph(self):
        if self.is_coherent is None:
            self.is_coherent = self.coherent()
        if self.delta == float('inf'):
            self.delta = self.least_degree()
        return self.ortype == EdgeOrType.UNORIENTED and self.is_coherent and self.n >= 3 and self.delta >= self.n / 2
    
    def gamils_cycle(self):
        if not self.is_gamiltons_graph():
            return []
        q = list(self.V)
        for k in range(0, self.n * (self.n - 1)):
            if self.find_edge(q[0], q[1]) is None:
                i = 2
                while self.find_edge(q[0], q[i]) is None or self.find_edge(q[1], q[i + 1]) is None:
                    i += 1
                j = 0
                while 1 + j < i - j:
                    q[1 + j], q[i - j] = q[i - j], q[1 + j]
                    j += 1
            q += [q[0]]
            q = q[1:]
        return [q[-1]] + q
    
    def gamils_way(self):
        if not self.is_gamiltons_graph():
            return []
        _G = self.copy()
        v = Vertex('R')
        for u in _G.V:
            _G.E.update([Edge(v, u), Edge(u, v)])
        v.degree = _G.n
        _G.V.add(v)
        q = _G.gamils_cycle()[1:]
        i = 0
        while q[i] != v:
            i += 1
        q = q[i+1:] + q[:i]
        return q
                


