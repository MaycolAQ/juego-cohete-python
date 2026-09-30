import pygame
import random
import math
import sys

pygame.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Cohete Espacial")
reloj = pygame.time.Clock()

NEGRO = (5, 5, 20)
BLANCO = (255, 255, 255)
ROJO = (230, 60, 60)
NARANJA = (255, 150, 50)
AMARILLO = (255, 230, 80)
VERDE = (80, 220, 120)
GRIS = (150, 150, 160)
CIAN = (100, 230, 255)
PURPURA = (180, 80, 220)
MARRON = (200, 100, 50)

estrellas = [[random.randint(0, ANCHO), random.randint(0, ALTO), random.uniform(0.5, 3)] for _ in range(80)]

class Cohete:
    def __init__(self):
        self.x = 100
        self.y = ALTO // 2
        self.vida = 3
        self.velocidad = 7
        self.enfriamiento = 0
        self.cd_disparo = 12
        self.contador_llama = 0
        self.invulnerable = 0

    def mover(self, dy):
        self.y = max(30, min(ALTO - 30, self.y + dy * self.velocidad))

    def ir_a(self, objetivo_y):
        diff = objetivo_y - self.y
        if abs(diff) > 5:
            self.y += max(-self.velocidad, min(self.velocidad, diff))
        self.y = max(30, min(ALTO - 30, self.y))

    def disparar(self, balas):
        if self.enfriamiento <= 0:
            balas.append(Bala(self.x + 22, self.y))
            self.enfriamiento = self.cd_disparo

    def actualizar(self):
        if self.enfriamiento > 0:
            self.enfriamiento -= 1
        if self.invulnerable > 0:
            self.invulnerable -= 1
        self.contador_llama = (self.contador_llama + 1) % 6

    def dibujar(self):
        if self.invulnerable > 0 and (self.invulnerable // 4) % 2 == 0:
            return
        x, y = int(self.x), int(self.y)
        tam = 10 + (self.contador_llama % 3) * 5
        pygame.draw.polygon(pantalla, NARANJA, [(x-16, y), (x-16-tam, y-7), (x-16-tam, y+7)])
        pygame.draw.polygon(pantalla, AMARILLO, [(x-16, y), (x-16-tam//2, y-4), (x-16-tam//2, y+4)])
        pygame.draw.polygon(pantalla, GRIS, [(x+22, y), (x-16, y-13), (x-16, y+13)])
        pygame.draw.polygon(pantalla, ROJO, [(x+22, y), (x+8, y-8), (x+8, y+8)])
        pygame.draw.circle(pantalla, CIAN, (x+2, y), 5)
        pygame.draw.circle(pantalla, BLANCO, (x+2, y), 5, 1)
        pygame.draw.polygon(pantalla, ROJO, [(x-12, y-11), (x-22, y-20), (x-16, y-6)])
        pygame.draw.polygon(pantalla, ROJO, [(x-12, y+11), (x-22, y+20), (x-16, y+6)])

    def get_rect(self):
        return pygame.Rect(int(self.x) - 12, int(self.y) - 13, 30, 26)


class Bala:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidad = 13
        self.radio = 4

    def mover(self):
        self.x += self.velocidad

    def dibujar(self):
        pygame.draw.circle(pantalla, (255, 255, 150), (int(self.x), int(self.y)), self.radio + 4)
        pygame.draw.circle(pantalla, AMARILLO, (int(self.x), int(self.y)), self.radio)

    def fuera(self):
        return self.x > ANCHO + 20


class BalaEnemiga:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidad = 5.5
        self.radio = 5

    def mover(self):
        self.x -= self.velocidad

    def dibujar(self):
        pygame.draw.circle(pantalla, (255, 80, 80), (int(self.x), int(self.y)), self.radio + 3)
        pygame.draw.circle(pantalla, (255, 200, 100), (int(self.x), int(self.y)), self.radio)

    def fuera(self):
        return self.x < -20


class NaveEnemiga:
    def __init__(self, nivel):
        self.x = ANCHO + 50
        self.tipo = random.choice(['basica', 'basica', 'basica', 'zigzag', 'tanque'])
        if self.tipo == 'basica':
            self.vida = 1
            self.velocidad = random.uniform(2.5, 4)
            self.radio = 18
            self.color = ROJO
        elif self.tipo == 'zigzag':
            self.vida = 2
            self.velocidad = random.uniform(2.5, 3.5)
            self.radio = 18
            self.color = PURPURA
        else:
            self.vida = 4
            self.velocidad = random.uniform(1.2, 2)
            self.radio = 26
            self.color = MARRON
        self.vida_max = self.vida
        self.velocidad += nivel * 0.15
        self.y = random.randint(60, ALTO - 60)
        self.base_y = self.y
        self.tiempo = 0
        self.disparo_cd = random.randint(80, 180)
        self.puede_disparar = self.tipo in ('zigzag', 'tanque')

    def mover(self):
        self.x -= self.velocidad
        self.tiempo += 1
        if self.tipo == 'zigzag':
            self.y = self.base_y + math.sin(self.tiempo * 0.08) * 70
            self.y = max(40, min(ALTO - 40, self.y))

    def actualizar(self, balas_enemigas):
        if self.puede_disparar and self.x < ANCHO - 80:
            self.disparo_cd -= 1
            if self.disparo_cd <= 0:
                balas_enemigas.append(BalaEnemiga(self.x - self.radio, self.y))
                self.disparo_cd = random.randint(100, 200)

    def dibujar(self):
        x, y = int(self.x), int(self.y)
        r = self.radio
        pygame.draw.polygon(pantalla, self.color, [
            (x - r, y), (x + r - 5, y - r*0.7), (x + r, y), (x + r - 5, y + r*0.7)
        ])
        pygame.draw.circle(pantalla, (255, 150, 150), (x + 3, y), r // 3)
        pygame.draw.circle(pantalla, BLANCO, (x + 3, y), r // 3, 1)
        if self.tipo == 'tanque':
            ancho_barra = r * 2
            pygame.draw.rect(pantalla, (60, 60, 60), (x - r, y - r - 12, ancho_barra, 6))
            pygame.draw.rect(pantalla, VERDE, (x - r, y - r - 12, ancho_barra * (self.vida/self.vida_max), 6))
            pygame.draw.rect(pantalla, BLANCO, (x - r, y - r - 12, ancho_barra, 6), 1)

    def get_rect(self):
        return pygame.Rect(int(self.x) - self.radio, int(self.y) - self.radio, self.radio*2, self.radio*2)

    def fuera(self):
        return self.x < -60


class Particula:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        ang = random.uniform(0, math.pi * 2)
        vel = random.uniform(1, 6)
        self.vx = math.cos(ang) * vel
        self.vy = math.sin(ang) * vel
        self.vida = random.randint(15, 40)
        self.vida_max = self.vida
        self.color = color
        self.tam = random.randint(2, 5)

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94
        self.vy *= 0.94
        self.vida -= 1

    def dibujar(self):
        alpha = self.vida / self.vida_max
        r = max(1, int(self.tam * alpha))
        pygame.draw.circle(pantalla, self.color, (int(self.x), int(self.y)), r)

    def viva(self):
        return self.vida > 0


particulas = []

def crear_explosion(x, y, color, cantidad=18):
    for _ in range(cantidad):
        particulas.append(Particula(x, y, color))


def reiniciar_juego():
    global cohete, balas, balas_enemigas, enemigos, particulas, puntuacion, nivel, frame, tiempo_spawn
    cohete = Cohete()
    balas = []
    balas_enemigas = []
    enemigos = []
    particulas = []
    puntuacion = 0
    nivel = 1
    frame = 0
    tiempo_spawn = 0


def dibujar_fondo():
    pantalla.fill(NEGRO)
    for estrella in estrellas:
        estrella[0] -= estrella[2] * 0.5
        if estrella[0] < 0:
            estrella[0] = ANCHO
            estrella[1] = random.randint(0, ALTO)
        brillo = int(150 + estrella[2] * 35)
        pygame.draw.circle(pantalla, (brillo, brillo, brillo), (int(estrella[0]), int(estrella[1])), max(1, int(estrella[2])))


cohete = Cohete()
balas = []
balas_enemigas = []
enemigos = []
puntuacion = 0
nivel = 1
frame = 0
tiempo_spawn = 0
estado = "menu"

fuente = pygame.font.Font(None, 30)
fuente_media = pygame.font.Font(None, 44)
fuente_grande = pygame.font.Font(None, 70)

touch_y = None
touch_activo = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                if estado in ("menu", "gameover"):
                    reiniciar_juego()
                    estado = "jugando"

        if event.type == pygame.MOUSEBUTTONDOWN:
            if estado in ("menu", "gameover"):
                reiniciar_juego()
                estado = "jugando"
            touch_activo = True
            touch_y = event.pos[1]

        if event.type == pygame.MOUSEBUTTONUP:
            touch_activo = False
            touch_y = None

        if event.type == pygame.MOUSEMOTION and touch_activo:
            touch_y = event.pos[1]

        if event.type == pygame.FINGERDOWN:
            if estado in ("menu", "gameover"):
                reiniciar_juego()
                estado = "jugando"
            touch_activo = True
            touch_y = event.y * ALTO

        if event.type == pygame.FINGERMOTION:
            touch_y = event.y * ALTO

        if event.type == pygame.FINGERUP:
            touch_activo = False
            touch_y = None

    if estado == "jugando":
        frame += 1
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            cohete.mover(-1)
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            cohete.mover(1)

        if touch_activo and touch_y is not None:
            cohete.ir_a(touch_y)

        cohete.actualizar()
        cohete.disparar(balas)

        for bala in balas[:]:
            bala.mover()
            if bala.fuera():
                balas.remove(bala)

        for bala in balas_enemigas[:]:
            bala.mover()
            if bala.fuera():
                balas_enemigas.remove(bala)

        tiempo_spawn += 1
        intervalo = max(25, 70 - nivel * 4)
        if tiempo_spawn >= intervalo:
            enemigos.append(NaveEnemiga(nivel))
            tiempo_spawn = 0

        for enemigo in enemigos[:]:
            enemigo.mover()
            enemigo.actualizar(balas_enemigas)
            if enemigo.fuera():
                enemigos.remove(enemigo)

        for bala in balas[:]:
            rect_bala = pygame.Rect(int(bala.x) - bala.radio, int(bala.y) - bala.radio, bala.radio*2, bala.radio*2)
            for enemigo in enemigos[:]:
                if rect_bala.colliderect(enemigo.get_rect()):
                    if bala in balas:
                        balas.remove(bala)
                    enemigo.vida -= 1
                    crear_explosion(bala.x, bala.y, AMARILLO, 6)
                    if enemigo.vida <= 0:
                        crear_explosion(enemigo.x, enemigo.y, enemigo.color, 20)
                        if enemigo in enemigos:
                            enemigos.remove(enemigo)
                        if enemigo.tipo == 'basica':
                            puntuacion += 10
                        elif enemigo.tipo == 'zigzag':
                            puntuacion += 20
                        else:
                            puntuacion += 30
                    break

        rect_cohete = cohete.get_rect()
        for enemigo in enemigos[:]:
            if rect_cohete.colliderect(enemigo.get_rect()):
                if cohete.invulnerable <= 0:
                    cohete.vida -= 1
                    cohete.invulnerable = 90
                    crear_explosion(cohete.x, cohete.y, NARANJA, 15)
                    if cohete.vida <= 0:
                        crear_explosion(cohete.x, cohete.y, ROJO, 40)
                        estado = "gameover"
                if enemigo in enemigos:
                    enemigos.remove(enemigo)
                crear_explosion(enemigo.x, enemigo.y, enemigo.color, 15)

        for bala in balas_enemigas[:]:
            rect_bala = pygame.Rect(int(bala.x) - bala.radio, int(bala.y) - bala.radio, bala.radio*2, bala.radio*2)
            if rect_bala.colliderect(rect_cohete) and cohete.invulnerable <= 0:
                cohete.vida -= 1
                cohete.invulnerable = 90
                crear_explosion(bala.x, bala.y, NARANJA, 10)
                if bala in balas_enemigas:
                    balas_enemigas.remove(bala)
                if cohete.vida <= 0:
                    crear_explosion(cohete.x, cohete.y, ROJO, 40)
                    estado = "gameover"

        nivel = 1 + puntuacion // 100

        for p in particulas[:]:
            p.actualizar()
            if not p.viva():
                particulas.remove(p)

    dibujar_fondo()

    if estado == "menu":
        titulo = fuente_grande.render("COHETE ESPACIAL", True, CIAN)
        pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, ALTO//2 - 100))
        sub = fuente_media.render("Vence a las naves desconocidas", True, BLANCO)
        pantalla.blit(sub, (ANCHO//2 - sub.get_width()//2, ALTO//2 - 30))
        instrucciones = [
            "Arrastra el dedo para mover el cohete",
            "El cohete dispara automaticamente",
            "Esquiva las balas enemigas",
            "",
            "TOCA LA PANTALLA PARA EMPEZAR"
        ]
        for i, linea in enumerate(instrucciones):
            color = AMARILLO if "TOCA" in linea else BLANCO
            txt = fuente.render(linea, True, color)
            pantalla.blit(txt, (ANCHO//2 - txt.get_width()//2, ALTO//2 + 40 + i * 32))

    elif estado == "jugando":
        for bala in balas:
            bala.dibujar()
        for bala in balas_enemigas:
            bala.dibujar()
        for enemigo in enemigos:
            enemigo.dibujar()
        for p in particulas:
            p.dibujar()
        cohete.dibujar()

        txt_puntos = fuente.render(f"Puntos: {puntuacion}", True, BLANCO)
        txt_nivel = fuente.render(f"Nivel: {nivel}", True, CIAN)
        pantalla.blit(txt_puntos, (15, 15))
        pantalla.blit(txt_nivel, (15, 50))

        for i in range(cohete.vida):
            pygame.draw.polygon(pantalla, ROJO, [
                (ANCHO - 40 - i * 35, 25),
                (ANCHO - 50 - i * 35, 40),
                (ANCHO - 30 - i * 35, 40)
            ])

    elif estado == "gameover":
        for bala in balas:
            bala.dibujar()
        for enemigo in enemigos:
            enemigo.dibujar()
        for p in particulas:
            p.dibujar()

        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        pantalla.blit(overlay, (0, 0))

        txt_go = fuente_grande.render("GAME OVER", True, ROJO)
        pantalla.blit(txt_go, (ANCHO//2 - txt_go.get_width()//2, ALTO//2 - 100))
        txt_pts = fuente_media.render(f"Puntuacion: {puntuacion}", True, AMARILLO)
        pantalla.blit(txt_pts, (ANCHO//2 - txt_pts.get_width()//2, ALTO//2 - 20))
        txt_niv = fuente_media.render(f"Nivel alcanzado: {nivel}", True, CIAN)
        pantalla.blit(txt_niv, (ANCHO//2 - txt_niv.get_width()//2, ALTO//2 + 30))
        txt_reinicio = fuente.render("Toca la pantalla para reiniciar", True, BLANCO)
        pantalla.blit(txt_reinicio, (ANCHO//2 - txt_reinicio.get_width()//2, ALTO//2 + 110))

    pygame.display.flip()
    reloj.tick(60)