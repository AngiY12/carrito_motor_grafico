import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import math
import os
import random
# ------------------------- CLASES PARA OBJETOS 3D -------------------------
class Textura:
    def __init__(self, ruta):
        self.id = self.cargar_textura(ruta)
        self.ruta = ruta
    
    def cargar_textura(self, ruta):
        """Carga una textura desde un archivo de imagen"""
        try:
            textura_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, textura_id)
            
            img = Image.open(ruta).convert('RGB')
            # Voltear la imagen verticalmente (OpenGL usa coordenadas Y invertidas)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = img.tobytes()
            
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height,
                         0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            
            return textura_id
            
        except Exception as e:
            # Si no puede cargar, simplemente devuelve None (usará color sólido)
            return None    

class Objeto3D:
    def __init__(self, pos=(0, 0, 0), rot=(0, 0, 0), esc=(1, 1, 1), color=(1, 1, 1)):
        self.posicion = list(pos)
        self.rotacion = list(rot)
        self.escala = list(esc)
        self.color = color
    
    def dibujar(self):
        glPushMatrix()
        glTranslatef(*self.posicion)
        glRotatef(self.rotacion[0], 1, 0, 0)
        glRotatef(self.rotacion[1], 0, 1, 0)
        glRotatef(self.rotacion[2], 0, 0, 1)
        glScalef(*self.escala)
        glColor3f(*self.color)
        self._dibujar()
        glPopMatrix()
    
    def _dibujar(self):
        raise NotImplementedError("Debes implementar este método en la subclase")

# ------------------------- CLASES PARA FRACTALES -------------------------
class Fractal(Objeto3D):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nivel = 3  # Nivel de recursión por defecto
        self.escala_fractal = 1.0  # Escala inicial del fractal
    
    def aumentar_nivel(self):
        self.nivel = min(self.nivel + 1, 6)  # Límite máximo de recursión
    
    def disminuir_nivel(self):
        self.nivel = max(self.nivel - 1, 1)  # Límite mínimo de recursión
    
    def aumentar_escala(self):
        self.escala_fractal *= 1.2
    
    def disminuir_escala(self):
        self.escala_fractal /= 1.2


class HelechoFractal(Fractal):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_hojas = (0.1, 0.7, 0.2)
        self.color_tallo = (0.3, 0.5, 0.2)
    
    def _dibujar(self):
        glPushMatrix()
        glScalef(self.escala_fractal, self.escala_fractal, self.escala_fractal)
        glRotatef(-90, 1, 0, 0)  # Apuntar hacia arriba
        self._dibujar_helecho(self.nivel, 1.5)
        glPopMatrix()
    
    def _dibujar_helecho(self, nivel, longitud):
        if nivel == 0:
            glColor3f(*self.color_hojas)
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 0, 0)
            glVertex3f(-longitud*0.3, 0, longitud*0.8)
            glVertex3f(longitud*0.3, 0, longitud*0.8)
            glEnd()
            return
        
        glColor3f(*self.color_tallo)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, longitud)
        glEnd()
        
        glPushMatrix()
        glTranslatef(0, 0, longitud)
        
        # Sub-ramas
        for i in range(3):
            glPushMatrix()
            angle = -30 + i * 30
            glRotatef(angle, 0, 1, 0)
            self._dibujar_helecho(nivel - 1, longitud * 0.6)
            glPopMatrix()
        
        glPopMatrix()

class TrianguloSierpinski(Fractal):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_base = (0.9, 0.2, 0.1)
        self.color_borde = (0.7, 0.1, 0.0)
    
    def _dibujar(self):
        glPushMatrix()
        glScalef(self.escala_fractal, self.escala_fractal, self.escala_fractal)
        glRotatef(0, 0, 0, 1)
        
        altura = 4.0 * math.sqrt(3) / 2
        self.vertices = [
            (0, altura * 2/3, 0),
            (-2, -altura * 1/3, 0),
            (2, -altura * 1/3, 0)
        ]
        
        self._dibujar_sierpinski(self.nivel, self.vertices)
        glPopMatrix()
    
    def _dibujar_sierpinski(self, nivel, vertices):
        if nivel == 0:
            glColor3f(*self.color_base)
            glBegin(GL_TRIANGLES)
            for v in vertices:
                glVertex3f(v[0], v[1], v[2])
            glEnd()
            
            glColor3f(*self.color_borde)
            glLineWidth(2)
            glBegin(GL_LINE_LOOP)
            for v in vertices:
                glVertex3f(v[0], v[1], v[2])
            glEnd()
            return
        
        p1, p2, p3 = vertices
        m1 = ((p1[0] + p2[0])/2, (p1[1] + p2[1])/2, (p1[2] + p2[2])/2)
        m2 = ((p2[0] + p3[0])/2, (p2[1] + p3[1])/2, (p2[2] + p3[2])/2)
        m3 = ((p3[0] + p1[0])/2, (p3[1] + p1[1])/2, (p3[2] + p1[2])/2)
        
        self._dibujar_sierpinski(nivel - 1, [p1, m1, m3])
        self._dibujar_sierpinski(nivel - 1, [m1, p2, m2])
        self._dibujar_sierpinski(nivel - 1, [m3, m2, p3])
class CuboMenger(Fractal):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.2, 0.5, 0.8)
    
    def _dibujar(self):
        glPushMatrix()
        glScalef(self.escala_fractal, self.escala_fractal, self.escala_fractal)
        glColor3f(*self.color)
        self._dibujar_cubo(self.nivel, 1.0)
        glPopMatrix()
    
    def _dibujar_cubo(self, nivel, tamaño):
        if nivel == 0:
            glutSolidCube(tamaño)
            return
        
        tercio = tamaño / 3
        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                for z in [-1, 0, 1]:
                    # Saltar el cubo central y los centros de las caras
                    if (x == 0 and y == 0) or (x == 0 and z == 0) or (y == 0 and z == 0):
                        continue
                    
                    glPushMatrix()
                    glTranslatef(x*tercio, y*tercio, z*tercio)
                    self._dibujar_cubo(nivel - 1, tercio)
                    glPopMatrix()


