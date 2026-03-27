# 
# LABORATORIO 1 - ÁRBOL AVL CON DATASET DE CURSOS UDEMY
# 
# Integrantes:
# - Ricardo Ramos
# - Francisco Cuello
# - Keinerth De la Hoz
#
# Descripción:
# Este programa implementa un Árbol AVL que almacena cursos
# del dataset de Udemy, utilizando como indicador princiapl el nivel de
# satisfacción del curso.
#
# El árbol se auto-balancea después de cada inserción o
# eliminación, garantizando eficiencia en las operaciones.
#
# Funcionalidades principales:
# - Insertar, eliminar y buscar nodos
# - Filtros según condiciones de la rúbrica
# - Recorrido por niveles
# - Obtención de relaciones (padre, abuelo, tío)
# - Visualización del árbol con Graphviz
# 
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Callable, Optional, List
import os
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except Exception:
    GRAPHVIZ_AVAILABLE = False


class Utils:
    """
    Clase de utilidades que contiene funciones auxiliares
    para el manejo de datos como redondeo y fechas.
    """
    @staticmethod
    def round5(value: float) -> float:
        """
        Redondea un número a 5 cifras decimales, tal como
        lo exige la rúbrica del laboratorio.

        Parámetro:
        value (float): número a redondear

        Retorna:
        float: número redondeado
        """
        return float(Decimal(str(value)).quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP))

    @staticmethod
    def parse_date(date_str: Any) -> Optional[datetime]:
        if pd.isna(date_str):
            return None
        s = str(date_str).strip()
        if not s:
            return None
        formats = [
            "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ", "%m/%d/%Y", "%d/%m/%Y"
        ]
        for fmt in formats:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                pass
        try:
            return pd.to_datetime(s).to_pydatetime()
        except Exception:
            return None


@dataclass
class Course:
    """
    Representa un curso del dataset.

    Cada objeto Course almacena toda la información relevante
    y calcula su nivel de satisfacción, que será utilizado
    como clave en el árbol AVL.
    """
    id: int
    title: str
    url: str
    rating: float
    num_reviews: int
    num_published_lectures: int
    created: Any
    last_update_date: Any
    duration: Any
    instructors_id: Any
    image: Any
    positive_reviews: int
    negative_reviews: int
    neutral_reviews: int
    satisfaction: float

    @staticmethod
    def calculate_satisfaction(rating: float, positive_reviews: int, neutral_reviews: int,
                               negative_reviews: int, num_reviews: int) -> float:
        """
        Calcula el nivel de satisfacción del curso usando
        la fórmula especificada en la rúbrica:

        satisfaction = rating * 0.7 + componente_reviews * 0.3

        Donde:
        componente_reviews = (5*positivas + 3*neutrales + negativas) / total_reviews

        Retorna:
        float: nivel de satisfacción redondeado a 5 decimales
        """
        if num_reviews <= 0:
            review_component = 0.0
        else:
            review_component = (5 * positive_reviews + 3 * neutral_reviews + negative_reviews) / num_reviews
        return Utils.round5(rating * 0.7 + review_component * 0.3)

    @classmethod
    def from_row(cls, row: pd.Series) -> "Course":
        rating = float(row["rating"])
        positive_reviews = int(row["positive_reviews"])
        negative_reviews = int(row["negative_reviews"])
        neutral_reviews = int(row["neutral_reviews"])
        num_reviews = int(row["num_reviews"])
        satisfaction = cls.calculate_satisfaction(
            rating, positive_reviews, neutral_reviews, negative_reviews, num_reviews
        )
        return cls(
            id=int(row["id"]),
            title=str(row["title"]),
            url=str(row["url"]),
            rating=rating,
            num_reviews=num_reviews,
            num_published_lectures=int(row["num_published_lectures"]),
            created=row["created"],
            last_update_date=row["last_update_date"],
            duration=row["duration"],
            instructors_id=row["instructors_id"],
            image=row["image"],
            positive_reviews=positive_reviews,
            negative_reviews=negative_reviews,
            neutral_reviews=neutral_reviews,
            satisfaction=satisfaction
        )

    def key(self) -> tuple[float, int]:
        """
        Clave de ordenamiento del árbol AVL.
        Se usa la tupla (satisfaction, id) para mantener el orden
        y garantizar que no haya duplicados de ID.
        """
        return (self.satisfaction, self.id)

    def summary(self) -> str:
        """
        Retorna un resumen corto del curso para mostrar
        en la lista de resultados de la interfaz gráfica.
        """
        return f"ID: {self.id} | Satisfaction: {self.satisfaction:.5f} | {self.title}"

    def to_dict(self) -> dict:
        """
        Convierte el objeto Course en un diccionario.
        Se utiliza para mostrar toda la información del curso
        cuando se selecciona un nodo en la interfaz.
        """
        return self.__dict__.copy()


