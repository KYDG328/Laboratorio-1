# Laboratorio 1: Implementación de Árbol AVL para Gestión de Cursos de Udemy

Este repositorio contiene la implementación en Python de un Árbol Binario de Búsqueda Auto-balanceable (AVL). El sistema procesa un dataset de cursos de Udemy y utiliza como clave principal de ordenamiento un índice de satisfacción calculado mediante una suma ponderada de las calificaciones y reseñas.

## Integrantes
* Ricardo Ramos
* Francisco
* Keinerth

## Descripción del Proyecto
El programa garantiza un tiempo de ejecución eficiente $O(\log n)$ para operaciones de inserción, eliminación y búsqueda mediante la aplicación automática de rotaciones simples (LL, RR) y dobles (LR, RL) para mantener el factor de balanceo del árbol.

Adicionalmente, el sistema incluye una Interfaz Gráfica de Usuario (GUI) desarrollada con Tkinter que permite interactuar con el árbol de forma dinámica.

## Requisitos y Dependencias
El código utiliza librerías estándar de Python (`tkinter`, `decimal`, `datetime`, `dataclasses`) y requiere la instalación de dos librerías externas para el manejo de datos y la exportación visual del árbol.

Para instalar las dependencias necesarias, ejecuta el siguiente comando en tu terminal:

`pip install pandas graphviz`

**Nota sobre Graphviz:** Además de la librería de Python, es posible que el sistema operativo requiera tener instalado el software base de Graphviz y agregado a las variables de entorno (PATH) para que la exportación de imágenes `.png` funcione correctamente.

## Uso y Ejecución
1. Asegúrate de tener el archivo `dataset_courses_with_reviews.csv` en la misma ruta que el script principal.
2. Ejecuta el archivo desde la terminal:

`python nombre_del_archivo.py`

## Funcionalidades Principales
* **Cálculo de Satisfacción:** Integración de la fórmula $(rating \times 0.7) + (componente\_reviews \times 0.3)$.
* **Operaciones CRUD:** Inserción y eliminación por ID o por nivel de satisfacción.
* **Filtros de Rúbrica:**
  * Filtro A: Cursos con reseñas positivas superiores a la suma de negativas y neutrales.
  * Filtro B: Cursos creados posteriormente a una fecha especificada.
  * Filtro C: Cursos con cantidad de clases publicadas dentro de un rango.
  * Filtro D: Cursos con un tipo de reseña superior al promedio del árbol.
* **Recorridos y Relaciones:** Recorrido por niveles (BFS) y búsqueda algorítmica de nodos padre, abuelo y tío.
* **Exportación Visual:** Generación de diagramas estructurales del árbol en formato PNG.