class Auto(Objeto3D):
    def __init__(self, textura_cuerpo=None, **kwargs):
        super().__init__(**kwargs)
        self.color_cuerpo = (0.66, 0.66, 0.9)   # Rojo brillante
        self.color_ventanas = (0.7, 0.9, 1.0, 0.3)  # Azul transparente
        self.color_llantas = (0.2, 0.2, 0.2)  # Negro
        self.color_luces_delanteras = (1.0, 1.0, 0.9)  # Blanco amarillento
        self.color_luces_traseras = (1.0, 0.1, 0.1)  # Rojo
        self.color_interior = (0.2, 0.2, 0.2)  # Gris oscuro
        self.textura_cuerpo = textura_cuerpo
        self.ancho = 2.2
        self.largo = 4.2
        self.alto = 1.4

    def _dibujar(self):
        # Orden de dibujo optimizado
        self._dibujar_chasis()
        self._dibujar_interior()
        self._dibujar_ventanas()
        self._dibujar_detalles_exteriores()
    
    def _dibujar_chasis(self):
        if self.textura_cuerpo and self.textura_cuerpo.id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura_cuerpo.id)
            glColor3f(1, 1, 1)
        else:
            glColor3f(*self.color_cuerpo)
        
        # Base del auto (chasis)
        glPushMatrix()
        glTranslatef(0, 0.6, 0)
        glScalef(self.ancho, 0.2, self.largo)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Laterales del auto (puertas)
        for lado in [-1, 1]:
            glPushMatrix()
            glTranslatef(lado * self.ancho * 0.45, 1, 0)
            glScalef(0.1, 0.5, self.largo * 0.8)
            glutSolidCube(1.0)
            glPopMatrix()
        
        # Parte delantera (capó)
        glPushMatrix()
        glTranslatef(0, 0.8, -self.largo * 0.4)
        glScalef(self.ancho * 0.9, 0.3, self.largo * 0.3)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Parte trasera (maletero)
        glPushMatrix()
        glTranslatef(0, 0.8, self.largo * 0.35)
        glScalef(self.ancho * 0.9, 0.3, self.largo * 0.3)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Techo del auto
        glPushMatrix()
        glTranslatef(0, 1.5, 0)
        glScalef(self.ancho * 0.8, 0.05, self.largo * 0.5+0.5)
        glutSolidCube(1.0)
        glPopMatrix()
        
   
        if self.textura_cuerpo and self.textura_cuerpo.id:
            glDisable(GL_TEXTURE_2D)
    
    def _dibujar_ventanas(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*self.color_ventanas)
        
        # Parabrisas delantero
        glPushMatrix()
        glTranslatef(0, 1.3, -self.largo * 0.2)
        glRotatef(-20, 1, 0, 0)
        glScalef(self.ancho * 0.7, 0.3, 0.01)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Ventana trasera
        glPushMatrix()
        glTranslatef(0, 1.3, self.largo *0.2-2.4)
        glRotatef(20, 1, 0, 0)
        glScalef(self.ancho * 0.8, 0.46, 0.01)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Ventanas laterales
        for lado in [-1, 1]:
            # Ventana delantera
            glPushMatrix()
            glTranslatef(lado * self.ancho * 0.4, 1.3, -self.largo * 0.1)
            glScalef(0.01, 0.3, self.largo * 0.25)
            glutSolidCube(1.0)
            glPopMatrix()
            
            # Ventana trasera
            glPushMatrix()
            glTranslatef(lado * self.ancho * 0.4, 1.3, self.largo * 0.1)
            glScalef(0.01, 0.3, self.largo * 0.25)
            glutSolidCube(1.0)
            glPopMatrix()
        
        glDisable(GL_BLEND)
    
    def _dibujar_interior(self):
        glColor3f(*self.color_interior)
        
        # Tablero
        glPushMatrix()
        glTranslatef(0, 0.9, -self.largo * 0.2)
        glScalef(self.ancho * 0.7, 0.1, 0.2)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Asientos
        for lado in [-1, 1]:
            # Base del asiento
            glPushMatrix()
            glTranslatef(lado * self.ancho * 0.3, 0.7, 0)
            glScalef(0.4, 0.2, 0.6)
            glutSolidCube(1.0)
            glPopMatrix()
            
            
        # Volante
        glColor3f(0, 0, 1.0)
        glPushMatrix()
        glTranslatef(self.ancho * 0.25, 1.2, -self.largo * 0.15)
        glRotatef(-10, 1, 0, 0)
        glutSolidTorus(0.05, 0.15, 8, 16)
        glPopMatrix()
    
    def _dibujar_detalles_exteriores(self):
        # Llantas
        glColor3f(*self.color_llantas)
        pos_llantas = [
            (-0.8, -1.5), (0.8, -1.5),  # Traseras
            (-0.8, 1.5), (0.8, 1.5)     # Delanteras
        ]
        
        for x, z in pos_llantas:
            glPushMatrix()
            glTranslatef(x,0.2, z)
            glRotatef(90, 0, 1, 0)
            glutSolidTorus(0.3, 0.31, 16, 16)
            glPopMatrix()
        
        # Luces delanteras
        glColor3f(*self.color_luces_delanteras)
        for x in [-0.6, -0.3, 0.3, 0.6]:
            glPushMatrix()
            glTranslatef(0, 0.6, -self.largo*0.3+3.6 )
            glutSolidSphere(0.1, 12, 12)
            glPopMatrix()
        
        # Luces traseras
        glColor3f(*self.color_luces_traseras)
        for x in [-0.7, -0.4, 0.4, 0.7]:
            glPushMatrix()
            glTranslatef(x, 0.6, self.largo * 0.001-2.5)
            glutSolidSphere(0.08, 10, 10)
            glPopMatrix()
        
class Casa(Objeto3D):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_paredes = (0.7, 0.5, 0.3)
        self.color_techo = (0.8, 0.2, 0.1)
        self.color_puerta = (0.4, 0.2, 0.0)
    
    def _dibujar(self):
        # Paredes
        glColor3f(*self.color_paredes)
        glPushMatrix()
        glScalef(2, 4.5, 2)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Techo (pirámide)
        glColor3f(*self.color_techo)
        glPushMatrix()
        glTranslatef(0, 2.3, 0)
        glRotatef(-90, 1, 0, 0)
        glutSolidCone(2.5, 1, 4, 1)
        glPopMatrix()
        
        # Puerta
        glColor3f(*self.color_puerta)
        glPushMatrix()
        glTranslatef(0, 0.5, 1.01)
        glScalef(0.6, 1.0, 0.1)
        glutSolidCube(1.0)
        glPopMatrix()