class AVLNode:
    """
    Nodo del árbol AVL.

    Cada nodo almacena un Course y mantiene la altura
    para realizar el balanceo automático.
    """
    def __init__(self, course: Course):
        self.course = course
        self.left: Optional["AVLNode"] = None
        self.right: Optional["AVLNode"] = None
        self.height = 1


class AVLCourseTree:
    """
    Implementación de un Árbol AVL.

    Este árbol se mantiene balanceado automáticamente
    después de cada operación de inserción o eliminación.

    La clave de ordenamiento es:
    (satisfaction, id)
    """
    def __init__(self):
        self.root: Optional[AVLNode] = None
        self.size = 0

    def height(self, node: Optional[AVLNode]) -> int:
        return 0 if node is None else node.height

    def balance_factor(self, node: Optional[AVLNode]) -> int:
        return 0 if node is None else self.height(node.left) - self.height(node.right)

    def update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(self.height(node.left), self.height(node.right))

    def rotate_right(self, y: AVLNode) -> AVLNode:
        """
        Realiza una rotación simple a la derecha.

        Se utiliza cuando el árbol está desbalanceado
        hacia la izquierda (caso LL).

        Retorna:
        AVLNode: nueva raíz del subárbol
        """
        x = y.left
        t2 = x.right if x else None
        x.right = y
        y.left = t2
        self.update_height(y)
        self.update_height(x)
        return x

    def rotate_left(self, x: AVLNode) -> AVLNode:
        """
        Realiza una rotación simple a la izquierda.

        Se utiliza cuando el árbol está desbalanceado
        hacia la derecha (caso RR).
        """
        y = x.right
        t2 = y.left if y else None
        y.left = x
        x.right = t2
        self.update_height(x)
        self.update_height(y)
        return y

    def rebalance(self, node: AVLNode) -> AVLNode:
        """
        Rebalancea el árbol verificando el factor de balanceo.

        Casos:
        - LL → rotación derecha
        - RR → rotación izquierda
        - LR → rotación izquierda + derecha
        - RL → rotación derecha + izquierda
        """
        self.update_height(node)
        bf = self.balance_factor(node)
        if bf > 1:
            if self.balance_factor(node.left) < 0:
                node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        if bf < -1:
            if self.balance_factor(node.right) > 0:
                node.right = self.rotate_right(node.right)
            return self.rotate_left(node)
        return node

    def insert(self, course: Course) -> None:
        """
        Inserta un curso en el árbol AVL.

        Verifica que no exista otro curso con el mismo ID.
        Luego inserta recursivamente y rebalancea el árbol.
        """
        if self.search_by_id(course.id) is not None:
            raise ValueError(f"Ya existe un curso con id {course.id} en el árbol.")
        self.root = self._insert(self.root, course)
        self.size += 1

    def _insert(self, node: Optional[AVLNode], course: Course) -> AVLNode:
        """
        Función recursiva auxiliar para insertar un nodo.
        (No se llama directamente desde fuera de la clase).
        """
        if node is None:
            return AVLNode(course)
        if course.key() < node.course.key():
            node.left = self._insert(node.left, course)
        else:
            node.right = self._insert(node.right, course)
        return self.rebalance(node)

    def delete_by_id(self, course_id: int) -> bool:
        target = self.search_by_id(course_id)
        if target is None:
            return False
        self.root = self._delete(self.root, target.key())
        self.size -= 1
        return True

    def delete_by_satisfaction(self, satisfaction: float) -> bool:
        matches = self.search_by_satisfaction(satisfaction)
        if not matches:
            return False
        self.root = self._delete(self.root, matches[0].key())
        self.size -= 1
        return True

    def _delete(self, node: Optional[AVLNode], key: tuple[float, int]) -> Optional[AVLNode]:
        """
        Función recursiva auxiliar para eliminar un nodo por su clave.
        """
        if node is None:
            return None
        if key < node.course.key():
            node.left = self._delete(node.left, key)
        elif key > node.course.key():
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            successor = self._min_node(node.right)
            node.course = successor.course
            node.right = self._delete(node.right, successor.course.key())
        return self.rebalance(node)

    def _min_node(self, node: AVLNode) -> AVLNode:
        """
        Retorna el nodo con la clave mínima del subárbol (usado en eliminación).
        """
        current = node
        while current.left is not None:
            current = current.left
        return current

    def search_by_id(self, course_id: int) -> Optional[Course]:
        return self._search_by_id(self.root, course_id)

    def _search_by_id(self, node: Optional[AVLNode], course_id: int) -> Optional[Course]:
        """
        Búsqueda recursiva de un curso por ID.
        """
        if node is None:
            return None
        if node.course.id == course_id:
            return node.course
        left_result = self._search_by_id(node.left, course_id)
        if left_result is not None:
            return left_result
        return self._search_by_id(node.right, course_id)

    def search_node_by_id(self, course_id: int) -> Optional[AVLNode]:
        return self._search_node_by_id(self.root, course_id)

    def _search_node_by_id(self, node: Optional[AVLNode], course_id: int) -> Optional[AVLNode]:
        """
        Búsqueda recursiva que retorna el nodo completo (usado para padre, abuelo, etc.).
        """
        if node is None:
            return None
        if node.course.id == course_id:
            return node
        left_result = self._search_node_by_id(node.left, course_id)
        if left_result is not None:
            return left_result
        return self._search_node_by_id(node.right, course_id)

    def search_by_satisfaction(self, satisfaction: float) -> List[Course]:
        result: List[Course] = []
        target = Utils.round5(satisfaction)
        self._search_by_satisfaction(self.root, target, result)
        return result

    def _search_by_satisfaction(self, node: Optional[AVLNode], target: float, result: List[Course]) -> None:
        """
        Búsqueda recursiva de todos los cursos con el mismo nivel de satisfacción.
        """
        if node is None:
            return
        current = node.course.satisfaction
        if target < current:
            self._search_by_satisfaction(node.left, target, result)
        elif target > current:
            self._search_by_satisfaction(node.right, target, result)
        else:
            self._collect_same_satisfaction(node, target, result)

    def _collect_same_satisfaction(self, node: Optional[AVLNode], target: float, result: List[Course]) -> None:
        """
        Recolecta todos los nodos con exactamente el mismo valor de satisfaction.
        """
        if node is None:
            return
        if node.course.satisfaction == target:
            result.append(node.course)
            self._collect_same_satisfaction(node.left, target, result)
            self._collect_same_satisfaction(node.right, target, result)
        elif target < node.course.satisfaction:
            self._collect_same_satisfaction(node.left, target, result)
        else:
            self._collect_same_satisfaction(node.right, target, result)

    def inorder(self) -> List[Course]:
        result: List[Course] = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node: Optional[AVLNode], result: List[Course]) -> None:
        """
        Recorrido inorder recursivo (usado internamente por inorder()).
        """
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.course)
        self._inorder(node.right, result)

    def level_order_recursive(self) -> List[List[int]]:
        h = self.height(self.root)
        levels: List[List[int]] = []
        for level in range(1, h + 1):
            current: List[int] = []
            self._collect_level(self.root, level, current)
            levels.append(current)
        return levels

    def _collect_level(self, node: Optional[AVLNode], level: int, result: List[int]) -> None:
        """
        Función recursiva auxiliar para recolectar los IDs de un nivel específico.
        """
        if node is None:
            return
        if level == 1:
            result.append(node.course.id)
        else:
            self._collect_level(node.left, level - 1, result)
            self._collect_level(node.right, level - 1, result)

    def filter_courses(self, predicate: Callable[[Course], bool]) -> List[Course]:
        result: List[Course] = []
        self._filter_recursive(self.root, predicate, result)
        return result

    def _filter_recursive(self, node: Optional[AVLNode], predicate: Callable[[Course], bool], result: List[Course]) -> None:
        """
        Función recursiva auxiliar para aplicar cualquier filtro.
        """
        if node is None:
            return
        self._filter_recursive(node.left, predicate, result)
        if predicate(node.course):
            result.append(node.course)
        self._filter_recursive(node.right, predicate, result)

    def filter_positive_greater_than_negative_plus_neutral(self) -> List[Course]:
        """
        Filtro A:
        Retorna cursos donde las reseñas positivas
        son mayores que la suma de negativas y neutrales.
        """
        return self.filter_courses(lambda c: c.positive_reviews > (c.negative_reviews + c.neutral_reviews))

    def filter_created_after(self, date_value: Any) -> List[Course]:
        """
        Filtro B:
        Retorna cursos creados después de una fecha dada.
        """
        target = Utils.parse_date(date_value)
        if target is None:
            raise ValueError("Fecha inválida.")
        return self.filter_courses(lambda c: Utils.parse_date(c.created) is not None and Utils.parse_date(c.created) > target)

    def filter_lectures_in_range(self, minimum: int, maximum: int) -> List[Course]:
        return self.filter_courses(lambda c: minimum <= c.num_published_lectures <= maximum)

    def filter_reviews_above_average(self, review_type: str) -> List[Course]:
        review_type = review_type.lower().strip()
        if review_type not in {"positive", "negative", "neutral"}:
            raise ValueError("Tipo inválido. Debe ser positive, negative o neutral.")
        courses = self.inorder()
        if not courses:
            return []
        attr = f"{review_type}_reviews"
        average = sum(getattr(c, attr) for c in courses) / len(courses)
        return [c for c in courses if getattr(c, attr) > average]

    def get_course_info(self, course_id: int) -> Optional[dict]:
        course = self.search_by_id(course_id)
        return None if course is None else course.to_dict()

    def get_level(self, course_id: int) -> int:
        return self._get_level(self.root, course_id, 0)

    def _get_level(self, node: Optional[AVLNode], course_id: int, level: int) -> int:
        """
        Calcula el nivel del nodo de forma recursiva.
        """
        if node is None:
            return -1
        if node.course.id == course_id:
            return level
        left = self._get_level(node.left, course_id, level + 1)
        if left != -1:
            return left
        return self._get_level(node.right, course_id, level + 1)

    def get_balance_factor_by_id(self, course_id: int) -> Optional[int]:
        node = self.search_node_by_id(course_id)
        if node is None:
            return None
        return self.balance_factor(node)

    def find_parent(self, course_id: int) -> Optional[Course]:
        """
        Encuentra el nodo padre de un curso de forma recursiva.
        """
        return self._find_parent(self.root, course_id)

    def _find_parent(self, node: Optional[AVLNode], course_id: int) -> Optional[Course]:
        """
        Función recursiva auxiliar para encontrar el padre de un nodo.
        """
        if node is None:
            return None
        if node.left and node.left.course.id == course_id:
            return node.course
        if node.right and node.right.course.id == course_id:
            return node.course
        left = self._find_parent(node.left, course_id)
        if left is not None:
            return left
        return self._find_parent(node.right, course_id)

    def find_grandparent(self, course_id: int) -> Optional[Course]:
        parent = self.find_parent(course_id)
        if parent is None:
            return None
        return self.find_parent(parent.id)

    def find_uncle(self, course_id: int) -> Optional[Course]:
        """
        Encuentra el tío de un nodo utilizando su abuelo.
        """
        parent = self.find_parent(course_id)
        if parent is None:
            return None
        grandparent = self.find_parent(parent.id)
        if grandparent is None:
            return None
        grandparent_node = self.search_node_by_id(grandparent.id)
        if grandparent_node is None:
            return None
        if grandparent_node.left and grandparent_node.left.course.id == parent.id:
            return grandparent_node.right.course if grandparent_node.right else None
        if grandparent_node.right and grandparent_node.right.course.id == parent.id:
            return grandparent_node.left.course if grandparent_node.left else None
        return None

    def export_graphviz(self, output_name: str = "avl_tree") -> Optional[str]:
        if not GRAPHVIZ_AVAILABLE:
            raise RuntimeError("No se pudo importar la librería graphviz en Python.")
        dot = Digraph(comment="AVL Tree")
        dot.attr("node", shape="record")
        if self.root is None:
            dot.node("empty", "Árbol vacío")
        else:
            self._add_graphviz_nodes(dot, self.root)
        return dot.render(output_name, format="png", cleanup=True)

    def _add_graphviz_nodes(self, dot: Digraph, node: Optional[AVLNode]) -> None:
        """
        Función recursiva que construye el gráfico Graphviz del árbol.
        """
        if node is None:
            return
        node_id = str(node.course.id)
        label = f"{{ID: {node.course.id}|Título: {node.course.title[:30]}|Satisfaction: {node.course.satisfaction:.5f}}}"
        dot.node(node_id, label)
        if node.left:
            left_id = str(node.left.course.id)
            dot.edge(node_id, left_id)
            self._add_graphviz_nodes(dot, node.left)
        if node.right:
            right_id = str(node.right.course.id)
            dot.edge(node_id, right_id)
            self._add_graphviz_nodes(dot, node.right)


