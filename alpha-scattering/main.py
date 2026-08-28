import asyncio
import pygame 
import math 
import random 
import sys
pygame.init()
e = 1.6e-19
massAlpha = 4 * 1.67e-27
chargeGold = 79 * e
chargeAlpha = 2 * e 
clock = pygame.time.Clock()
OG_WIDTH = 1980
OG_HEIGHT = 1200
if sys.platform == "emscripten":
    import platform
    WIDTH = int(platform.window.innerWidth)
    HEIGHT = int(platform.window.innerHeight)
    platform.window.document.body.style.margin = "0"
    platform.window.document.body.style.padding = "0"
    platform.window.document.body.style.overflow = "hidden"
    platform.window.document.body.style.background = "black"
else:
    WIDTH = OG_WIDTH
    HEIGHT = OG_HEIGHT
xGold = 0.0
yGOld = 0.0
running = True
screen = pygame.display.set_mode((WIDTH,HEIGHT))
if sys.platform == "emscripten":
    platform.window.canvas.style.width ="100vw"
    platform.window.canvas.style.height="100vh"
    platform.window.canvas.style.display ="block"
SCALE_UI = min(WIDTH/OG_WIDTH , HEIGHT / OG_HEIGHT)
SCALE = 8.0e15 * SCALE_UI
k = 8.99e9
initalPartilces_Position = []
positions_alpha = []
trail = []
numberOfparticles = 20
resetButton = pygame.Rect(WIDTH//2 + int(40*SCALE_UI),HEIGHT//2 - int(30*SCALE_UI),int(150*SCALE_UI),int(60*SCALE_UI))
font = pygame.font.Font(None,max(15,int(40*SCALE_UI)))
def generateAlphaParticles():
    for i in range (numberOfparticles):
        alphaY = random.uniform(-5e-14,5e-14) 
        alphaXo = -1e-13
        initalVelocity_alpha = random.randrange(int(1.5e7),int(2.1e7),int(1e5))
        initalPartilces_Position.append((alphaXo, alphaY, initalVelocity_alpha , 0)) #x,y,vx,vy
        trail.append([])
def particlePosition(alphaXinitial, alphaYinital, vX , vY , time  ):
    changeinX = alphaXinitial - xGold
    changeinY = alphaYinital - yGOld
    r =math.sqrt((changeinX) ** 2 + (changeinY) ** 2)
    if r < 1e-16:
        r = 1e-16
    force = chargeAlpha * chargeGold * k/ r**2
    acceleration = force / massAlpha
    beta = math.atan2(changeinY , changeinX)
    acc_X = math.cos(beta) * acceleration
    acc_y = math.sin(beta) * acceleration
    velocity_Y = (acc_y * time) + vY
    velocity_X = (acc_X* time) + vX
    x = alphaXinitial + velocity_X*time
    y = alphaYinital + velocity_Y*time
    return x,y,velocity_X,velocity_Y
    

generateAlphaParticles()
async def main():
    global running
    while running:
        clock.tick(60)
        dt = 1e-22
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    generateAlphaParticles()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resetButton.collidepoint(event.pos):
                    generateAlphaParticles()
        screen.fill((39,30,30))
        for i, (alpha_x_0, alpha_y_0, velocity_x, velocity_y) in enumerate(initalPartilces_Position):
            x,y,vx,vy= particlePosition (alpha_x_0, alpha_y_0, velocity_x, velocity_y,dt)
            initalPartilces_Position[i] = (x, y, vx, vy)
        for i,(x,y,_,_) in enumerate(initalPartilces_Position):
            screenX = WIDTH//2 + x*SCALE
            screenY = HEIGHT//2 - y*SCALE
            pygame.draw.circle(screen, (255,255,255) , (int(screenX),int(screenY)) ,max(2,int(4*SCALE_UI)))
            trail[i].append((screenX,screenY))
            if len(trail[i]) > 20:
                trail[i].pop(0)
            if len( trail [i]) > 1:
                pygame.draw.lines(screen, ( 224 , 84, 84 ) , False , trail[i] , max(1,int(1*SCALE_UI)) )
        pygame.draw.circle(screen,(255,215,0),(WIDTH//2,HEIGHT//2),max(5,int(10*SCALE_UI)))

        pygame.draw.rect(screen,(100,100,100),resetButton)
        resetText = font.render("RESET",True,(255,255,255))
        screen.blit(resetText,resetText.get_rect(center=resetButton.center))

        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()

asyncio.run(main())