class Montana(Objeto3D):
    def __init__(self, textura=None, **kwargs):
        super().__init__(**kwargs)
        self.textura = textura
        self.color_base = (0.4, 0.3, 0.1)  # Color marrón base
        self.color_pico = (0.5, 0.4, 0.2)  # Color picos
        self.picos = [(-1.5, -1.5, 5), (1.5, -1.5, 4), (0, 1.5, 6)]  # (x, z, altura)
    
    def _dibujar(self):
        # Configurar textura si existe
        if self.textura and self.textura.id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura.id)
            glColor3f(1, 1, 1)
        else:
            glColor3f(*self.color_base)

        # Habilitar polígonos de dos caras para montañas
        glDisable(GL_CULL_FACE)  # Desactivar culling para montañas
        
        # Base de la montaña (usando GLUT para la base cuadrada)
        glPushMatrix()
        glScalef(8, 0.1, 8)  # 8x8 unidades (equivalente a -4 a 4 en tu versión)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Dibujar picos (usando GL_TRIANGLE_FAN como en tu versión original)
        for offset_x, offset_z, height in self.picos:
            if self.textura and self.textura.id:
                glBegin(GL_TRIANGLE_FAN)
                glTexCoord2f(0.5, 1); glVertex3f(offset_x, height, offset_z)
                glTexCoord2f(0, 0); glVertex3f(-4, 0, -4)
                glTexCoord2f(1, 0); glVertex3f(4, 0, -4)
                glTexCoord2f(1, 1); glVertex3f(4, 0, 4)
                glTexCoord2f(0, 1); glVertex3f(-4, 0, 4)
                glTexCoord2f(0, 0); glVertex3f(-4, 0, -4)
                glEnd()
            else:
                glColor3f(*self.color_pico)
                glBegin(GL_TRIANGLE_FAN)
                glVertex3f(offset_x, height, offset_z)
                glVertex3f(-4, 0, -4)
                glVertex3f(4, 0, -4)
                glVertex3f(4, 0, 4)
                glVertex3f(-4, 0, 4)
                glVertex3f(-4, 0, -4)
                glEnd()
        
        if self.textura and self.textura.id:
            glDisable(GL_TEXTURE_2D)
        
        glEnable(GL_CULL_FACE)  # Reactivar culling


class Carretera(Objeto3D):
    def __init__(self, textura=None, puntos_control=None, **kwargs):  # AGREGAR textura=None
        super().__init__(**kwargs)
        self.textura = textura  # AGREGAR esta línea

        self.puntos_control = puntos_control or [
            (-5.0, 0.01, 40.0),
            (-100.0, 0.01, 20.0),
            (100.0, 0.01, -20.0),
            (5.0, 0.01, -40.0)
        ]
        self.segmentos = 100
        self.ancho = 5
    
    def _calcular_punto(self, t):
        """Calcula un punto en la curva Bézier cúbica"""
        if len(self.puntos_control) < 4:
            return self.puntos_control[0]
        
        num_segmentos = len(self.puntos_control) - 3
        segmento = min(int(t * num_segmentos), num_segmentos - 1)
        t_segmento = (t * num_segmentos) - segmento
        
        p0 = self.puntos_control[segmento]
        p1 = self.puntos_control[segmento + 1]
        p2 = self.puntos_control[segmento + 2]
        p3 = self.puntos_control[segmento + 3]
        
        mt = 1 - t_segmento
        mt2 = mt * mt
        t2 = t_segmento * t_segmento
        
        x = mt2 * mt * p0[0] + 3 * mt2 * t_segmento * p1[0] + 3 * mt * t2 * p2[0] + t2 * t_segmento * p3[0]
        y = mt2 * mt * p0[1] + 3 * mt2 * t_segmento * p1[1] + 3 * mt * t2 * p2[1] + t2 * t_segmento * p3[1]
        z = mt2 * mt * p0[2] + 3 * mt2 * t_segmento * p1[2] + 3 * mt * t2 * p2[2] + t2 * t_segmento * p3[2]
        
        return (x, y, z)
    
    def _dibujar(self):
        # Desactivar culling temporalmente para la carretera
        glDisable(GL_CULL_FACE)


        if self.textura and self.textura.id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura.id)
            glColor3f(1, 1, 1)  # Blanco para no alterar la textura
        else:
            glColor3f(0.2, 0.2, 0.2)
        
        # Dibujar la carretera
        glBegin(GL_QUAD_STRIP)
        for i in range(self.segmentos + 1):
            t = i / self.segmentos
            punto = self._calcular_punto(t)
            
            # Calcular tangente
            if i < self.segmentos:
                t_sig = (i + 0.01) / self.segmentos
                punto_sig = self._calcular_punto(t_sig)
                tangente = (punto_sig[0] - punto[0], 0, punto_sig[2] - punto[2])
            else:
                tangente = (0, 0, 1)
            
            # Calcular normal
            normal = (-tangente[2], 0, tangente[0])
            magnitud = math.sqrt(normal[0]**2 + normal[2]**2)
            if magnitud > 0:
                normal = (normal[0]/magnitud * self.ancho, 0, normal[2]/magnitud * self.ancho)
            
            # Bordes de la carretera
            borde_izq = (punto[0] + normal[0], punto[1], punto[2] + normal[2])
            borde_der = (punto[0] - normal[0], punto[1], punto[2] - normal[2])
            
            # Agregar coordenadas de textura
            glTexCoord2f(0, t * 10)  # Repetir textura a lo largo
            glVertex3f(*borde_izq)
            glTexCoord2f(1, t * 10)
            glVertex3f(*borde_der)
        glEnd()

        # Desactivar textura antes de dibujar marcas viales
        if self.textura and self.textura.id:
            glDisable(GL_TEXTURE_2D)
        
        # Marcas viales
        glColor3f(1, 1, 1)
        puntos_centrales = [self._calcular_punto(i/self.segmentos) for i in range(self.segmentos + 1)]
        
        for i in range(0, self.segmentos - 1, 4):
            p1 = puntos_centrales[i]
            p2 = puntos_centrales[i + 2]
            
            p1 = (p1[0], p1[1] + 0.01, p1[2])
            p2 = (p2[0], p2[1] + 0.01, p2[2])
            
            tangente = (p2[0] - p1[0], 0, p2[2] - p1[2])
            normal = (-tangente[2], 0, tangente[0])
            magnitud = math.sqrt(normal[0]**2 + normal[2]**2)
            if magnitud > 0:
                normal = (normal[0]/magnitud * 0.15, 0, normal[2]/magnitud * 0.15)
            
            glBegin(GL_QUADS)
            glVertex3f(p1[0] + normal[0], p1[1], p1[2] + normal[2])
            glVertex3f(p1[0] - normal[0], p1[1], p1[2] - normal[2])
            glVertex3f(p2[0] - normal[0], p2[1], p2[2] - normal[2])
            glVertex3f(p2[0] + normal[0], p2[1], p2[2] + normal[2])
            glEnd()

        glEnable(GL_CULL_FACE)  # Reactivar culling

