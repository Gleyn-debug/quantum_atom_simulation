import asyncio
import pygame
import math
import random
import sys 

pygame.init()
OG_WIDTH = 1200
OG_HEIGHT = 1080
FPS = 60
POINTS = []
clock = pygame.time.Clock()
dragging = False
running = True
N = 1
L = 0
M = 0
PHASE = []

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
screen = pygame.display.set_mode((WIDTH,HEIGHT))

if sys.platform == "emscripten":
    platform.window.canvas.style.width ="100vw"
    platform.window.canvas.style.height="100vh"
    platform.window.canvas.style.display ="block"
SCALE_UI = min(WIDTH/OG_WIDTH , HEIGHT / OG_HEIGHT)
SCALE = 120 * SCALE_UI

def associated_laguere(order,alpha,ro):
    total = 0.0
    for i in range(order+ 1 ):
        coefficient = ((-1) **i) * math.comb(order+alpha, order - i)
        total += coefficient * ( ro ** i) / math.factorial(i)
    return total

def associated_legendre (l,m,x):
    p_mm = 1.0
    if m> 0:
        root = math.sqrt (max(0.0,1.0 - x **2))
        factor = 1.0
        for _ in range (m):
            p_mm  *= -factor  * root
            factor += 2.0

    if l ==m:
        return p_mm

    p_mlm =x * ( 2*m + 1) * p_mm
    if l == m + 1 :
        return p_mlm

    previous = p_mm
    current = p_mlm
    for degree in range(m+2,1+l):
        next_value = ((2*degree - 1) * x * current - ( degree + m - 1) * previous) / (degree - m)
        previous , current = current , next_value

    return current

def radial_wave(n,l,radius):
    ro =  2* radius / n
    order = n - l - 1
    alpha = 2 * l + 1
    value = math.exp(-ro/2) * (ro**l) * associated_laguere(order,alpha,ro)
    return value

def angular_wave(l,m,x,y,z):
    cosThetha = max(-1,min(1,z))
    phi = math.atan2(y,x)
    abs_n = abs(m)
    value = associated_legendre(l,abs_n, cosThetha)
    if m < 0:
        value = value*math.cos(abs_n*phi)
    elif m > 0:
        value = value*math.sin(abs_n*phi)
    return value

def angularMax (l,m):
    maximum = 0.0000001
    for i in range(61):
        thehta = math.pi * i / 60
        z = math.cos(thehta)
        for j in range ( 121 ):
            phi = math.pi * 2 * j / 120
            x  = math.sin(thehta) * math.cos(phi)
            y  = math.sin(thehta) * math.sin(phi)
            maximum = max(maximum, abs(angular_wave(l,m,x,y,z)))
    return maximum

def radialMax (n,l, maxradius):
    maximum = 0.000001
    samples = 2000
    for i in range (1 , samples + 1 ):
        radius = i * maxradius / samples
        value = radial_wave(n,l,radius)
        probability = value ** 2 * radius **2
        maximum = max(maximum , probability)

    return maximum

def sampleRadius (n,l, maxradius, radialMax):
    while True:
        radius = random.uniform(0.0, maxradius)
        radialValue = radial_wave ( n,l,radius)
        probabiltiy = radius ** 2 * radialValue **2
        if random.random() <= probabiltiy/ radialMax:
            return radius, radialValue

def sampleDirection(angularmax, m, l):
    while True:
        z = random.uniform(-1.0,1.0)
        phi = random.uniform(0.0, math.pi * 2)
        horizontal = math.sqrt(max(0.0,1.0 - z**2))
        x = horizontal * math.cos(phi)
        y = horizontal * math.sin(phi)
        anuglarvalue = angular_wave(l,m,x,y,z)
        probability = (anuglarvalue / angularmax) **2
        if random.random() <= probability:
            return x,y,z,anuglarvalue

def generateClouds(n,l,m):
    points = [ ]
    PHASE = []
    maxRadius = 4.5 * n **2
    maxRadial = radialMax ( n, l ,maxRadius)
    maxAngular = angularMax (l,m)
    while len(points) < 10000:
        radius , radialValue = sampleRadius(n,l,maxRadius , maxRadial)
        xi,yj,zk , angularValue = sampleDirection(maxAngular, m ,l )
        screenRadius = (radius /  ((n*n)) *( 0.78+0.08*n))
        x = screenRadius * xi
        y = screenRadius * yj
        z = screenRadius * zk
        wavefunction = radialValue * angularValue
        if wavefunction < 0:
            phase = -1
        elif wavefunction > 0:
            phase = 1
        else:
            phase = 1

        points.append((x,y,z))
        PHASE.append((phase,z))
    return points , PHASE
def axisPoint(x,y,z):

    rotatedY = y * math.cos(angleX) + z * math.sin(angleX)
    rotatedX = x
    rotatedZ = -y * math.sin(angleX) + z * math.cos(angleX)

    oldX = rotatedX
    oldZ = rotatedZ

    rotatedX = oldX * math.cos(angleY) - oldZ * math.sin(angleY)
    rotatedZ = oldX * math.sin(angleY) + oldZ * math.cos(angleY)

    perspective = cameraDistance / (cameraDistance + rotatedZ)

    projectedX = rotatedX * perspective
    projectedY = rotatedY * perspective

    screenX = WIDTH // 2 + int(projectedX * SCALE * zoom)
    screenY = HEIGHT // 2 - int(projectedY * SCALE * zoom)
    return screenX,screenY
def drawAxes():

    length =5

    pygame.draw.line(screen,"white",axisPoint(-length,0,0),axisPoint(length,0,0),2)
    pygame.draw.line(screen,"white",axisPoint(0,-length,0),axisPoint(0,length,0),2)
    pygame.draw.line(screen,"white",axisPoint(0,0,-length),axisPoint(0,0,length),2)