class CourseRepository:
    REQUIRED_COLUMNS = {
        "id", "title", "url", "rating", "num_reviews", "num_published_lectures",
        "created", "last_update_date", "duration", "instructors_id", "image",
        "positive_reviews", "negative_reviews", "neutral_reviews"
    }
    """
    Repositorio que carga y accede al dataset CSV.
    """

    def __init__(self, csv_path: str):
        self.df = self.load_dataframe(csv_path)

    @classmethod
    def load_dataframe(cls, csv_path: str) -> pd.DataFrame:
        df = pd.read_csv(csv_path)
        missing = cls.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Faltan columnas en el CSV: {missing}")
        return df

    def find_course_by_id(self, course_id: int) -> Optional[Course]:
        rows = self.df[self.df["id"] == course_id]
        if rows.empty:
            return None
        return Course.from_row(rows.iloc[0])


class AVLApp(tk.Tk):
    """
    Interfaz gráfica del sistema.

    Permite interactuar con el árbol AVL mediante:
    - Inserciones
    - Eliminaciones
    - Búsquedas
    - Filtros
    - Visualización del árbol
    """
    def __init__(self, csv_path: str):
        super().__init__()
        self.title("Laboratorio AVL - Cursos Udemy")
        self.geometry("1500x900")
        self.minsize(1200, 800)

        self.repository = CourseRepository(csv_path)
        self.tree = AVLCourseTree()
        self.last_results: List[Course] = []
        self.step_counter = 0
        self.current_image_path = None
        self.current_photo = None

        self._build_ui()
        self._set_status("CSV cargado. El árbol inicia vacío.")

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self, padding=10)
        left.grid(row=0, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)

        right = ttk.Frame(self, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        ops = ttk.LabelFrame(left, text="Operaciones principales", padding=10)
        ops.grid(row=0, column=0, sticky="ew", pady=5)
        for i in range(4):
            ops.columnconfigure(i, weight=1)

        ttk.Label(ops, text="ID curso:").grid(row=0, column=0, sticky="w")
        self.id_entry = ttk.Entry(ops)
        self.id_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(ops, text="Insertar por ID", command=self.insert_by_id).grid(row=0, column=2, sticky="ew", padx=5)
        ttk.Button(ops, text="Eliminar por ID", command=self.delete_by_id).grid(row=0, column=3, sticky="ew", padx=5)

        ttk.Label(ops, text="Satisfaction:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.sat_entry = ttk.Entry(ops)
        self.sat_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=(8, 0))
        ttk.Button(ops, text="Buscar por ID", command=self.search_by_id).grid(row=1, column=2, sticky="ew", padx=5, pady=(8, 0))
        ttk.Button(ops, text="Eliminar por Satisfaction", command=self.delete_by_satisfaction).grid(row=1, column=3, sticky="ew", padx=5, pady=(8, 0))
        ttk.Button(ops, text="Buscar por Satisfaction", command=self.search_by_satisfaction).grid(row=2, column=2, sticky="ew", padx=5, pady=(8, 0))
        ttk.Button(ops, text="Recorrido por niveles", command=self.show_levels).grid(row=2, column=3, sticky="ew", padx=5, pady=(8, 0))

        filters = ttk.LabelFrame(left, text="Filtros", padding=10)
        filters.grid(row=1, column=0, sticky="ew", pady=5)
        for i in range(4):
            filters.columnconfigure(i, weight=1)

        ttk.Button(filters, text="Filtro A", command=self.filter_a).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(filters, text="Fecha >").grid(row=0, column=1, sticky="e")
        self.date_entry = ttk.Entry(filters)
        self.date_entry.grid(row=0, column=2, sticky="ew", padx=5)
        ttk.Button(filters, text="Filtro B", command=self.filter_b).grid(row=0, column=3, sticky="ew", padx=5)

        ttk.Label(filters, text="Min clases").grid(row=1, column=0, sticky="e")
        self.min_lect_entry = ttk.Entry(filters)
        self.min_lect_entry.grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Label(filters, text="Max clases").grid(row=1, column=2, sticky="e")
        self.max_lect_entry = ttk.Entry(filters)
        self.max_lect_entry.grid(row=1, column=3, sticky="ew", padx=5)
        ttk.Button(filters, text="Filtro C", command=self.filter_c).grid(row=2, column=3, sticky="ew", padx=5, pady=5)

        ttk.Label(filters, text="Tipo reseña").grid(row=2, column=0, sticky="e")
        self.review_type = ttk.Combobox(filters, values=["positive", "negative", "neutral"], state="readonly")
        self.review_type.grid(row=2, column=1, sticky="ew", padx=5)
        self.review_type.set("positive")
        ttk.Button(filters, text="Filtro D", command=self.filter_d).grid(row=2, column=2, sticky="ew", padx=5, pady=5)

        middle = ttk.PanedWindow(left, orient="vertical")
        middle.grid(row=2, column=0, sticky="nsew", pady=5)

        results_frame = ttk.LabelFrame(middle, text="Resultados", padding=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        self.results_list = tk.Listbox(results_frame, height=10)
        self.results_list.grid(row=0, column=0, sticky="nsew")
        self.results_list.bind("<<ListboxSelect>>", self.on_select_result)
        scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_list.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.results_list.config(yscrollcommand=scroll.set)
        middle.add(results_frame, weight=1)

        details = ttk.LabelFrame(middle, text="Detalles del nodo seleccionado", padding=10)
        details.columnconfigure(0, weight=1)
        details.rowconfigure(0, weight=1)

        self.details_text = tk.Text(details, height=16, wrap="word")
        self.details_text.grid(row=0, column=0, sticky="nsew")
        self.details_text.config(state="disabled")
        middle.add(details, weight=1)

        extras = ttk.Frame(left)
        extras.grid(row=3, column=0, sticky="ew", pady=5)
        extras.columnconfigure(0, weight=1)
        extras.columnconfigure(1, weight=1)
        extras.columnconfigure(2, weight=1)

        ttk.Button(extras, text="Exportar imagen manual", command=self.export_manual_image).grid(row=0, column=0, sticky="ew", padx=5)
        ttk.Button(extras, text="Refrescar imagen", command=self.refresh_image).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(extras, text="Limpiar resultados", command=self.clear_results).grid(row=0, column=2, sticky="ew", padx=5)

        self.status_var = tk.StringVar(value="Listo.")
        ttk.Label(left, textvariable=self.status_var, relief="sunken", anchor="w").grid(row=4, column=0, sticky="ew", pady=(10, 0))

        img_frame = ttk.LabelFrame(right, text="Visualización del árbol AVL", padding=10)
        img_frame.grid(row=0, column=0, sticky="nsew")
        img_frame.columnconfigure(0, weight=1)
        img_frame.rowconfigure(0, weight=1)

        self.image_label = ttk.Label(img_frame, text="Todavía no se ha generado ninguna imagen.")
        self.image_label.grid(row=0, column=0, sticky="nsew")

    def _set_status(self, text: str):
        self.status_var.set(text)

    def _update_results(self, courses: List[Course]):
        self.last_results = courses
        self.results_list.delete(0, tk.END)
        for course in courses:
            self.results_list.insert(tk.END, course.summary())
        self._set_status(f"Resultados encontrados: {len(courses)}")

    def _show_details(self, text: str):
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, text)
        self.details_text.config(state="disabled")

    def _show_course_details(self, course: Course):
        info = self.tree.get_course_info(course.id)
        if info is None:
            self._show_details("El curso no está en el árbol.")
            return
        parent = self.tree.find_parent(course.id)
        grandparent = self.tree.find_grandparent(course.id)
        uncle = self.tree.find_uncle(course.id)
        lines = [f"{k}: {v}" for k, v in info.items()]
        lines.append("")
        lines.append(f"Nivel del nodo: {self.tree.get_level(course.id)}")
        lines.append(f"Factor de balanceo: {self.tree.get_balance_factor_by_id(course.id)}")
        lines.append(f"Padre: {parent.id if parent else None}")
        lines.append(f"Abuelo: {grandparent.id if grandparent else None}")
        lines.append(f"Tío: {uncle.id if uncle else None}")
        self._show_details("\n".join(lines))

    def _export_step_image(self, operation_name: str):
        self.step_counter += 1
        filename = f"paso_{self.step_counter}_{operation_name}"
        path = self.tree.export_graphviz(filename)
        self.current_image_path = path
        self.refresh_image()
        self._set_status(f"Imagen generada: {path}")

    def insert_by_id(self):
        """
        Operación 1 de la rúbrica: Insertar un nodo mediante el ID.
        Carga el curso del CSV, lo inserta en el AVL y genera la imagen.
        """
        try:
            course_id = int(self.id_entry.get().strip())
            course = self.repository.find_course_by_id(course_id)
            if course is None:
                messagebox.showwarning("Aviso", "Ese ID no existe en el dataset.")
                return
            self.tree.insert(course)
            self._update_results([course])
            self._show_course_details(course)
            self._export_step_image("insertar")
            messagebox.showinfo("Éxito", "Curso insertado correctamente.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_by_id(self):
        """
        Operación 2 de la rúbrica: Eliminar un nodo utilizando el ID.
        """
        try:
            course_id = int(self.id_entry.get().strip())
            if not self.tree.delete_by_id(course_id):
                messagebox.showwarning("Aviso", "Ese ID no existe en el árbol.")
                return
            self._export_step_image("eliminar_id")
            self._show_details("Nodo eliminado correctamente.")
            messagebox.showinfo("Éxito", "Nodo eliminado correctamente.")
        except ValueError:
            messagebox.showerror("Error", "Ingresa un ID válido.")

    def delete_by_satisfaction(self):
        """
        Operación 2 de la rúbrica: Eliminar un nodo utilizando el nivel de satisfacción.
        """
        try:
            satisfaction = float(self.sat_entry.get().strip())
            if not self.tree.delete_by_satisfaction(satisfaction):
                messagebox.showwarning("Aviso", "Ese satisfaction no existe en el árbol.")
                return
            self._export_step_image("eliminar_satisfaction")
            self._show_details("Nodo eliminado por satisfaction.")
            messagebox.showinfo("Éxito", "Nodo eliminado correctamente.")
        except ValueError:
            messagebox.showerror("Error", "Ingresa un satisfaction válido.")

    def search_by_id(self):
        """
        Operación 3 de la rúbrica: Buscar un nodo utilizando el ID.
        """
        try:
            course_id = int(self.id_entry.get().strip())
            course = self.tree.search_by_id(course_id)
            if course is None:
                self._update_results([])
                self._show_details("Curso no encontrado en el árbol.")
                return
            self._update_results([course])
            self._show_course_details(course)
        except ValueError:
            messagebox.showerror("Error", "Ingresa un ID válido.")

    def search_by_satisfaction(self):
        """
        Operación 3 de la rúbrica: Buscar un nodo utilizando el nivel de satisfacción.
        """
        try:
            satisfaction = float(self.sat_entry.get().strip())
            results = self.tree.search_by_satisfaction(satisfaction)
            self._update_results(results)
            if results:
                self._show_course_details(results[0])
            else:
                self._show_details("No se encontraron cursos con ese satisfaction.")
        except ValueError:
            messagebox.showerror("Error", "Ingresa un satisfaction válido.")

    def filter_a(self):
        """
        Filtro A de la rúbrica: positive_reviews > negative_reviews + neutral_reviews.
        """
        results = self.tree.filter_positive_greater_than_negative_plus_neutral()
        self._update_results(results)
        self._show_details("Filtro A aplicado. Selecciona un curso de la lista.")

    def filter_b(self):
        """
        Filtro B de la rúbrica: cursos creados después de una fecha dada.
        """
        try:
            results = self.tree.filter_created_after(self.date_entry.get().strip())
            self._update_results(results)
            self._show_details("Filtro B aplicado. Selecciona un curso de la lista.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def filter_c(self):
        """
        Filtro C de la rúbrica: cantidad de clases dentro de un rango dado.
        """
        try:
            minimum = int(self.min_lect_entry.get().strip())
            maximum = int(self.max_lect_entry.get().strip())
            results = self.tree.filter_lectures_in_range(minimum, maximum)
            self._update_results(results)
            self._show_details("Filtro C aplicado. Selecciona un curso de la lista.")
        except ValueError:
            messagebox.showerror("Error", "Ingresa un rango válido de clases.")

    def filter_d(self):
        """
        Filtro D de la rúbrica: reseñas superiores al promedio de todos los nodos del árbol.
        """
        try:
            results = self.tree.filter_reviews_above_average(self.review_type.get().strip())
            self._update_results(results)
            self._show_details("Filtro D aplicado. Selecciona un curso de la lista.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_levels(self):
        """
        Operación 5 de la rúbrica: Mostrar recorrido por niveles (recursivo).
        """
        levels = self.tree.level_order_recursive()
        if not levels:
            self._show_details("El árbol está vacío.")
            return
        lines = ["Recorrido por niveles:"]
        for i, ids in enumerate(levels):
            lines.append(f"Nivel {i}: {ids}")
        self._show_details("\n".join(lines))

    def on_select_result(self, event=None):
        """
        Al seleccionar un curso de la lista, muestra padre, abuelo, tío,
        nivel, factor de balanceo y toda la información del nodo.
        """
        selection = self.results_list.curselection()
        if not selection:
            return
        idx = selection[0]
        if 0 <= idx < len(self.last_results):
            self._show_course_details(self.last_results[idx])

    def export_manual_image(self):
        """Genera manualmente la imagen del árbol AVL con Graphviz."""
        try:
            filename = f"arbol_manual_{self.step_counter + 1}"
            path = self.tree.export_graphviz(filename)
            self.current_image_path = path
            self.refresh_image()
            messagebox.showinfo("Éxito", f"Imagen exportada en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_image(self):
        """Actualiza la imagen que se muestra en la interfaz gráfica."""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            self.image_label.configure(text="No hay imagen disponible todavía.", image="")
            self.current_photo = None
            return
        try:
            photo = tk.PhotoImage(file=self.current_image_path)
            self.current_photo = photo
            self.image_label.configure(image=photo, text="")
        except Exception:
            self.image_label.configure(
                text=f"Imagen generada en:\n{self.current_image_path}\n\nÁbrela desde la carpeta del proyecto si no se muestra aquí.",
                image=""
            )
            self.current_photo = None

    def clear_results(self):
        """Limpia la lista de resultados y los detalles."""
        self.last_results = []
        self.results_list.delete(0, tk.END)
        self._show_details("")
        self._set_status("Resultados limpiados.")


def main():
    app = AVLApp("dataset_courses_with_reviews.csv")
    app.mainloop()


if __name__ == "__main__":
    main()
