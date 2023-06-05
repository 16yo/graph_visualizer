import pygame
from pygame.locals import * 
from graph import *
from math import pi, tan, atan, cos, sin, exp

def draw_node(screen, color, pos, size, name='',borderline=2):
    pygame.draw.circle(screen, (0, 0, 0), pos, size+borderline)
    pygame.draw.circle(screen, color, pos, size)

    if name != '':
        font = pygame.font.SysFont('freesansbold.ttf', size)    
        img = font.render(name, True,
                          pygame.Color((0, 0, 0)),
                          pygame.Color((255, 255, 255)))
        screen.blit(img, (pos[0] - img.get_width() / 2,
                          pos[1] - img.get_height() / 2))

def polar_angle(x, y):
    if x == 0:
        if y < 0:
            return 3/2*pi
        if y > 0:
            return pi/2
    if y == 0:
        if x < 0:
            return pi
        if x > 0:
            return 0
    if y < 0 and x > 0:
        gamma = atan(abs(y / x))
    elif y < 0 and x < 0:
        gamma = pi - atan(abs(y / x))
    elif y > 0 and x < 0:
        gamma = 3/2*pi - atan(abs(x / y))
    elif y > 0 and x > 0:
        gamma = 2 * pi - atan(abs(y / x))
    return gamma

def draw_loop(screen, color, v, scale, pc, n):
    alpha = 2 * pi / n
    l = 0
    r = scale / 10
    dy = 2*r / pc
    k = 0
    while k < n: 
        gamma = alpha * k + pi
        l = 0
        p = [[v.r.x, v.r.y]]
        _p = [[v.r.x, v.r.y]]
        while l <= pc:
            y = l * dy
            x = (r**2 - (y - r)**2)**(1/2)
            p.append([v.r.x + cos(gamma) * x + sin(gamma) * y, v.r.y - sin(gamma) * x + cos(gamma) * y])
            _p.append([v.r.x + cos(gamma) * (-x) + sin(gamma) * y, v.r.y - sin(gamma) * (-x) + cos(gamma) * y])
            l += 1
        pygame.draw.lines(screen, color, False, p, 2)
        pygame.draw.lines(screen, color, False, _p, 2)
        k += 1

def draw_arc(screen, color, v, u, scale, pc, n):
    _n = n - (n % 2)
    r = u.r - v.r
    alpha = atan(scale / r.len()) * 2/6
    gamma = polar_angle(r.x, r.y)
    a = r.len() / 2
    dx = r.len() / pc
    b0 = a * tan(alpha)
    d = 2 * b0 / _n
    k = 0
    b = b0 - d * k
    while k < _n / 2:
        l = 1
        p = [[v.r.x, v.r.y]]
        _p = [[v.r.x, v.r.y]]
        while l < pc:
            x = l * dx
            y = b * (1 - (x / a - 1)**2)**(1/2)
            p.append([v.r.x + cos(gamma) * x + sin(gamma) * y, v.r.y - sin(gamma) * x + cos(gamma) * y])
            _p.append([v.r.x + cos(gamma) * x + sin(gamma) * (-y), v.r.y - sin(gamma) * x + cos(gamma) * (-y)])
            l += 1
        p.append([u.r.x, u.r.y])
        _p.append([u.r.x, u.r.y])
        pygame.draw.lines(screen, color, False, p, 2)
        pygame.draw.lines(screen, color, False, _p, 2)
        k += 1
        b = b0 - d * k

def draw_edge(screen, edges, scale, pc=10):
    if len(edges) == 0:
        return
    e = next(iter(edges))
    v = e.v
    u = e.u
    n = len(edges)
    if v == u:
        draw_loop(screen, e.color, v, scale, 2*pc, n)
    else:
        if n % 2 == 1:
            pygame.draw.aaline(screen, e.color, v.pos(), u.pos())
        if n > 1:
            draw_arc(screen, e.color, v, u, scale, pc, n)


def is_valid_edges_input(texts):
    for text in texts:
        t = [a for a in text.split(' ') if a != '' and a != '\n']
        if not (0 < len(t) < 4):
            return False
    return True

def show_way(way, G, alg_count, last_edge, to_show):
    if alg_count == len(way):
        last_edge.v.color = (255, 255, 255)
        last_edge.u.color = (255, 255, 255)
        to_show = False
        way = []
        alg_count = 0
    else:
        if alg_count == 0:
            G.find_vertex(way[0]).color = (255, 0, 0)
        else:
            if alg_count == 1:
                G.find_vertex(way[0]).color = (255, 255, 255)
            else:
                last_edge.v.color = (255, 255, 255)
                last_edge.u.color = (255, 255, 255)
            last_edge = G.find_edge(way[alg_count - 1], way[alg_count])
            last_edge.u.color = (255, 0, 0)
        alg_count += 1
    return way, alg_count, last_edge, to_show