angleX = 0
angleY = 0
zoom = 1.0
font = pygame.font.SysFont(None,int(20 * SCALE_UI))

class Button:
    def __init__(self, x,y,width, height , text,value ):
        self.rect = pygame.Rect(x,y,width,height)
        self.text=  text
        self.value = value
    def draw(self,active = False):
        if active:
            color = (80,120,200)
        else:
            color = (80,60,70)
        pygame.draw.rect(screen,color , self.rect, border_radius= int(8 * SCALE_UI))
        pygame.draw.rect(screen,(180,180,190), self.rect,2, border_radius=int ( 8 * SCALE_UI))
        textSurface = font.render(self.text, True, (255,255,255))
        screen.blit(textSurface , textSurface.get_rect(center = self.rect.center))
    def clicked (self, mousePosition):
        return self.rect.collidepoint (mousePosition)

BUTTON_WIDTH = int(30 * SCALE_UI)
BUTTON_HEIGHT = int(30 * SCALE_UI)
BUTTON_GAP = int(5 * SCALE_UI)
subshellnames = {0:"s" , 1:"p" ,2: "d" , 3: "f" , 4:"g", 5: "h" ,6: "i", 7: "k" , 8: "l" , 9:"m"  }
nbuttons = []

for i in range ( 1, 11):
    button = Button(int(30*SCALE_UI),int(100 * SCALE_UI) + (i- 1) *(BUTTON_HEIGHT + BUTTON_GAP) , BUTTON_WIDTH,BUTTON_HEIGHT,f"n ={i}" , i)
    nbuttons.append(button)

def createbuttons_L (N):
    buttons = []
    for l in range(N):
        button = Button(int(SCALE_UI*70),int(SCALE_UI * 100) + l * (BUTTON_HEIGHT + BUTTON_GAP), BUTTON_WIDTH, BUTTON_HEIGHT,subshellnames[l],l)
        buttons.append(button)
    return buttons

def createbuttons_M (L):
    buttons = []
    for i , m in enumerate(range(-L,L +1)):
        button = Button(int(110*SCALE_UI),int(SCALE_UI*100) + i * (BUTTON_HEIGHT + BUTTON_GAP), BUTTON_WIDTH, BUTTON_HEIGHT,f"m={m}",m)
        buttons.append(button)
    return buttons

lbuttons = createbuttons_L(N)
mbuttons = createbuttons_M(L)
cameraDistance = 10
async def main():
    global running
    global dragging
    global N
    global L
    global M
    global POINTS
    global PHASE
    global angleX
    global angleY
    global lbuttons
    global mbuttons
    global zoom
    POINTS, PHASE = generateClouds(N,L,M)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mousePos = event.pos
                    buttonClicked = False

                    for button in nbuttons:
                        if button.clicked(mousePos):
                            N = button.value
                            L = 0
                            M = 0
                            lbuttons = createbuttons_L(N)
                            mbuttons = createbuttons_M(L)
                            POINTS , PHASE = generateClouds(N,L,M)
                            buttonClicked = True

                    for button in lbuttons:
                        if button.clicked(mousePos):
                            L = button.value
                            M = 0
                            mbuttons = createbuttons_M(L)
                            POINTS , PHASE = generateClouds(N,L,M)
                            buttonClicked = True

                    for button in mbuttons:
                        if button.clicked(mousePos):
                            M = button.value
                            POINTS , PHASE = generateClouds(N,L,M)
                            buttonClicked = True

                    if not buttonClicked:
                        dragging = True
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    zoom *= 1.1
                elif event.y < 0:
                    zoom /= 1.1
                zoom = max(0.4, min(2.5,zoom))

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False

            elif dragging and event.type == pygame.MOUSEMOTION:
                mouseX , mouseY = event.rel
                angleY += mouseX * 0.01
                angleX += mouseY * 0.01

        

        ZOOMED_SCALE = SCALE * zoom
        screen.fill("black")
        drawAxes()
        for (x,y,z), phasedata in zip(POINTS, PHASE):
            
            rotatedY = y * math.cos(angleX) + z * math.sin(angleX)
            rotatedX = x
            rotatedZ = -y* math.sin(angleX) + z * math.cos( angleX )
            oldX = rotatedX
            oldZ = rotatedZ
            rotatedX = oldX * math.cos(angleY) - oldZ * math.sin(angleY)
            rotatedZ = oldX * math.sin(angleY) + oldZ * math.cos(angleY)

            prespective = cameraDistance / ( cameraDistance + rotatedZ)
            projectedX = rotatedX * prespective
            projectedY = rotatedY * prespective
            
            projectedX , projectedY 
            screenX = WIDTH //2 + int(projectedX * ZOOMED_SCALE)
            screenY = HEIGHT // 2 - int(projectedY * ZOOMED_SCALE)

            brightness = int(max(80,min(255,160 + rotatedZ * (35))))

            if phasedata [0] == 1:
                COLOR = ( 238 , brightness , 238 )

            elif phasedata [0] == -1:
                COLOR = (203,brightness, 87)

            pygame.draw.circle(screen,COLOR , (screenX,screenY),max(1,int(2 * SCALE_UI)))
        pygame.draw.circle(screen , (255,255,255), (WIDTH //2 , HEIGHT //2 ), max(2,int( 6 * SCALE_UI)))

        for button in nbuttons:
            button.draw(button.value == N)

        for button in lbuttons:
            button.draw(button.value == L)

        for button in mbuttons:
            button.draw(button.value == M)

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)
    pygame.quit()

asyncio.run(main())
