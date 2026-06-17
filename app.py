import streamlit as st
import graphviz
import os
from lexer import tokenizar, Lexer, TipoToken
from parser import Parser, ErrorSintactico
from ast_nodes import (
    Nodo, NodoPrograma, NodoAsignacion, NodoMostrar,
    NodoOperacionBinaria, NodoNegacion, NodoNumero, NodoIdentificador
)


IMG_SALUDO = "paco_saludando.png"
IMG_FELIZ = "paco_feliz.png"
IMG_PENSANDO = "paco_pensando.png"

def cargar_paco(ruta_imagen, ancho=120):
    """Muestra la imagen si existe, si no, deja un espacio reservado."""
    if os.path.exists(ruta_imagen):
        st.image(ruta_imagen, width=ancho)
    else:
        st.info(f"🖼️ [Falta: {ruta_imagen}]")



class EvaluadorExplicativo:
    def __init__(self):
        self.variables = {}
        self.pasos = []

    def evaluar(self, nodo: Nodo):
        if isinstance(nodo, NodoPrograma):
            for sentencia in nodo.sentencias:
                self.evaluar(sentencia)
            return self.variables

        elif isinstance(nodo, NodoAsignacion):
            valor = self.evaluar(nodo.expresion)
            self.variables[nodo.nombre] = valor
            return valor

        elif isinstance(nodo, NodoNumero):
            return nodo.valor

        elif isinstance(nodo, NodoNegacion):
            val = self.evaluar(nodo.operando)
            resultado = -val
            self.pasos.append(f"Primero, cambiamos el signo de **{val}** y se convierte en **{resultado}**.")
            return resultado

        elif isinstance(nodo, NodoOperacionBinaria):
            izq = self.evaluar(nodo.izquierda)
            der = self.evaluar(nodo.derecha)
            
            if nodo.operador == '+': resultado = izq + der
            elif nodo.operador == '-': resultado = izq - der
            elif nodo.operador == '*': resultado = izq * der
            elif nodo.operador == '/': 
                if der == 0: raise ZeroDivisionError("División por cero")
                resultado = izq / der
            
            res_fmt = int(resultado) if resultado == int(resultado) else round(resultado, 2)
            
            if nodo.operador == '+': op_texto = "sumamos"
            elif nodo.operador == '-': op_texto = "restamos"
            elif nodo.operador == '*': op_texto = "multiplicamos"
            elif nodo.operador == '/': op_texto = "dividimos"
            
            self.pasos.append(f"Luego, {op_texto}: **{izq} {nodo.operador} {der}**. ¡Esto nos da **{res_fmt}**!")
            return resultado



def generar_grafo_ast(nodo: Nodo, dot=None) -> graphviz.Digraph:
    if dot is None:
        dot = graphviz.Digraph(comment='AST de MatExp')
        dot.attr(bgcolor='transparent', rankdir='TB')
        dot.attr('node', shape='rect', style='filled,rounded', fontcolor='white', fontname='Comic Sans MS, Helvetica', penwidth='0', margin='0.3')
        dot.attr('edge', color='#FF9F43', arrowhead='vee', arrowsize='1.2', penwidth='3')

    id_nodo = str(id(nodo))

    if isinstance(nodo, NodoPrograma):
        dot.node(id_nodo, "¡TU RETO!", fillcolor="#20BF6B", fontsize='16')
        for sent in nodo.sentencias:
            if isinstance(sent, NodoAsignacion):
                generar_grafo_ast(sent.expresion, dot)
                dot.edge(id_nodo, str(id(sent.expresion)))
            else:
                generar_grafo_ast(sent, dot)
                dot.edge(id_nodo, str(id(sent)))

    elif isinstance(nodo, NodoOperacionBinaria):
        dot.node(id_nodo, f" {nodo.operador} ", fillcolor="#EB3B5A", shape="circle")
        id_izq = str(id(nodo.izquierda))
        id_der = str(id(nodo.derecha))
        generar_grafo_ast(nodo.izquierda, dot)
        generar_grafo_ast(nodo.derecha, dot)
        dot.edge(id_nodo, id_izq)
        dot.edge(id_nodo, id_der)

    elif isinstance(nodo, NodoNegacion):
        dot.node(id_nodo, "Sorpresa (-)", fillcolor="#8854D0")
        id_op = str(id(nodo.operando))
        generar_grafo_ast(nodo.operando, dot)
        dot.edge(id_nodo, id_op)

    elif isinstance(nodo, NodoNumero):
        dot.node(id_nodo, str(nodo.valor), fillcolor="#2D98DA", shape="circle")

    return dot



