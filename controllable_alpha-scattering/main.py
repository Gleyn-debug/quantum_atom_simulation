import pygame
import math
import asyncio
import sys

pygame.init()

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

SCALE_UI = min(WIDTH/OG_WIDTH , HEIGHT/OG_HEIGHT)

electronCharge = 1.60e-19
k = 8.99e9

alphaCharge = 2*electronCharge
goldCharge = 79*electronCharge
massAlphaParticle = 6.64e-27

centerX = WIDTH/2
centerY = HEIGHT/2

xAlpha = -6.0e-13
yAlpha = 5.0e-14
xGold = 0.0
yGold = 0.0
r = 0

accelerationX = 0
accelerationY = 0
acceleration = 0

velocityX = 1.5e7
velocityY = 0

scale = 6.0e14*SCALE_UI

screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

if sys.platform == "emscripten":
    platform.window.canvas.style.width = "100vw"
    platform.window.canvas.style.height = "100vh"
    platform.window.canvas.style.display = "block"

async def main():
    global xAlpha
    global yAlpha
    global velocityX
    global velocityY

    run = True
    trail = []
    simulationStart = False

    while run:
        dt = clock.tick(60)/1e22

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    simulationStart = False
                    xAlpha = -6.0e-13
                    yAlpha = 5.0e-14
                    velocityX = 1.5e7
                    velocityY = 0
                    trail = []

                if event.key == pygame.K_RIGHT:
                    simulationStart = True
                    trail = []

            if event.type == pygame.MOUSEWHEEL:
                if event.y < 0:
                    yAlpha -= 1.0e-14
                    trail = []

                if event.y > 0:
                    yAlpha += 1.0e-14
                    trail = []

        if simulationStart:
            r = math.sqrt((xAlpha-xGold)**2 + (yAlpha-yGold)**2)
            force = k*goldCharge*alphaCharge/r**2
            acceleration = force/massAlphaParticle
            accelerationX = acceleration*((xAlpha-xGold)/r)
            accelerationY = acceleration*((yAlpha-yGold)/r)

            velocityY = accelerationY*dt + velocityY
            velocityX = accelerationX*dt + velocityX

            xAlpha += velocityX*dt
            yAlpha += velocityY*dt

        screen.fill((39,30,30))

        pygame.draw.circle(screen,(255,0,0),(int(centerX),int(centerY)),max(5,int(20*SCALE_UI)))

        gameX = int(centerX + xAlpha*scale)
        gameY = int(centerY - yAlpha*scale)

        trail.append((gameX,gameY))

        if len(trail) > 20:
            trail.pop(0)

        if len(trail) > 1:
            pygame.draw.lines(screen,(224,84,84),False,trail,max(1,int(SCALE_UI)))

        pygame.draw.circle(screen,(255,255,255),(gameX,gameY),max(2,int(4*SCALE_UI)))

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
