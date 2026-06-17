from dataclasses import dataclass, field
from typing import Union


# ─── Nodo base ────────────────────────────────────────────────────────────────

class Nodo:
    """Clase base de todos los nodos del AST."""
    pass


# ─── Nodos hoja (terminales) ──────────────────────────────────────────────────

@dataclass
class NodoNumero(Nodo):
    """Representa un literal numérico: 3, 4.5, etc."""
    valor: float

    def __repr__(self):
        return f"Numero({self.valor})"


@dataclass
class NodoIdentificador(Nodo):
    """Representa una variable: x, resultado, num1, etc."""
    nombre: str

    def __repr__(self):
        return f"Ident({self.nombre})"


# ─── Nodos internos (no terminales) ──────────────────────────────────────────

@dataclass
class NodoOperacionBinaria(Nodo):
    """
    Representa una operación entre dos expresiones.
    Operador puede ser: '+', '-', '*', '/'
    """
    operador: str
    izquierda: Nodo
    derecha: Nodo

    def __repr__(self):
        return f"OpBin({self.izquierda} {self.operador} {self.derecha})"


@dataclass
class NodoNegacion(Nodo):
    """Representa un negativo unario: -x, -(3+2), etc."""
    operando: Nodo

    def __repr__(self):
        return f"Neg({self.operando})"


# ─── Nodos de sentencia ───────────────────────────────────────────────────────

@dataclass
class NodoAsignacion(Nodo):
    """
    Representa una asignación: x = 3 + 4
    """
    nombre: str       # nombre de la variable
    expresion: Nodo   # árbol de la expresión del lado derecho

    def __repr__(self):
        return f"Asignacion({self.nombre} = {self.expresion})"


@dataclass
class NodoMostrar(Nodo):
    """
    Representa la instrucción: MOSTRAR x
    """
    nombre: str       # nombre de la variable a mostrar

    def __repr__(self):
        return f"Mostrar({self.nombre})"


# ─── Nodo raíz ────────────────────────────────────────────────────────────────

@dataclass
class NodoPrograma(Nodo):
    """
    Nodo raíz del AST. Contiene la lista de sentencias del programa.
    """
    sentencias: list[Nodo] = field(default_factory=list)

    def __repr__(self):
        return f"Programa({len(self.sentencias)} sentencias)"