st.set_page_config(page_title="MatExp - ¡Aventura Matemática!", layout="centered", page_icon="🦙")

col_saludo1, col_saludo2 = st.columns([1, 4])
with col_saludo1:
    cargar_paco(IMG_SALUDO, ancho=130)
with col_saludo2:
    st.title("¡Aventura Matemática!")
    st.write("¡Hola! Soy **Paco la Alpaca**. Inventa un problema matemático genial, intenta adivinar el resultado y yo te ayudaré a descubrir si acertaste. ¡A jugar!")

st.markdown("---")


formula_usuario = st.text_input("1️⃣ Escribe tu misión matemática aquí:", placeholder="Ejemplo: 3 + 5 * (10 - 2)")

if formula_usuario.strip():
    respuesta_usuario = st.number_input("2️⃣ ¿Cuál crees que es el número mágico (resultado)?", step=1.0, value=0.0)
    
    if st.button("🚀 ¡Revisar mi misión!"):
        try:
            codigo_sintetico = f"resultado = {formula_usuario}"
            tokens = tokenizar(codigo_sintetico)
            parser = Parser(tokens)
            ast = parser.parsear_programa()
            
            evaluador = EvaluadorExplicativo()
            variables = evaluador.evaluar(ast)
            resultado_calculado = variables.get("resultado")
            
            st.markdown("---")
            
            # EVALUACIÓN CORRECTA (PACO FELIZ)
            if float(respuesta_usuario) == float(resultado_calculado):
                col_feliz1, col_feliz2 = st.columns([1, 4])
                with col_feliz1:
                    cargar_paco(IMG_FELIZ, ancho=130)
                with col_feliz2:
                    st.success(f"### ¡Wohooo! ¡Eres un genio!\nTu respuesta es **SÚPER CORRECTA**. El resultado mágico es **{resultado_calculado}**. ¡Choca esos cinco! ✋")
                st.balloons()
            
            else:
                col_pen1, col_pen2 = st.columns([1, 4])
                with col_pen1:
                    cargar_paco(IMG_PENSANDO, ancho=130)
                with col_pen2:
                    st.warning(f"### ¡Uy! Estuviste cerquita...\nMe dijiste **{respuesta_usuario}**, pero el número escondido era **{resultado_calculado}**. ¡No te preocupes! Vamos a resolverlo juntos como un rompecabezas:")
                
                st.markdown("### 🧩 Los pasos mágicos:")
                for paso in evaluador.pasos:
                    st.info(f"✨ {paso}")
                
                st.markdown("### 🌳 El Árbol de nuestro problema:")
                st.write("Mira cómo dividimos tu misión. ¡Siempre empezamos resolviendo las bolitas que están más abajo en el árbol!")
                grafo = generar_grafo_ast(ast)
                st.graphviz_chart(grafo)

        except ErrorSintactico as es:
            st.error("🛑 **¡Paco está confundido!** Parece que pusiste símbolos juntos o te olvidaste de cerrar un paréntesis. ¡Revisa tu misión!")
        except ZeroDivisionError:
            st.error("🛑 **¡Oh no!** Intentaste dividir entre cero, ¡y eso rompe las reglas de las matemáticas!")
        except Exception as e:
            st.error(f"¡Ups! Ocurrió algo raro: {e}")