class Arbol(Objeto3D):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_tronco = (0.4, 0.2, 0.1)
        self.color_copa = (0.1, 0.6, 0.2)
    
    def _dibujar(self):
        # Tronco
        glColor3f(*self.color_tronco)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glutSolidCylinder(0.2, 2, 8, 1)
        glPopMatrix()
        
        # Copa
        glColor3f(*self.color_copa)
        glPushMatrix()
        glTranslatef(0, 2, 0)
        glutSolidSphere(1, 8, 8)
        glPopMatrix()

class Suelo(Objeto3D):
    def __init__(self, textura=None, **kwargs):
        super().__init__(**kwargs)
        self.textura = textura
        self.color = (0.5, 0.7, 0.3)  # Verde hierba
    
    def _dibujar(self):
        if self.textura and self.textura.id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.textura.id)
            glColor3f(1, 1, 1)
        else:
            glColor3f(*self.color)
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-100, 0, 100)
        glTexCoord2f(20, 0); glVertex3f(100, 0, 100)
        glTexCoord2f(20, 20); glVertex3f(100, 0, -100)
        glTexCoord2f(0, 20); glVertex3f(-100, 0, -100)
        glEnd()
        
        if self.textura and self.textura.id:
            glDisable(GL_TEXTURE_2D)

class Inicial3D(Objeto3D):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (1, 1, 0)
        self.grosor = 0.2
    
    def _dibujar(self):

        glDisable(GL_LIGHTING)
        glColor3f(*self.color)
        glLineWidth(5)
        
        # Parte izquierda de la A
        glBegin(GL_QUADS)
        glVertex3f(-0.8, -1, 0)
        glVertex3f(-0.6, -1, 0)
        glVertex3f(0.0, 1, 0)
        glVertex3f(-0.1, 1, 0)
        
        glVertex3f(-0.1, 1, self.grosor)
        glVertex3f(0.0, 1, self.grosor)
        glVertex3f(-0.6, -1, self.grosor)
        glVertex3f(-0.8, -1, self.grosor)
        
        glVertex3f(-0.8, -1, 0)
        glVertex3f(-0.8, -1, self.grosor)
        glVertex3f(-0.1, 1, self.grosor)
        glVertex3f(-0.1, 1, 0)
        
        glVertex3f(-0.6, -1, 0)
        glVertex3f(-0.6, -1, self.grosor)
        glVertex3f(0.0, 1, self.grosor)
        glVertex3f(0.0, 1, 0)
        glEnd()
        
        # Parte derecha de la A
        glBegin(GL_QUADS)
        glVertex3f(0.1, 1, 0)
        glVertex3f(0.0, 1, 0)
        glVertex3f(0.8, -1, 0)
        glVertex3f(0.6, -1, 0)
        
        glVertex3f(0.6, -1, self.grosor)
        glVertex3f(0.8, -1, self.grosor)
        glVertex3f(0.0, 1, self.grosor)
        glVertex3f(0.1, 1, self.grosor)
        
        glVertex3f(0.0, 1, 0)
        glVertex3f(0.0, 1, self.grosor)
        glVertex3f(0.6, -1, self.grosor)
        glVertex3f(0.6, -1, 0)
        
        glVertex3f(0.1, 1, 0)
        glVertex3f(0.1, 1, self.grosor)
        glVertex3f(0.8, -1, self.grosor)
        glVertex3f(0.8, -1, 0)
        glEnd()
        
        # Barra horizontal
        glBegin(GL_QUADS)
        glVertex3f(-0.3, 0.3, 0)
        glVertex3f(0.3, 0.3, 0)
        glVertex3f(0.3, 0.1, 0)
        glVertex3f(-0.3, 0.1, 0)
        
        glVertex3f(-0.3, 0.1, self.grosor)
        glVertex3f(0.3, 0.1, self.grosor)
        glVertex3f(0.3, 0.3, self.grosor)
        glVertex3f(-0.3, 0.3, self.grosor)
        
        glVertex3f(-0.3, 0.1, 0)
        glVertex3f(-0.3, 0.1, self.grosor)
        glVertex3f(-0.3, 0.3, self.grosor)
        glVertex3f(-0.3, 0.3, 0)
        
        glVertex3f(0.3, 0.3, 0)
        glVertex3f(0.3, 0.3, self.grosor)
        glVertex3f(0.3, 0.1, self.grosor)
        glVertex3f(0.3, 0.1, 0)
        glEnd()
        
        glEnable(GL_LIGHTING)

