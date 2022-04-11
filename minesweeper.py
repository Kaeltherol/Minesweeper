#import libraries
from ctypes.wintypes import SIZE
import pygame
import random
import queue
import time

pygame.init()
WIDTH, HEIGHT = 700, 800
win = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("BOMBSweeper")
#global variables


BG_COLOR = "white"
ROWS, COLS = 10,10
BOMBS = 10

NUM_FONT = pygame.font.SysFont('comicsans',20)
NUM_COLORS = {
    1: "black",
    2: "green",
    3: "red",
    4: "orange",
    5: "yellow",
    6: "purple",
    7: "blue",
    8: "pink"
}
RECT_COLOR = (200,200,200)
CLICKED_RECT_COLOR = (140,140,140)
FLAG_RECT_COLOR = (0,255,0)
BOMB_RECT_COLOR = (0,0,0)
SIZE = WIDTH//ROWS
LOST_FONT = pygame.font.SysFont('comicsans',100)
TIME_FONT = pygame.font.SysFont('comicsans',30)
FLAG_FONT = pygame.font.SysFont('comicsans',30)
BOMB_FONT = pygame.font.SysFont('comicsans',30)

POP_UP_WIDTH = WIDTH*2/3
POP_UP_HEIGHT = HEIGHT*1/5
POP_UP_COLOR = (140,140,140)
POP_UP_FONT = pygame.font.SysFont('comicsans',30)

#functions

#draw game window
def draw(win,field, cover_field,current_time, flags):
    win.fill(BG_COLOR)

    time_text = TIME_FONT.render(f"Time Elapsed: {round(current_time)}",1,'black')
    win.blit(time_text, (10, HEIGHT-time_text.get_height()))

    flag_text = FLAG_FONT.render(f"Flag Left: {flags}",1,"black")
    win.blit(flag_text, (10, HEIGHT - 2*flag_text.get_height()))

    bomb_text = BOMB_FONT.render(f"Bombs: {BOMBS}",1,'black')
    win.blit(bomb_text, (WIDTH-10-bomb_text.get_width(),HEIGHT - 2*bomb_text.get_height()))

    for i, row in enumerate(field):
        y = SIZE*i
        for j, value in enumerate(row):
            x = SIZE*j

            is_covered = cover_field[i][j] == 0
            is_flag = cover_field[i][j] == -2
            is_bomb = value == -1

            if is_flag:
                pygame.draw.rect(win, FLAG_RECT_COLOR, (x,y,SIZE, SIZE))
                pygame.draw.rect(win, "black", (x,y,SIZE,SIZE),2)
                continue


            if is_covered:
                pygame.draw.rect(win, RECT_COLOR, (x,y,SIZE, SIZE))
                pygame.draw.rect(win, "black", (x,y,SIZE,SIZE),2)
                continue
            else:
                pygame.draw.rect(win, CLICKED_RECT_COLOR, (x,y,SIZE, SIZE))
                pygame.draw.rect(win, "black", (x,y,SIZE,SIZE),2)
                if is_bomb:
                    pygame.draw.circle(win,BOMB_RECT_COLOR,(x+SIZE/2,y+SIZE/2),1)
            

            if value > 0:
                text = NUM_FONT.render(str(value),1,NUM_COLORS[value])
                win.blit(text, (x+(SIZE/2-text.get_width()/2),y+(SIZE/2-text.get_height()/2)))
    pygame.display.update()

def get_neighbors(row, col, rows, cols):
    neighbors=[]

    if row > 0:
        neighbors.append((row-1,col)) #UP

    if row < rows-1:
        neighbors.append((row+1,col)) #DOWN

    if col > 0:
        neighbors.append((row, col-1)) #LEFT

    if col < cols-1:
        neighbors.append((row, col+1)) #RIGHT

    if (row >0) & (col>0):
        neighbors.append((row-1,col-1)) #UPLEFT

    if (row>0) & (col < cols-1):
        neighbors.append((row-1,col+1)) #UPRIGHT

    if (row<rows-1) & (col>0):
        neighbors.append((row+1,col-1)) #DOWNLEFT

    if (row<rows-1) & (col<cols-1):
        neighbors.append((row+1,col+1)) #DOWNRIGHT

    return neighbors

def create_mine_field(rows, cols,BOMBS):
    field = [[0 for _ in range(cols)] for _ in range(rows)]
    mine_positions = set()

    while len(mine_positions) < BOMBS:
        row = random.randrange(0, rows)
        col = random.randrange(0, cols)
        pos = row, col

        if pos in mine_positions:
            continue
        
        
        mine_positions.add(pos)
        field[row][col] = -1

    for mine in mine_positions:
        neighbors = get_neighbors(*mine, rows, cols)
        for r, c in neighbors:
            if (r,c) in mine_positions:
                continue
            field[r][c]+=1
    
    return field, mine_positions


