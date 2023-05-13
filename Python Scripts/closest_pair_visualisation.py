from closest_pair_parallel import closest_pair_wrapper, parr_closest_pair_wrapper, generatePoints
import multiprocessing
import pygame

def convert_coords(p):
    x = int(2.5*(p[0] + 100)) + 50
    y = int(2.5*(p[1] + 100)) + 50
    # print(x,y)
    return (x, y)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    points = generatePoints(25)
    
    #find closest pair of both sequential algorithm and parallel
    a = closest_pair_wrapper(points)[:2]
    b = parr_closest_pair_wrapper(points)[:2]

    p1, p2 = sorted(a) 
    parr1, parr2 = sorted(b)


    pygame.init()
    screen = pygame.display.set_mode((600, 600))

    screen.fill((16*4 + 3, 16*4 + 4, 16*4 + 5)) #434445 - background colour
    running = True

    #color for 3 types of points - selected in sequential, selected in parallel, selected by both
    c1 = (16*4 + 3, 16*10 + 13, 16*14 + 2) #43ADE2
    c2 = (16*14 + 2, 16*8 + 11, 16*4 + 3) #E28B43
    c3 = tuple([(c1[i] + c2[i])//2 for i in range(3)]) #avg of previous 2 colours
    print(c3)

    #lines for 3 types of pairs - selected in sequential, selected in parallel, selected in both
    l1 = (16*6 + 4, 16*11 + 9, 16*13 + 4) #64B9E4
    l2 = (16*14 + 2, 16*9 + 12, 16*6 + 1) #E29C61
    l3 = tuple([(l1[i] + l2[i])//2 for i in range(3)]) #avg of previous 2 colours

    for point in points:
        pygame.draw.circle(screen, (16*13 + 3, 16*2 + 9, 16*2 + 9),convert_coords(point), 6) #D32929 - default point colour

    #point colour for closest pair points
    if p1 != parr1:
        pygame.draw.circle(screen, c1,convert_coords(p1), 6) 
        pygame.draw.circle(screen, c2,convert_coords(parr1), 6) 
    else:
        pygame.draw.circle(screen, c3,convert_coords(p1), 6) 

    if p2 != parr2:
        pygame.draw.circle(screen, c1,convert_coords(p2), 6) 
        pygame.draw.circle(screen, c2,convert_coords(parr2), 6) 
    else:
        pygame.draw.circle(screen, c3,convert_coords(p2), 6) 

    #line colour for closest pair points
    if p1 != parr1 or p2 != parr2:
        pygame.draw.line(screen, l1, convert_coords(p1), convert_coords(p2), width=2) 
        pygame.draw.line(screen, l2, convert_coords(parr1), convert_coords(parr2), width=2) 
    else:
        pygame.draw.line(screen, l3, convert_coords(p1), convert_coords(p2), width=2)


    #show screen until user quits
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pygame.display.flip()

    pygame.quit()