# Window settings
WIDTH  = 1000
HEIGHT = 800

screen = pygame.display.set_mode([WIDTH, HEIGHT])

pygame.display.set_caption('Euler\'s & Gamilton\'s ways and cycles')

# Edges
graph_edges = (Point(300, 50), Point(WIDTH-300, HEIGHT-150))
input_edges = (Point(0, 50), Point(300, HEIGHT - 150))
buttons_edges = (Point(0, HEIGHT - 100), Point(300, 200))
alg_edges = (Point(300, HEIGHT - 100), Point(WIDTH-300, 200))

# Graph example
li = [
    ['A', 'B'],
    ['A', 'B'],
    ['A', 'C'],
    ['A', 'C'],
    ['A', 'D'],
    ['C', 'D'],
    ['A', 'E'],
    ['E', 'C']
]

G = Graph(li, InputType.EDGE_LIST, scale=300, size=30, edges=graph_edges)

G.generate_positions(graph_edges)

edge_eqc = G.eq_classes()

# Font
pygame.font.init()
font = pygame.font.SysFont('freesansbold.ttf', 32)
button_font = pygame.font.SysFont('freesansbold.ttf', 18)

# Boxes and buttons
if True:
    graph_box = pygame.Rect((graph_edges[0].x, graph_edges[0].y, graph_edges[1].x, graph_edges[1].y))
    input_box = pygame.Rect((input_edges[0].x, input_edges[0].y, input_edges[1].x, input_edges[1].y))
    input_box_active = False
    buttons_box = pygame.Rect((buttons_edges[0].x, buttons_edges[0].y, buttons_edges[1].x, buttons_edges[1].y))
    buttons_box_active = False
    alg_box = pygame.Rect((alg_edges[0].x, alg_edges[0].y, alg_edges[1].x, alg_edges[1].y))
    alg_box_active = False
    graph_box = pygame.Rect((graph_edges[0].x, graph_edges[0].y, graph_edges[1].x, graph_edges[1].y))
    graph_box_active = False

    update_graph_button = pygame.Rect((0.1*buttons_edges[1].x+buttons_edges[0].x, 0.1*buttons_edges[1].y+buttons_edges[0].y, \
                                       0.3*buttons_edges[1].x, 0.3*buttons_edges[1].y))


    clear_graph_button = pygame.Rect((0.6*buttons_edges[1].x+buttons_edges[0].x, 0.1*buttons_edges[1].y+buttons_edges[0].y, \
                                       0.3*buttons_edges[1].x, 0.3*buttons_edges[1].y))

    eulers_way_button = pygame.Rect((0.072*alg_edges[1].x+alg_edges[0].x, 0.1*alg_edges[1].y+alg_edges[0].y, \
                                       0.16*alg_edges[1].x, 0.3*alg_edges[1].y))
    show_eulers_way = False
    eulers_cycle_button = pygame.Rect((0.304*alg_edges[1].x+alg_edges[0].x, 0.1*alg_edges[1].y+alg_edges[0].y, \
                                       0.16*alg_edges[1].x, 0.3*alg_edges[1].y))
    show_eulers_cycle = False
    gamils_way_button = pygame.Rect((0.536*alg_edges[1].x+alg_edges[0].x, 0.1*alg_edges[1].y+alg_edges[0].y, \
                                       0.16*alg_edges[1].x, 0.3*alg_edges[1].y))
    show_gamils_way = False
    gamils_cycle_button = pygame.Rect((0.768*alg_edges[1].x+alg_edges[0].x, 0.1*alg_edges[1].y+alg_edges[0].y, \
                                       0.16*alg_edges[1].x, 0.3*alg_edges[1].y))
    show_gamils_cycle = False

# Color
if True:    
    color_inactive = (128, 128, 128)
    color_active = (0, 0, 0)
    color = color_inactive
    active = False

# For input box
if True:
    line=0
    texts = []

    for l in li:
        texts.append(str(line + 1) + ': ' + str(l[0]) + ' ' + str(l[1]) + '\n')
        line += 1

    line -= 1
    texts[line] = texts[line][:-1]

# Text
if True:
    edges_input_box_header = font.render('Graph edges:', True, (0, 0, 0))
    update_graph_button_text = button_font.render('Update graph', True, (0, 0, 0))
    clear_graph_button_text = button_font.render('Clear graph', True, (0, 0, 0))

    eulers_way_button_text = button_font.render('Euler\'s way', True, (0, 0, 0))
    eulers_cycle_button_text = button_font.render('Euler\'s cycle', True, (0, 0, 0))

    gamils_way_button_text = button_font.render('Gamilton\'s way', True, (0, 0, 0))
    gamils_cycle_button_text = button_font.render('Gamilton\'s cycle', True, (0, 0, 0))

