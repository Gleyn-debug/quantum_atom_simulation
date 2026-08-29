import asyncio
import pygame  
import math  
import random 
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

Clock = pygame.time.Clock() 
run = True 
screen = pygame.display.set_mode((WIDTH,HEIGHT)) 

if sys.platform == "emscripten":
    platform.window.canvas.style.width ="100vw"
    platform.window.canvas.style.height="100vh"
    platform.window.canvas.style.display ="block"

SCALE_UI = min(WIDTH/OG_WIDTH , HEIGHT / OG_HEIGHT)
 
amplitude = 20 * SCALE_UI
freqeucny = 0.1
initialX_wave = 0
initalY_wave = 0
waveHorizontalSpeed = 500 * SCALE_UI
phaseSpeed = 5
time = 0  
wave = [ ] 
phase = 0  
numberofwaves = 12  
beta = math.pi*2 / numberofwaves 
hR = 6.63e-34 / ( 2  * math.pi ) 
e = 1.6e-19 
m = 9.11e-31 
k = 8.99e9 
Z = 1 
N = 1 
thehta = 0  
atomRadius =  0 
angularvelocity = 0 
scale = 1e12 * SCALE_UI
atoms = [] 
waves = [] 
 
def getRadius(N): 
    r = (N**2 * hR **2) / ( m * Z * k * e ** 2) 
    v = (N * hR) / ( m * r) 
    w = v/r 
    r = r* scale     
    return r , w  
 
def drawAtom (time,aThehta, centerX , centery): 
    aThehta += angularvelocity * time * 1e-16 
    x = math.cos(aThehta) * atomRadius 
    y = math.sin(aThehta) * atomRadius 
    gameX = int(centerX + x ) 
    gameY = int (centery + y) 
    pygame.draw.circle(screen,(120,120,120) , (int(centerX) , int(centery)),int(atomRadius), max(1,int(2*SCALE_UI))) 
    pygame.draw.circle(screen,(255,215,0) , (int(centerX) , int(centery) ), max(5,int(20*SCALE_UI))) 
    pygame.draw.circle(screen,(255,80,80) , (gameX , gameY), max(3,int(8*SCALE_UI))) 
    return aThehta 
 
def intereaction(atomX , atomY , radius , wavestartX , waveendX ,wavey): 
    if atomX < wavestartX: 
        closestX = wavestartX 
    elif atomX > waveendX: 
        closestX = waveendX 
    else: 
        closestX = atomX 
     
    closestY = wavey 
    dx = closestX - atomX 
    dy = closestY - atomY 
    distance = math.sqrt(dx**2 + dy**2) 
    if distance <= radius: 
        return True 
    else: 
        return False 
 
def drawwaves(xO,yO,time,dHit): 
    if dHit: 
        for j in range(numberofwaves): 
            points =  [ ] 
            alpha = j * beta 
            for i in range ( 300 ): 
                x = i*SCALE_UI + ( waveHorizontalSpeed * time) 
                y = (amplitude * math.sin((freqeucny * i )) - (phaseSpeed * time)) 
                rotatedX = xO + x*math.cos(alpha) - y *math.sin(alpha) 
                rotatedY = yO + y*math.cos(alpha) + x *math.sin(alpha) 
                points.append((rotatedX, rotatedY)) 
            pygame.draw.lines(screen, (255,255,120), False , points , max(1,int(3*SCALE_UI)) ) 
    else: 
        points = [] 
        for j in range ( 300 ): 
            x = j*SCALE_UI + ( waveHorizontalSpeed * time) + xO 
            y = (amplitude * math.sin((freqeucny *  j)) - (phaseSpeed * time)) + yO 
            points.append((x, y)) 
        pygame.draw.lines(screen, (255,255,120), False , points , max(1,int(3*SCALE_UI)) ) 
 
 
async def main():
    global run
    global atomRadius
    global angularvelocity

    while run: 
        dt = Clock.tick(60) / 1000 
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                run = False 
            if event.type == pygame.MOUSEBUTTONDOWN: 
                if event.button == 1: 
                    atomX , atomY = event.pos 
                    atoms.append({"x": atomX , "y" : atomY ,"time" : 0 ,"thetha" : 0 , "radius" : 0 , "N" : N , "delayTime" : 0, "excited" : False}) 
                if event.button == 3: 
                    initalWaveX , initalWaveY = event.pos 
                    waves.append({"x" : initalWaveX , "y" : initalWaveY , "time" : 0 , "absorbed" :  False}) 
                
        screen.fill((30,30,30)) 
        for atom in atoms[:]: 
            if atom["excited"] : 
                atom["delayTime"] += dt 
                if atom["delayTime"] >=  atom["emissionDelay"]: 
                    atom["N"] = 1  
                    atom["delayTime"] = 0 
                    atom ["excited"] = False 
                    waves.append({"x" : atom["x"] , "y" : atom["y"] , "time" : 0 , "absorbed" :  True}) 
            atomRadius, angularvelocity = getRadius(atom["N"]) 
            atom["radius"] = atomRadius 
            atom["time"] += dt 
            atom["thetha"] += angularvelocity * dt * 1e-16 
            drawAtom(atom["time"], atom ["thetha"] ,atom["x"] , atom["y"]) 
        for wave in waves[:]: 
            wave["time"] += dt 
            waveStartX = wave ["x"] + waveHorizontalSpeed * wave["time"] 
            waveEndX = waveStartX + 300*SCALE_UI
            absorbed = False 
            hit = False 
            if not wave["absorbed"]: 
                for atom in atoms[:]: 
                    hit = intereaction (atom["x"] , atom["y"], atom["radius"], waveStartX , waveEndX , wave["y"]) 
                    if hit: 
                        if atom["N"] < 4: 
                            atom["N"] += 1  
                        atom["delayTime"] = 0  
                        atom["emissionDelay"] = random.expovariate(1/3) 
                        atom ["excited"] = True 
                        waves.remove(wave) 
                        absorbed = True 
                        break 
            if not absorbed: 
                drawwaves(wave["x"] , wave["y"] , wave["time"] ,wave["absorbed"]) 
        pygame.display.flip() 

        await asyncio.sleep(0)
 
    pygame.quit() 
 
asyncio.run(main())
