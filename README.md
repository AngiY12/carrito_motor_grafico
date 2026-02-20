# 🛠️ Mini-Motor Gráfico: Sandbox 3D y Simulador

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![OpenGL](https://img.shields.io/badge/OpenGL-PyOpenGL-5586A4?style=flat&logo=opengl)
![Status](https://img.shields.io/badge/Estado-Completado-success)

Un mini motor gráfico 3D y entorno de edición interactivo (inspirado en herramientas como Unity) construido desde cero con Python y **OpenGL (GLUT)**. 

El proyecto inicia como un "lienzo en blanco" (terreno despejado y carretera) donde el usuario puede conducir libremente y utilizar herramientas de *raycasting* para construir y diseñar su propio entorno en tiempo real.

## ✨ Características Principales

* **🗺️ Lienzo Despejado:** Escenario inicial vacío optimizado para que el usuario construya su nivel desde cero.
* **🖱️ Sandbox Interactivo (Raycasting):** Barra de herramientas 2D que permite seleccionar objetos y posicionarlos en el mundo 3D haciendo clic directamente sobre el terreno usando transformación de coordenadas (`gluUnProject`).
* **🌀 Renderizado de Fractales:** Generación paramétrica y recursiva de estructuras matemáticas complejas, incluyendo:
  * Helecho Fractal
  * Triángulo de Sierpinski 
  * Cubo de Menger 
* **🚗 Modelo 3D y Controles:** Vehículo interactivo con controles de aceleración, frenado, rotación, fricción e inercia. Incluye penalización de velocidad al salir del asfalto hacia el césped.
* **🌓 Iluminación y Ciclo Día/Noche:** Transición automatizada de luz y color del cielo basada en la posición del vehículo, incluyendo sol diurno y simulación de luz lunar.
* **🌑 Sombras Dinámicas:** Sistema de proyección de sombras planas calculando la intersección geométrica con el suelo según la posición de la fuente de luz y del objeto.

## 🛠️ Requisitos Previos

Asegúrate de tener instalado Python en tu sistema y ejecuta el siguiente comando para instalar las dependencias necesarias:

```bash
pip install PyOpenGL PyOpenGL_accelerate
pip install Pillow