# Warnings
if True:
    show_warning = 0

    wrong_edges_input_warning = font.render('Wrong edges input warning!', True, (255, 0, 0))

    no_eulers_way_warning = font.render('There\' no Euler\'s way in this graph', True, (0, 0, 0))
    no_eulers_cycle_warning = font.render('There\' no Euler\'s cycle in this graph', True, (0, 0, 0))

    no_gamils_way_warning = font.render('Given graph doesn\'t satisfy Dirac\'s theorem  condition', True, (0, 0, 0))
    no_gamils_cycle_warning = font.render('Given graph doesn\'t satisfy Dirac\'s theorem  condition', True, (0, 0, 0))

    wait_warning = font.render('Please, wait until running algorithm stop', True, (0, 0, 0))


tick = 0
dt = 0.01

last_edge = None
alg_count = 0
algo_active = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            show_warning = 0
            input_box_active = buttons_box_active = alg_box_active = graph_box_active = False
            if input_box.collidepoint(event.pos):
                input_box_active = True
            if buttons_box.collidepoint(event.pos):
                buttons_box_active = True
            if alg_box.collidepoint(event.pos):
                alg_box_active = True
            if graph_box.collidepoint(event.pos):
                graph_box_active = True
            if update_graph_button.collidepoint(event.pos):
                if is_valid_edges_input(texts):
                    li = []
                    for text in texts:
                        t = [a for a in text.split(' ') if a != '' and a != '\n']
                        if len(t) > 1:
                            v = t[1]
                            if len(t) < 3:
                                if v[-1] == '\n':
                                    v = v[:-1]
                                li.append([v])
                            else:
                                u = t[2]
                                if u[-1] == '\n':
                                    u = u[:-1]
                                li.append([v, u])
                    G = Graph(li, InputType.EDGE_LIST, scale=300, size=30, edges=graph_edges)
                    G.generate_positions(graph_edges)
                    edge_eqc = G.eq_classes()

                    eulers_way = []
                    show_eulers_way = False
                    eulers_cycle = []
                    show_eulers_cycle = False
                    gamils_way = []
                    show_gamils_way = False
                    gamils_cycle = []
                    show_gamils_cycle = False

                    print(G)
                else:
                    show_warning = 1
            if eulers_way_button.collidepoint(event.pos):
                if algo_active:
                    show_warning = 6
                else:
                    eulers_way = G.eulers_way()
                    if len(eulers_way) == 0:
                        show_warning = 2
                    else: 
                        show_eulers_way = True
                        chain = font.render('Chain: ' + str(eulers_way), True, (0, 0, 0))
                        print(eulers_way)
            if eulers_cycle_button.collidepoint(event.pos):
                if algo_active:
                    show_warning = 6
                else:
                    eulers_cycle = G.eulers_cycle()
                    if len(eulers_cycle) == 0:
                        show_warning = 3
                    else: 
                        show_eulers_cycle = True
                        chain = font.render('Cycle: ' + str(eulers_cycle), True, (0, 0, 0))
                        print(eulers_cycle)
            if gamils_way_button.collidepoint(event.pos):
                if algo_active:
                    show_warning = 6
                else:
                    gamils_way = G.gamils_way()
                    if len(gamils_way) == 0:
                        show_warning = 4
                    else:
                        show_gamils_way = True
                        chain = font.render('Chain: ' + str(gamils_way), True, (0, 0, 0))
                        print(gamils_way)
            if gamils_cycle_button.collidepoint(event.pos):
                if algo_active:
                    show_warning = 6
                else:
                    gamils_cycle = G.gamils_cycle()
                    if len(gamils_cycle) == 0:
                        show_warning = 5
                    else:
                        show_gamils_cycle = True
                        chain = font.render('Cycle: ' + str(gamils_cycle), True, (0, 0, 0))
                        print(gamils_cycle)
            if clear_graph_button.collidepoint(event.pos):

                texts = ['1: ']
                line = 0
                G.clear()
                edge_eqc = []

                eulers_way = []
                show_eulers_way = False
                eulers_cycle = []
                show_eulers_cycle = False
                gamils_way = []
                show_gamils_way = False
                gamils_cycle = []
                show_gamils_cycle = False
                
        if event.type == pygame.KEYDOWN:
            if input_box_active:
                if event.key == pygame.K_RETURN:
                    texts[line] += '\n'
                    line += 1
                    texts.append(str(line + 1) + ': ')
                elif event.key == pygame.K_BACKSPACE:
                    if line > 0 and texts[line] == str(line + 1) + ': ':
                        texts = texts[:-1]
                        line -= 1
                    if line > 0 or texts[0] != '1: ':
                        texts[line] = texts[line][:-1]
                else:
                    texts[line] += event.unicode

    screen.fill((255, 255, 255))


    # Panels and texts
    if True:
        # Input box
        screen.blit(edges_input_box_header, (input_box.x+5, input_box.y-22))

        edges_input = [font.render(text, True, color_active if input_box_active else color_inactive) for text in texts]
        for i in range(len(edges_input)):
            screen.blit(edges_input[i], (input_box.x + 5, input_box.y+5+22*i))

        pygame.draw.rect(screen, color_active if input_box_active else color_inactive, input_box, 4)


        # Panels
        pygame.draw.rect(screen, color_active if buttons_box_active else color_inactive, buttons_box, 4)

        pygame.draw.rect(screen, color_active if alg_box_active else color_inactive, alg_box, 4)

        pygame.draw.rect(screen, color_active if buttons_box_active else color_inactive, update_graph_button, 2)
        screen.blit(update_graph_button_text, (update_graph_button.x+5, update_graph_button.y+22))

        pygame.draw.rect(screen, color_active if buttons_box_active else color_inactive, clear_graph_button, 2)
        screen.blit(clear_graph_button_text, (clear_graph_button.x+10, clear_graph_button.y+22))

        # Buttons and texts
        pygame.draw.rect(screen, color_active if alg_box_active else color_inactive, eulers_way_button, 2)
        screen.blit(eulers_way_button_text, (eulers_way_button.x+22, eulers_way_button.y+22))
        pygame.draw.rect(screen, color_active if alg_box_active else color_inactive, eulers_cycle_button, 2)
        screen.blit(eulers_cycle_button_text, (eulers_cycle_button.x+17, eulers_cycle_button.y+22))

        pygame.draw.rect(screen, color_active if alg_box_active else color_inactive, gamils_way_button, 2)
        screen.blit(gamils_way_button_text, (gamils_way_button.x+12, gamils_way_button.y+22))
        pygame.draw.rect(screen, color_active if alg_box_active else color_inactive, gamils_cycle_button, 2)
        screen.blit(gamils_cycle_button_text, (gamils_cycle_button.x+7, gamils_cycle_button.y+22))

        pygame.draw.rect(screen, color_active if graph_box_active else color_inactive, graph_box, 4)

    # Show algorithms
    if tick % 200 == 0:
        if show_eulers_way:
            eulers_way, alg_count, last_edge, show_eulers_way = show_way(eulers_way, G, alg_count, last_edge, show_eulers_way)
            algo_active = show_eulers_way
        elif show_eulers_cycle:
            eulers_cycle, alg_count, last_edge, show_eulers_cycle = show_way(eulers_cycle, G, alg_count, last_edge, show_eulers_cycle)
            algo_active = show_eulers_cycle
        elif show_gamils_cycle:
            gamils_cycle, alg_count, last_edge, show_gamils_cycle = show_way(gamils_cycle, G, alg_count, last_edge, show_gamils_cycle)
            algo_active = show_gamils_cycle
        elif show_gamils_way:
            gamils_way, alg_count, last_edge, show_gamils_way = show_way(gamils_way, G, alg_count, last_edge, show_gamils_way)
            algo_active = show_gamils_way


    if algo_active:
        screen.blit(chain, (graph_edges[0].x + graph_edges[1].x * 0.2, \
                            graph_edges[0].y + graph_edges[1].y * 0.9))

    # draw nodes and edges
    for es in edge_eqc:
        draw_edge(screen, es, 300, 20)
    for v in G.V:
        draw_node(screen, v.color, v.pos(), 30, name=v.name)

    # warnings
    if show_warning == 1:
        screen.blit(wrong_edges_input_warning, (graph_edges[0].x + graph_edges[1].x * 0.2, \
                                                graph_edges[0].y + graph_edges[1].y * 0.8))
    elif show_warning == 2:
        screen.blit(no_eulers_way_warning, (graph_edges[0].x + graph_edges[1].x * 0.2, \
                                                graph_edges[0].y + graph_edges[1].y * 0.8))
    elif show_warning == 3:
        screen.blit(no_eulers_cycle_warning, (graph_edges[0].x + graph_edges[1].x * 0.2, \
                                                graph_edges[0].y + graph_edges[1].y * 0.8))
    elif show_warning == 4:
        screen.blit(no_gamils_way_warning, (graph_edges[0].x + graph_edges[1].x * 0.08, \
                                                graph_edges[0].y + graph_edges[1].y * 0.8))
    elif show_warning == 5:
        screen.blit(no_gamils_cycle_warning, (graph_edges[0].x + graph_edges[1].x * 0.08, \
                                                graph_edges[0].y + graph_edges[1].y * 0.8))
    elif show_warning == 6:
        screen.blit(wait_warning, (graph_edges[0].x + graph_edges[1].x * 0.2, \
                                                graph_edges[0].y + graph_edges[1].y * 0.8))


    pygame.display.update()

    G.update_positions(dt)

    tick += 1
