from lexer import tokenizar, Token, TipoToken
from ast_nodes import (
    Nodo, NodoPrograma, NodoAsignacion, NodoMostrar,
    NodoOperacionBinaria, NodoNegacion, NodoNumero, NodoIdentificador
)


class ErrorSintactico(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos    = 0

    # ── Helpers de navegación ─────────────────────────────────────────────────

    def _actual(self) -> Token:
        return self.tokens[self.pos]

    def _consumir(self, tipo: TipoToken) -> Token:
        """
        Verifica que el token actual sea del tipo esperado,
        lo retorna y avanza al siguiente.
        """
        tok = self._actual()
        if tok.tipo != tipo:
            raise ErrorSintactico(
                f"[Parser] Línea {tok.linea}: "
                f"se esperaba '{tipo.name}' pero se encontró '{tok.tipo.name}' ({tok.valor!r})"
            )
        self.pos += 1
        return tok

    def _revisar(self, *tipos: TipoToken) -> bool:
        """Retorna True si el token actual es uno de los tipos dados."""
        return self._actual().tipo in tipos

    # ── Reglas de la gramática ────────────────────────────────────────────────

    def parsear_programa(self) -> NodoPrograma:
        """programa → sentencia+"""
        sentencias = []

        while not self._revisar(TipoToken.FIN):
            sentencias.append(self._parsear_sentencia())

        if not sentencias:
            raise ErrorSintactico("[Parser] El programa está vacío.")

        return NodoPrograma(sentencias)

    def _parsear_sentencia(self) -> Nodo:
        """sentencia → asignacion | mostrar"""
        tok = self._actual()

        if tok.tipo == TipoToken.MOSTRAR:
            return self._parsear_mostrar()

        if tok.tipo == TipoToken.IDENTIFICADOR:
            return self._parsear_asignacion()

        raise ErrorSintactico(
            f"[Parser] Línea {tok.linea}: "
            f"sentencia inválida, token inesperado '{tok.valor}'"
        )

    def _parsear_asignacion(self) -> NodoAsignacion:
        """asignacion → IDENTIFICADOR "=" expresion"""
        tok_nombre = self._consumir(TipoToken.IDENTIFICADOR)
        self._consumir(TipoToken.IGUAL)
        expresion = self._parsear_expresion()
        return NodoAsignacion(tok_nombre.valor, expresion)

    def _parsear_mostrar(self) -> NodoMostrar:
        """mostrar → "MOSTRAR" IDENTIFICADOR"""
        self._consumir(TipoToken.MOSTRAR)
        tok_nombre = self._consumir(TipoToken.IDENTIFICADOR)
        return NodoMostrar(tok_nombre.valor)

    def _parsear_expresion(self) -> Nodo:
        """expresion → termino ( ("+" | "-") termino )*"""
        nodo = self._parsear_termino()

        while self._revisar(TipoToken.MAS, TipoToken.MENOS):
            operador = self._actual().valor
            self.pos += 1
            derecha  = self._parsear_termino()
            nodo     = NodoOperacionBinaria(operador, nodo, derecha)

        return nodo

    def _parsear_termino(self) -> Nodo:
        """termino → factor ( ("*" | "/") factor )*"""
        nodo = self._parsear_factor()

        while self._revisar(TipoToken.MULT, TipoToken.DIV, TipoToken.LPAREN, TipoToken.IDENTIFICADOR):
            
            if self._revisar(TipoToken.LPAREN, TipoToken.IDENTIFICADOR):
                operador = '*'
                derecha = self._parsear_factor()
            else:
                operador = self._actual().valor
                self.pos += 1
                derecha = self._parsear_factor()
            
            nodo = NodoOperacionBinaria(operador, nodo, derecha)

        return nodo
    def _parsear_factor(self) -> Nodo:
        """factor → NUMERO | IDENTIFICADOR | "(" expresion ")" | "-" factor"""
        tok = self._actual()

        # Número literal
        if tok.tipo == TipoToken.NUMERO:
            self.pos += 1
            valor = float(tok.valor)
            # Guardar como entero si no tiene decimales, para mejor lectura
            return NodoNumero(int(valor) if valor == int(valor) else valor)

        # Variable
        if tok.tipo == TipoToken.IDENTIFICADOR:
            self.pos += 1
            return NodoIdentificador(tok.nombre if hasattr(tok, 'nombre') else tok.valor)

        # Expresión entre paréntesis
        if tok.tipo == TipoToken.LPAREN:
            self._consumir(TipoToken.LPAREN)
            nodo = self._parsear_expresion()
            self._consumir(TipoToken.RPAREN)
            return nodo

        # Negación unaria
        if tok.tipo == TipoToken.MENOS:
            self.pos += 1
            operando = self._parsear_factor()
            return NodoNegacion(operando)

        raise ErrorSintactico(
            f"[Parser] Línea {tok.linea}: "
            f"factor inválido, token inesperado '{tok.valor}'"
        )


# ─── Función de conveniencia ──────────────────────────────────────────────────

def parsear(codigo: str) -> NodoPrograma:
    tokens = tokenizar(codigo)
    return Parser(tokens).parsear_programa()


# ─── Test rápido ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    codigo = """
# Programa de prueba
x = 3 + 4
y = 2 * (x - 1)
z = y / 3.5
MOSTRAR z
"""
    ast = parsear(codigo)
    print("AST generado:")
    print(ast)
    print()
    for s in ast.sentencias:
        print(" ", s)