class Escena:
    def __init__(self, textura_hierba=None, textura_montana=None, textura_asfalto=None):  # AGREGAR textura_asfalto aquí
        self.ancho = 1024
        self.alto = 768
        
        # Configuración de cámara
        self.cam_distancia = 8
        self.cam_altura = 3.0
        self.cam_offset_y = 1.5
        self.modo_vista = 'perspectiva'
        
        # Estado del auto
        self.auto_pos_x = -10
        self.auto_pos_y = 0.2
        self.auto_pos_z = 40
        self.auto_angulo = 0
        self.velocidad_auto = 0
        self.velocidad_angular = 0

        # Crear objetos
        self.auto = Auto(pos=(self.auto_pos_x, self.auto_pos_y, self.auto_pos_z))
        self.carretera = Carretera(textura=textura_asfalto)  # Agregar textura
        self.suelo = Suelo(textura=textura_hierba)  # Ya está bien
        self.inicial = Inicial3D(pos=(-6, 2, -5), esc=(0.5, 0.8, 0.5))
        self.objetos = self._generar_entorno(textura_montana)  # Ya está bien

        # Parámetros de control
        self.aceleracion = 0.008
        self.velocidad_rotacion = 2.0
        self.friccion = 0.95
        self.friccion_angular = 0.9

        # Estado de teclas
        self.tecla_arriba = False
        self.tecla_abajo = False
        self.tecla_izquierda = False
        self.tecla_derecha = False




        self.boton_seleccionado = None
        self.botones = [
            {"texto": "Árbol", "x": 20, "y": 50, "tipo": "arbol"},
            {"texto": "Casa", "x": 90, "y": 50, "tipo": "casa"},
            {"texto": "Montaña", "x": 160, "y": 50, "tipo": "montana"},
            {"texto": "Auto", "x": 230, "y": 50, "tipo": "auto"},
            {"texto": "Eliminar", "x": 300, "y": 50, "tipo": "eliminar", "color": (0.8, 0.3, 0.3)},
            {"texto": "Helecho", "x": 370, "y": 50, "tipo": "helecho_fractal"},
            {"texto": "Sierpinski", "x": 440, "y": 50, "tipo": "sierpinski"},
            {"texto": "Cubo M.", "x": 510, "y": 50, "tipo": "cubo_menger"},
            {"texto": "+Tam", "x": 650, "y": 50, "tipo": "aumentar_tam", "color": (0.3, 0.7, 0.3)},
            {"texto": "-Tam", "x": 710, "y": 50, "tipo": "disminuir_tam", "color": (0.7, 0.3, 0.3)}
        ]


        # Objeto fractal seleccionado para modificar
        self.fractal_seleccionado = None



    def _generar_entorno(self,textura_montana=None):
        objetos = []

        return objetos
    
    def _calcular_tangente_en_punto(self, punto_obj):
        mejor_t = 0
        mejor_dist = float('inf')
        
        for i in range(100):
            t = i / 99
            punto_carretera = self.carretera._calcular_punto(t)
            dist = math.sqrt(
                (punto_obj[0] - punto_carretera[0])**2 +
                (punto_obj[1] - punto_carretera[1])**2 +
                (punto_obj[2] - punto_carretera[2])**2
            )
            
            if dist < mejor_dist:
                mejor_dist = dist
                mejor_t = t
        
        t_sig = min(mejor_t + 0.01, 1.0)
        punto_sig = self.carretera._calcular_punto(t_sig)
        return (
            punto_sig[0] - punto_obj[0],
            punto_sig[1] - punto_obj[1],
            punto_sig[2] - punto_obj[2]
        )
    
    def dibujar(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self._configurar_vista()
        self._configurar_luz()
        
        # Obtener posición actual de la luz
        luz_pos = self._obtener_posicion_luz_actual()

        # Dibujar el suelo primero
        self.suelo.dibujar()
        
        # Dibujar la carretera
        self.carretera.dibujar()

        # Dibujar sombras (con profundidad deshabilitada temporalmente)
        glDepthMask(GL_FALSE)
        luz_pos = self._obtener_posicion_luz_actual()
        for obj in self.objetos:
            if isinstance(obj, (Arbol, Casa, Montana, Auto)):
                self._dibujar_sombra_objeto(obj, luz_pos)
        glDepthMask(GL_TRUE)
 

        # Dibujar los objetos
        for obj in self.objetos:
            obj.dibujar()
    
        
        # Dibujar el auto
        self.auto.dibujar()

        # Dibujar la inicial
        self.inicial.dibujar()
        

        self.dibujar_barra_herramientas()


        glutSwapBuffers()
    
    def _dibujar_sombra_objeto(self, objeto, luz_pos):
        """Dibuja la sombra de un objeto proyectada sobre el suelo"""
        # Desactivar luces y texturas para las sombras
        glDisable(GL_TEXTURE_2D)
        
        # Habilitar blending para transparencia
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Color negro semitransparente para todas las sombras
        glColor4f(0.0, 0.0, 0.0, 0.4)
        
        # Evitar z-fighting con el suelo
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(-1.0, -1.0)
        
        # Calcular la proyección de la sombra manualmente
        glPushMatrix()
        
        # Obtener la posición del objeto
        obj_x, obj_y, obj_z = objeto.posicion
        
        # Calcular dónde debe proyectarse la sombra en el suelo (y=0.01)
        y_suelo = 0.01
        y_luz = luz_pos[1]
        y_obj = obj_y
        
        # Factor de proyección
        if y_luz > y_obj:  # Solo proyectar si la luz está arriba del objeto
            factor = (y_luz - y_suelo) / (y_luz - y_obj)
            
            # Posición proyectada de la sombra
            sombra_x = luz_pos[0] + (obj_x - luz_pos[0]) * factor
            sombra_z = luz_pos[2] + (obj_z - luz_pos[2]) * factor
            
            # Aplicar transformación de sombra
            glTranslatef(sombra_x, y_suelo, sombra_z)
            
            # Escalar en Y para aplastar la sombra
            escala_sombra = 0.1
            if isinstance(objeto, Auto):
                glScalef(1.0, escala_sombra, 1.0)
            elif isinstance(objeto, Arbol):
                glScalef(0.8, escala_sombra, 0.8)
            elif isinstance(objeto, Casa):
                glScalef(0.9, escala_sombra, 0.9)
            elif isinstance(objeto, Montana):
                glScalef(0.7, escala_sombra, 0.7)
            
            # Aplicar rotación del objeto original
            glRotatef(objeto.rotacion[0], 1, 0, 0)
            glRotatef(objeto.rotacion[1], 0, 1, 0)
            glRotatef(objeto.rotacion[2], 0, 0, 1)
            
            # Dibujar una versión simplificada del objeto como sombra
            if isinstance(objeto, Auto):
                self._dibujar_sombra_auto()
            elif isinstance(objeto, Arbol):
                self._dibujar_sombra_arbol()
            elif isinstance(objeto, Casa):
                self._dibujar_sombra_casa()
            elif isinstance(objeto, Montana):
                self._dibujar_sombra_montana()
        
        glPopMatrix()
        
        # Restaurar configuración
        glDisable(GL_POLYGON_OFFSET_FILL)
        glDisable(GL_BLEND)

    def _dibujar_sombra_auto(self):
        """Dibuja una sombra simplificada del auto"""
        glPushMatrix()
        glScalef(2.4, 1, 4.0)
        glutSolidCube(1.0)
        glPopMatrix()

    def _dibujar_sombra_arbol(self):
        """Dibuja una sombra simplificada del árbol"""
        # Tronco
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glutSolidCylinder(0.2, 2, 8, 1)
        glPopMatrix()
        
        # Copa
        glPushMatrix()
        glTranslatef(0, 2, 0)
        glutSolidSphere(1, 8, 8)
        glPopMatrix()

    def _dibujar_sombra_casa(self):
        """Dibuja una sombra simplificada de la casa"""
        # Paredes
        glPushMatrix()
        glScalef(2, 2.5, 2)
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Techo
        glPushMatrix()
        glTranslatef(0, 1.3, 0)
        glRotatef(-90, 1, 0, 0)
        glutSolidCone(2.5, 1, 4, 1)
        glPopMatrix()

    def _dibujar_sombra_montana(self):
        """Dibuja una sombra simplificada de la montaña"""
        glPushMatrix()
        glScalef(8, 3, 8)
        glutSolidCube(1.0)
        glPopMatrix()

    def _obtener_posicion_luz_actual(self):
        """Obtiene la posición actual de la luz basada en la transición día/noche"""
        zona_transicion_inicio = -20.0
        zona_transicion_fin = 20.0
        
        if self.auto_pos_x <= zona_transicion_inicio:
            factor_noche = 0.0
        elif self.auto_pos_x >= zona_transicion_fin:
            factor_noche = 1.0
        else:
            factor_noche = (self.auto_pos_x - zona_transicion_inicio) / (zona_transicion_fin - zona_transicion_inicio)
            factor_noche = (1.0 - math.cos(factor_noche * math.pi)) / 2.0
        
        factor_dia = 1.0 - factor_noche
        
        # Calcular posición de luz
        altura_luz = 15.0 * factor_dia + 8.0 * factor_noche
        pos_x_luz = 0.0 * factor_dia + 3.0 * factor_noche
        
        return [pos_x_luz, altura_luz, 5.0, 1.0]
    
    def _configurar_vista(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        aspect = self.ancho / self.alto
        
        if self.modo_vista == 'perspectiva':
            gluPerspective(60, aspect, 0.1, 200.0)
            
            radianes = math.radians(self.auto_angulo)
            
            cam_x = self.auto_pos_x - math.sin(radianes) * self.cam_distancia
            cam_z = self.auto_pos_z - math.cos(radianes) * self.cam_distancia
            cam_y = self.auto_pos_y + self.cam_altura
            
            mirar_x = self.auto_pos_x + math.sin(radianes) * 5
            mirar_z = self.auto_pos_z + math.cos(radianes) * 5
            mirar_y = self.auto_pos_y + self.cam_offset_y
            
            gluLookAt(cam_x, cam_y, cam_z,
                    mirar_x, mirar_y, mirar_z,
                    0, 1, 0)
        else: # Vista ortogonal
        # Ajusta estos valores según lo que necesites
            zoom = 45  # Puedes ajustar este valor para hacer zoom
            glOrtho(-zoom * aspect, zoom * aspect, -zoom, zoom, 0.1, 100.0)
            
            # Posición fija de la cámara en vista ortogonal
            cam_x = 0
            cam_y = 15  # Altura de la cámara
            cam_z = 0
            
            gluLookAt(cam_x, cam_y, cam_z,
                    cam_x, 0, cam_z - 1,  # Mira hacia abajo
                    0, 1, 0)  # Vector "arriba"
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def _configurar_luz(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        zona_transicion_inicio = -20.0
        zona_transicion_fin = 20.0
        ancho_transicion = zona_transicion_fin - zona_transicion_inicio
        
        if self.auto_pos_x <= zona_transicion_inicio:
            factor_noche = 0.0
        elif self.auto_pos_x >= zona_transicion_fin:
            factor_noche = 1.0
        else:
            factor_noche = (self.auto_pos_x - zona_transicion_inicio) / ancho_transicion
            factor_noche = (1.0 - math.cos(factor_noche * math.pi)) / 2.0
        
        factor_dia = 1.0 - factor_noche
        
        # Colores del día
        luz_dia_difusa = [0.8, 0.8, 0.7, 1.0]
        luz_dia_ambiente = [0.4, 0.4, 0.4, 1.0]
        cielo_dia = [0.53, 0.81, 0.98]
        
        # Colores de la noche
        luz_noche_difusa = [0.15, 0.15, 0.25, 1.0]
        luz_noche_ambiente = [0.05, 0.05, 0.1, 1.0]
        cielo_noche = [0.02, 0.02, 0.1]
        
        # Interpolación suave entre día y noche
        luz_difusa = [
            luz_dia_difusa[0] * factor_dia + luz_noche_difusa[0] * factor_noche,
            luz_dia_difusa[1] * factor_dia + luz_noche_difusa[1] * factor_noche,
            luz_dia_difusa[2] * factor_dia + luz_noche_difusa[2] * factor_noche,
            1.0
        ]
        
        luz_ambiente = [
            luz_dia_ambiente[0] * factor_dia + luz_noche_ambiente[0] * factor_noche,
            luz_dia_ambiente[1] * factor_dia + luz_noche_ambiente[1] * factor_noche,
            luz_dia_ambiente[2] * factor_dia + luz_noche_ambiente[2] * factor_noche,
            1.0
        ]
        
        # Color del cielo con interpolación suave
        color_cielo = [
            cielo_dia[0] * factor_dia + cielo_noche[0] * factor_noche,
            cielo_dia[1] * factor_dia + cielo_noche[1] * factor_noche,
            cielo_dia[2] * factor_dia + cielo_noche[2] * factor_noche
        ]
        
        # Aplicar colores calculados
        glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
        glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
        glClearColor(color_cielo[0], color_cielo[1], color_cielo[2], 1.0)
        
        # Posición de la luz que simula el sol/luna
        altura_luz = 15.0 * factor_dia + 8.0 * factor_noche
        pos_x_luz = 0.0 * factor_dia + 3.0 * factor_noche
        
        glLightfv(GL_LIGHT0, GL_POSITION, [pos_x_luz, altura_luz, 5.0, 1.0])
        
        # Habilitar materiales
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Configurar segunda luz para simular luna durante la noche
        if factor_noche > 0.3:
            glEnable(GL_LIGHT1)
            luz_luna = [0.1 * factor_noche, 0.1 * factor_noche, 0.2 * factor_noche, 1.0]
            ambiente_luna = [0.05 * factor_noche, 0.05 * factor_noche, 0.1 * factor_noche, 1.0]
            
            glLightfv(GL_LIGHT1, GL_DIFFUSE, luz_luna)
            glLightfv(GL_LIGHT1, GL_AMBIENT, ambiente_luna)
            glLightfv(GL_LIGHT1, GL_POSITION, [-5.0, 12.0, -10.0, 1.0])
        else:
            glDisable(GL_LIGHT1)



    def actualizar_auto(self):
        # Control de velocidad lineal
        if not (self.tecla_arriba or self.tecla_abajo):
            self.velocidad_auto *= self.friccion
            if abs(self.velocidad_auto) < 0.001:
                self.velocidad_auto = 0
        
        if self.tecla_arriba:
            self.velocidad_auto = min(self.velocidad_auto + self.aceleracion, 0.25)
        elif self.tecla_abajo:
            self.velocidad_auto = max(self.velocidad_auto - self.aceleracion, -0.15)
        



        # Control de rotación
        if not (self.tecla_izquierda or self.tecla_derecha):
            self.velocidad_angular *= self.friccion_angular
            if abs(self.velocidad_angular) < 0.1:
                self.velocidad_angular = 0
        
        if abs(self.velocidad_auto) > 0.01:
            if self.tecla_izquierda:
                self.velocidad_angular = min(self.velocidad_angular + 0.3, self.velocidad_rotacion)
            elif self.tecla_derecha:
                self.velocidad_angular = max(self.velocidad_angular - 0.3, -self.velocidad_rotacion)
        else:
            self.velocidad_angular *= 0.8
        
        # Aplicar rotación
        self.auto_angulo += self.velocidad_angular
        self.auto_angulo = self.auto_angulo % 360
        
        # Mover el auto según su ángulo actual
        if abs(self.velocidad_auto) > 0:
            radianes = math.radians(self.auto_angulo)
            self.auto_pos_x += math.sin(radianes) * self.velocidad_auto
            self.auto_pos_z += math.cos(radianes) * self.velocidad_auto
        
        # Actualizar posición del objeto auto
        self.auto.posicion = [self.auto_pos_x, self.auto_pos_y, self.auto_pos_z]
        self.auto.rotacion = [0, self.auto_angulo, 0]

    def manejar_teclado(self, tecla, x, y):
        tecla = tecla.lower()
        if tecla == b'\x1b':  # ESC
            sys.exit(0)
        elif tecla == b'o':  # Tecla O para alternar vista
            if self.modo_vista == 'perspectiva':
                self.modo_vista = 'ortogonal'
            else:
                self.modo_vista = 'perspectiva'
            glutPostRedisplay()



    def manejar_teclado_especial(self, tecla, x, y):
        if tecla == GLUT_KEY_LEFT:
            self.tecla_izquierda = True
        elif tecla == GLUT_KEY_RIGHT:
            self.tecla_derecha = True
        elif tecla == GLUT_KEY_UP:
            self.tecla_arriba = True
        elif tecla == GLUT_KEY_DOWN:
            self.tecla_abajo = True

    def manejar_teclado_especial_up(self, tecla, x, y):
        if tecla == GLUT_KEY_LEFT:
            self.tecla_izquierda = False
        elif tecla == GLUT_KEY_RIGHT:
            self.tecla_derecha = False
        elif tecla == GLUT_KEY_UP:
            self.tecla_arriba = False
        elif tecla == GLUT_KEY_DOWN:
            self.tecla_abajo = False


    def manejar_clic_raton(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # Verificar si se hizo clic en algún botón
            for boton in self.botones:
                if (boton["x"] <= x <= boton["x"] + 70 and 
                    boton["y"] <= y <= boton["y"] + 30):
                    
                    if boton["tipo"] in ["aumentar_tam", "disminuir_tam"]:
                        self._manejar_cambio_tamano(boton["tipo"])
                    else:
                        self.boton_seleccionado = boton["tipo"]
                        print(f"Botón {boton['texto']} seleccionado")
                    break
            else:
                # Si se hizo clic fuera de los botones
                if self.boton_seleccionado == "eliminar":
                    self._eliminar_objeto_en_posicion(x, y)
                elif self.boton_seleccionado:  # Para los otros botones (añadir objetos)
                    self._agregar_objeto_en_posicion(x, y)
        
        glutPostRedisplay()


    def _manejar_cambio_tamano(self, accion):
        """Maneja el aumento o disminución de tamaño del fractal seleccionado"""
        if not self.fractal_seleccionado:
            print("Selecciona un fractal primero haciendo clic en él")
            return
        
        if accion == "aumentar_tam":
            self.fractal_seleccionado.aumentar_escala()
            print(f"Tamaño aumentado a {self.fractal_seleccionado.escala_fractal:.2f}")
        elif accion == "disminuir_tam":
            self.fractal_seleccionado.disminuir_escala()
            print(f"Tamaño reducido a {self.fractal_seleccionado.escala_fractal:.2f}")


    


    def _agregar_objeto_en_posicion(self, x_2d, y_2d):
        """Convierte coordenadas 2D del ratón a 3D en la escena"""
        # Convertir coordenadas de pantalla a coordenadas 3D
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
        # El Y de OpenGL está invertido respecto a las coordenadas de la ventana
        y_2d = viewport[3] - y_2d
        
        # Obtener coordenadas en el plano del suelo (y=0)
        try:
            win_x = x_2d
            win_y = y_2d
            win_z = glReadPixels(x_2d, y_2d, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
            
            pos_3d = gluUnProject(win_x, win_y, win_z, 
                                 modelview, projection, viewport)
            
            if pos_3d:
                x, y, z = pos_3d
                if self.boton_seleccionado == "arbol":
                    nuevo_objeto = Arbol(pos=(x, 0, z))
                elif self.boton_seleccionado == "casa":
                    nuevo_objeto = Casa(pos=(x, 0, z))
                elif self.boton_seleccionado == "montana":
                    nuevo_objeto = Montana(pos=(x, 0, z))
                elif self.boton_seleccionado == "auto":
                    nuevo_objeto = Auto(pos=(x, 0.2, z))
                elif self.boton_seleccionado == "helecho_fractal":
                    nuevo_objeto = HelechoFractal(pos=(x, 0, z))
                elif self.boton_seleccionado == "sierpinski":
                    nuevo_objeto = TrianguloSierpinski(pos=(x, 1.7, z))
                elif self.boton_seleccionado == "cubo_menger":
                    nuevo_objeto = CuboMenger(pos=(x, 0.7, z))

                
                self.objetos.append(nuevo_objeto)
                # Si es un fractal, lo marcamos como seleccionado
                if isinstance(nuevo_objeto, Fractal):
                    self.fractal_seleccionado = nuevo_objeto
        except:
            print("No se pudo determinar la posición 3D")

    def _eliminar_objeto_en_posicion(self, x_2d, y_2d):
        """Intenta eliminar un objeto en la posición del clic"""
        # Convertir coordenadas 2D a 3D
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
        # El Y de OpenGL está invertido
        y_2d = viewport[3] - y_2d
        
        try:
            # Obtener profundidad en el punto del clic
            win_z = glReadPixels(x_2d, y_2d, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
            
            # Convertir a coordenadas 3D
            pos_3d = gluUnProject(x_2d, y_2d, win_z, modelview, projection, viewport)
            
            if pos_3d:
                x, y, z = pos_3d
                punto_clic = (x, y, z)
                
                # Buscar el objeto más cercano al punto de clic
                objeto_a_eliminar = None
                distancia_min = float('inf')
                umbral_distancia = 4.0
                
                for obj in self.objetos:
                    distancia = math.sqrt(
                        (obj.posicion[0] - x)**2 +
                        (obj.posicion[1] - y)**2 +
                        (obj.posicion[2] - z)**2
                    )
                    
                    if distancia < distancia_min and distancia < umbral_distancia:
                        distancia_min = distancia
                        objeto_a_eliminar = obj
                
                # Eliminar el objeto si se encontró uno cercano
                if objeto_a_eliminar:
                    self.objetos.remove(objeto_a_eliminar)
                    # Si era el fractal seleccionado, deseleccionarlo
                    if objeto_a_eliminar == self.fractal_seleccionado:
                        self.fractal_seleccionado = None
                    print("Objeto eliminado")
                else:
                    print("No se encontró objeto para eliminar en esa posición")


        except Exception as e:
            print(f"Error al intentar eliminar objeto: {str(e)}")

    def dibujar_barra_herramientas(self):
        """Dibuja la barra de herramientas en modo 2D"""
        glDisable(GL_CULL_FACE)  # <-- Añade esto

        # Guardar estado de proyección
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.ancho, self.alto, 0)  # Coordenadas invertidas en Y
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # Deshabilitar características 3D TEMPORALMENTE
        glDisable(GL_DEPTH_TEST)  # IMPORTANTE: desactivar depth test para la UI
        glDisable(GL_LIGHTING)
        
        # Dibujar fondo de la barra (gris oscuro)
        glColor3f(0.2, 0.2, 0.25)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.ancho, 0)
        glVertex2f(self.ancho, 90)
        glVertex2f(0, 90)
        glEnd()
        
        # Dibujar botones
        for boton in self.botones:
            # Color del botón (azul si está seleccionado, gris si no)
            if self.boton_seleccionado == boton["tipo"]:
                glColor3f(0.3, 0.5, 0.8)  # Azul seleccionado
            else:
                glColor3f(*boton.get("color", (0.4, 0.4, 0.5)))
            
            # Dibujar fondo del botón
            glBegin(GL_QUADS)
            glVertex2f(boton["x"], boton["y"]-20)
            glVertex2f(boton["x"] + 70, boton["y"]-20)
            glVertex2f(boton["x"] + 70, boton["y"] + 30)
            glVertex2f(boton["x"], boton["y"] + 30)
            glEnd()
            
            # Dibujar texto del botón (blanco)
            glColor3f(1, 1, 1)
            glRasterPos2f(boton["x"] + 10, boton["y"] + 10)
            for char in boton["texto"]:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
        
        # Restaurar estado OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()




    def actualizar(self):
        self.actualizar_auto()
        glutPostRedisplay()

#------------------------ MAIN -------------------------
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1024, 768)
    glutCreateWindow(b"Carrera 3D con GLUT")
    
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glClearDepth(1.0)  
    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)
    

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Cargar texturas SIN verificar si existen
    textura_hierba = Textura("hierba.jpg")      # Para el suelo
    textura_montana = Textura("montana.jpg")    # Para las montañas  
    textura_asfalto = Textura("asfalto.jpg")    # Para la carretera
    # Crear escena pasando las texturas
    escena = Escena(textura_hierba, textura_montana, textura_asfalto)
    
    glutDisplayFunc(escena.dibujar)
    glutMouseFunc(escena.manejar_clic_raton)  # <-- Nuevo callback para el ratón
    glutKeyboardFunc(escena.manejar_teclado)
    glutSpecialFunc(escena.manejar_teclado_especial)
    glutSpecialUpFunc(escena.manejar_teclado_especial_up)
    
    def timer_callback(value):
        escena.actualizar()
        glutTimerFunc(16, timer_callback, 0)
    
    def reshape(width, height):
        escena.ancho = width
        escena.alto = height
        glViewport(0, 0, width, height)
        glutPostRedisplay()
    
    glutReshapeFunc(reshape)
    glutTimerFunc(0, timer_callback, 0)
    
    print("Controles:")
    print("- Flechas: Mover el auto")
    print("- ESC: Salir")
    
    glutMainLoop()

if __name__ == "__main__":
    main()