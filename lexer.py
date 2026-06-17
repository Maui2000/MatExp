from dataclasses import dataclass
from enum import Enum, auto


# ─── Tipos de token ───────────────────────────────────────────────────────────

class TipoToken(Enum):
    # Literales
    NUMERO       = auto()   # 3, 4.5, 100
    IDENTIFICADOR = auto()  # x, resultado, num1

    # Palabra clave
    MOSTRAR      = auto()   # MOSTRAR

    # Operadores
    MAS          = auto()   # +
    MENOS        = auto()   # -
    MULT         = auto()   # *
    DIV          = auto()   # /

    # Agrupación y asignación
    LPAREN       = auto()   # (
    RPAREN       = auto()   # )
    IGUAL        = auto()   # =

    # Control
    FIN          = auto()   # fin del archivo


# ─── Estructura de un token ───────────────────────────────────────────────────

@dataclass
class Token:
    tipo:   TipoToken
    valor:  str
    linea:  int

    def __repr__(self):
        return f"Token({self.tipo.name}, {self.valor!r}, linea={self.linea})"


# ─── Palabras reservadas ──────────────────────────────────────────────────────

PALABRAS_CLAVE = {
    "MOSTRAR": TipoToken.MOSTRAR,
}


# ─── Lexer ────────────────────────────────────────────────────────────────────

class Lexer:
    def __init__(self, codigo: str):
        self.codigo  = codigo
        self.pos     = 0          # posición actual en el string
        self.linea   = 1          # línea actual (para mensajes de error)
        self.tokens  = []

    # ── Helpers de navegación ─────────────────────────────────────────────────

    def _actual(self) -> str:
        """Retorna el carácter actual sin avanzar."""
        if self.pos < len(self.codigo):
            return self.codigo[self.pos]
        return ""

    def _avanzar(self) -> str:
        """Retorna el carácter actual y avanza la posición."""
        c = self.codigo[self.pos]
        self.pos += 1
        if c == "\n":
            self.linea += 1
        return c

    def _saltar_espacios(self):
        """Salta espacios, tabs y saltos de línea."""
        while self.pos < len(self.codigo) and self._actual() in " \t\r\n":
            self._avanzar()

    def _saltar_comentario(self):
        """Salta todo hasta el fin de la línea."""
        while self.pos < len(self.codigo) and self._actual() != "\n":
            self._avanzar()

    # ── Lectura de tokens compuestos ──────────────────────────────────────────

    def _leer_numero(self) -> Token:
        """Lee un entero o decimal."""
        inicio = self.pos
        linea  = self.linea

        while self.pos < len(self.codigo) and self._actual().isdigit():
            self._avanzar()

        # parte decimal
        if self._actual() == "." and self.pos + 1 < len(self.codigo) and self.codigo[self.pos + 1].isdigit():
            self._avanzar()  # consume el punto
            while self.pos < len(self.codigo) and self._actual().isdigit():
                self._avanzar()

        valor = self.codigo[inicio:self.pos]
        return Token(TipoToken.NUMERO, valor, linea)

    def _leer_identificador(self) -> Token:
        """Lee un identificador o palabra clave."""
        inicio = self.pos
        linea  = self.linea

        while self.pos < len(self.codigo) and (self._actual().isalnum() or self._actual() == "_"):
            self._avanzar()

        valor = self.codigo[inicio:self.pos]
        tipo  = PALABRAS_CLAVE.get(valor, TipoToken.IDENTIFICADOR)
        return Token(tipo, valor, linea)

    # ── Tokenización principal ────────────────────────────────────────────────

    def tokenizar(self) -> list[Token]:
        """
        Recorre todo el código fuente y retorna la lista de tokens.
        Lanza un ValueError si encuentra un carácter inesperado.
        """
        tokens = []

        while self.pos < len(self.codigo):
            self._saltar_espacios()

            if self.pos >= len(self.codigo):
                break

            c = self._actual()

            # Comentarios
            if c == "#":
                self._saltar_comentario()
                continue

            # Número
            if c.isdigit():
                tokens.append(self._leer_numero())
                continue

            # Identificador o palabra clave
            if c.isalpha() or c == "_":
                tokens.append(self._leer_identificador())
                continue

            # Operadores y símbolos de un carácter
            self._avanzar()  # consume el carácter
            linea = self.linea

            if   c == "+": tokens.append(Token(TipoToken.MAS,    c, linea))
            elif c == "-": tokens.append(Token(TipoToken.MENOS,  c, linea))
            elif c == "*": tokens.append(Token(TipoToken.MULT,   c, linea))
            elif c == "/": tokens.append(Token(TipoToken.DIV,    c, linea))
            elif c == "(": tokens.append(Token(TipoToken.LPAREN, c, linea))
            elif c == ")": tokens.append(Token(TipoToken.RPAREN, c, linea))
            elif c == "=": tokens.append(Token(TipoToken.IGUAL,  c, linea))
            else:
                raise ValueError(
                    f"[Lexer] Carácter inesperado '{c}' en la línea {self.linea}"
                )

        tokens.append(Token(TipoToken.FIN, "", self.linea))
        return tokens


# ─── Función de conveniencia ──────────────────────────────────────────────────

def tokenizar(codigo: str) -> list[Token]:
    return Lexer(codigo).tokenizar()


# ─── Test rápido ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    codigo = """
# Programa de prueba
x = 3 + 4
y = 2 * (x - 1)
z = y / 3.5
MOSTRAR z
"""
    for tok in tokenizar(codigo):
        print(tok)