def get_grid_pos(mouse_pos):
    mx, my = mouse_pos
    row = int(my//SIZE)
    col = int(mx//SIZE)
    return row, col

def uncover_from_pos(row, col, cover_field, field,flagged,mine_positions):
    q = queue.Queue()
    q.put((row, col))
    visited = set()

    while not q.empty():
        current = q.get()

        neighbors = get_neighbors(*current, ROWS, COLS)
        for r,c in neighbors:
            if ((r,c) in visited)|((r,c) in flagged)|((r,c) in mine_positions):
                continue

            value = field[r][c]
            cover_field[r][c] = 1
            if value == 0:
                q.put((r,c))
            visited.add((r,c))

def draw_lost(win,text):
    text = LOST_FONT.render(text,1,"red")
    win.blit(text,(WIDTH/2-text.get_width()/2,HEIGHT/2-text.get_height()/2))
    pygame.display.update()


def draw_win(win,text):
    text = LOST_FONT.render(text,1,"green")
    win.blit(text,(WIDTH/2-text.get_width()/2,HEIGHT/2-text.get_height()/2))
    pygame.display.update()

def discover_bombs(win,field):

    for i, row in enumerate(field):
        y = SIZE*i
        for j, value in enumerate(row):
            x = SIZE*j

            is_bomb = value == -1
            if is_bomb:
                pygame.draw.circle(win,BOMB_RECT_COLOR,(x+SIZE/2,y+SIZE/2),SIZE/2-4)

def bomb_count(flagged,mine_positions):
    bomb_discovered = 0
    for pos in mine_positions:
        if pos in flagged:
            bomb_discovered +=1
    return bomb_discovered

def game_over():
    loop = True
    pygame.draw.rect(win, POP_UP_COLOR, (WIDTH/2-POP_UP_WIDTH/2,HEIGHT/2-POP_UP_HEIGHT/2,POP_UP_WIDTH, POP_UP_HEIGHT))
    pygame.draw.rect(win, 'black', (WIDTH/2-POP_UP_WIDTH/2,HEIGHT/2-POP_UP_HEIGHT/2,POP_UP_WIDTH, POP_UP_HEIGHT),2)

    pygame.draw.rect(win, POP_UP_COLOR, (WIDTH/2-POP_UP_WIDTH/2+POP_UP_WIDTH/8,HEIGHT/2-POP_UP_HEIGHT/2+POP_UP_HEIGHT/3,POP_UP_WIDTH/3, POP_UP_HEIGHT/3))
    pygame.draw.rect(win, 'black', (WIDTH/2-POP_UP_WIDTH/2+POP_UP_WIDTH/8,HEIGHT/2-POP_UP_HEIGHT/2+POP_UP_HEIGHT/3,POP_UP_WIDTH/3, POP_UP_HEIGHT/3),2)

    pygame.draw.rect(win, POP_UP_COLOR, (WIDTH/2+POP_UP_WIDTH/2-POP_UP_WIDTH*1/8-POP_UP_WIDTH/3,HEIGHT/2-POP_UP_HEIGHT/2+POP_UP_HEIGHT/3,POP_UP_WIDTH/3, POP_UP_HEIGHT/3))
    pygame.draw.rect(win, 'black', (WIDTH/2+POP_UP_WIDTH/2-POP_UP_WIDTH*1/8-POP_UP_WIDTH/3,HEIGHT/2-POP_UP_HEIGHT/2+POP_UP_HEIGHT/3,POP_UP_WIDTH/3, POP_UP_HEIGHT/3),2)
    again_text = POP_UP_FONT.render('Play again',1,'black')
    win.blit(again_text,(WIDTH/2-POP_UP_WIDTH/2+POP_UP_WIDTH/8+POP_UP_WIDTH/6-again_text.get_width()/2,HEIGHT/2-POP_UP_HEIGHT/2+POP_UP_HEIGHT/3))
    quit_text = POP_UP_FONT.render('Quit',1,'black')
    win.blit(quit_text,(WIDTH/2+POP_UP_WIDTH/2-POP_UP_WIDTH*1/8-POP_UP_WIDTH/6-quit_text.get_width()/2,HEIGHT/2-POP_UP_HEIGHT/2+POP_UP_HEIGHT/3))
    pygame.display.update()
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                loop = False
        pygame.display.update


def main():
    run = True
    field,mine_positions = create_mine_field(ROWS, COLS, BOMBS)
    flags = BOMBS
    bomb_discovered = 0
    cover_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    flagged = set()

    start_time = time.time()

    while run:
        current_time = time.time()-start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed = pygame.mouse.get_pressed()
                row, col = get_grid_pos(pygame.mouse.get_pos())

                if row >= ROWS or col >= COLS:
                    continue

                if mouse_pressed[0] and cover_field[row][col]!=-2:
                    cover_field[row][col] = 1

                    if field[row][col] == -1:

                        draw(win,field,cover_field,current_time,flags)
                        discover_bombs(win,field)
                        draw_lost(win,"YOU DIED")
                        pygame.time.delay(1000)
                        game_over()
                        run = False

                    elif field[row][col] == 0:
                        uncover_from_pos(row, col, cover_field,field,flagged, mine_positions)
                    
                elif mouse_pressed[2]: 
                    if cover_field[row][col] ==-2:
                        cover_field[row][col] = 0
                        flags +=1
                        flagged.discard((row,col))

                    else:
                        if flags < 1:
                            continue
                        flags -= 1
                        cover_field[row][col] = -2
                        flagged.add((row,col))
                        bomb_discovered = bomb_count(flagged,mine_positions)
                        if bomb_discovered == BOMBS:
                            draw(win,field,cover_field,current_time,flags)
                            discover_bombs(win,field)
                            draw_win(win,'YOU WIN')
                            pygame.time.delay(2000)
                            game_over()
                            run = False

        draw(win, field, cover_field,current_time, flags)
        create_mine_field(ROWS, COLS,BOMBS)

    pygame.quit()



if __name__=="__main__":
    main()