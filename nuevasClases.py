# coding: utf-8
from dataclasses import dataclass, field
from typing import List

from collections import Counter

from Context import Context
from Exceptions import *


DEFAULT_CAST = 'Object'
NULL = '_no_type'



@dataclass
class Nodo:
    linea: int

    def str(self, n):
        return f'{n*" "}#{self.linea}\n'


@dataclass
class Formal(Nodo):
    nombre_variable: str
    tipo: str
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_formal\n'
        resultado += f'{(n+2)*" "}{self.nombre_variable}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        return resultado


class Expresion(Nodo):
    cast: str


@dataclass
class Asignacion(Expresion):
    nombre: str
    cuerpo: Expresion

    def Tipo(self, ctx: Context) -> None:
        if self.nombre == 'self':
            raise SELF_ASSIGNMENT(self.cuerpo.linea)
        tipo = ctx.get_variable_type(self.nombre)
        if not tipo:
            raise UNDECLARED_ID(self.cuerpo.linea, self.nombre)
        self.cuerpo.Tipo(ctx)
        if not ctx.inherits_from(self.cuerpo.cast, tipo):
            raise ASSIGN_TYPE_ERROR(self.cuerpo.linea, self.cuerpo.cast, tipo, self.nombre)
        self.cast = self.cuerpo.cast

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_assign\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class LlamadaMetodoEstatico(Expresion):
    cuerpo: Expresion
    clase: str
    nombre_metodo: str
    argumentos: List[Expresion]

    def Tipo(self, ctx: Context) -> None:
        self.cuerpo.Tipo(ctx)
        for arg in self.argumentos:
            arg.Tipo(ctx)
        if not ctx.inherits_from(self.cuerpo.cast, self.clase):
            raise EXPR_NOT_CONFORM(self.cuerpo.linea, self.cuerpo.cast, self.clase)
        ctx.check_method(
            self.linea, self.clase, self.nombre_metodo, 
            [arg.cast for arg in self.argumentos])
        metType = ctx.get_method_type(self.cuerpo.cast, self.nombre_metodo)
        self.cast = self.cuerpo.cast if metType == 'SELF_TYPE' else metType

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_static_dispatch\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n+2)*" "}{self.clase}\n'
        resultado += f'{(n+2)*" "}{self.nombre_metodo}\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.argumentos])
        resultado += f'{(n+2)*" "})\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class LlamadaMetodo(Expresion):
    cuerpo: Expresion
    nombre_metodo: str
    argumentos: List[Expresion]

    def Tipo(self, ctx: Context) -> None:
        self.cuerpo.Tipo(ctx)
        for arg in self.argumentos:
            arg.Tipo(ctx)
        clase = self.cuerpo.cast
        ctx.check_method(
            self.linea, clase, self.nombre_metodo,
            [arg.cast for arg in self.argumentos])
        metType = ctx.get_method_type(self.cuerpo.cast, self.nombre_metodo)
        self.cast = self.cuerpo.cast if metType == 'SELF_TYPE' else metType

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_dispatch\n'
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n+2)*" "}{self.nombre_metodo}\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.argumentos])
        resultado += f'{(n+2)*" "})\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Condicional(Expresion):
    condicion: Expresion
    verdadero: Expresion
    falso: Expresion

    def Tipo(self, ctx: Context) -> None:
        self.condicion.Tipo(ctx)
        self.verdadero.Tipo(ctx)
        self.falso.Tipo(ctx)
        if self.condicion.cast != 'Bool':
            raise INCORRECT_LOOP_CONDITION(self.condicion.linea)
        self.cast = ctx.get_common_ancestor([self.verdadero.cast, self.falso.cast])

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_cond\n'
        resultado += self.condicion.str(n+2)
        resultado += self.verdadero.str(n+2)
        resultado += self.falso.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Bucle(Expresion):
    condicion: Expresion
    cuerpo: Expresion

    def Tipo(self, ctx: Context) -> None:
        self.condicion.Tipo(ctx)
        self.cuerpo.Tipo(ctx)
        if self.condicion.cast != 'Bool':
            raise INCORRECT_LOOP_CONDITION(self.condicion.linea)
        self.cast = 'Object'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_loop\n'
        resultado += self.condicion.str(n+2)
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Let(Expresion):
    nombre: str
    tipo: str
    inicializacion: Expresion
    cuerpo: Expresion

    def Tipo(self, ctx: Context) -> None:
        # TODO Check nombre en scope y cuerpo igual al tipo
        # Ir metiendo en el scope
        ctx.add_let_scope({ self.nombre:self.tipo })
        self.inicializacion.Tipo(ctx)
        self.cuerpo.Tipo(ctx)
        ctx.exit_scope()
        if self.nombre == 'self':
            raise NOT_BOUNDABLE_IN_LET(self.linea)
        if self.inicializacion.cast != NULL:
            if not ctx.inherits_from(self.inicializacion.cast, self.tipo):
                raise INITIALIZATION_NOT_CONFORM(self.inicializacion.linea,self.inicializacion.cast, self.nombre, self.tipo)
        self.cast = self.cuerpo.cast

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_let\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.inicializacion.str(n+2)
        resultado += self.cuerpo.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Bloque(Expresion):
    expresiones: List[Expresion]

    def Tipo(self, ctx: Context) -> None:
        for expr in self.expresiones:
            expr.Tipo(ctx)
        self.cast = self.expresiones[-1].cast

    def str(self, n):
        resultado = super().str(n)
        resultado = f'{n*" "}_block\n'
        resultado += ''.join([e.str(n+2) for e in self.expresiones])
        resultado += f'{(n)*" "}: {self.cast}\n'
        resultado += '\n'
        return resultado


@dataclass
class RamaCase(Nodo):
    nombre_variable: str
    tipo: str
    cuerpo: Expresion

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_branch\n'
        resultado += f'{(n+2)*" "}{self.nombre_variable}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        return resultado


@dataclass
class Swicht(Nodo):
    expr: Expresion
    casos: List[RamaCase]

    def Tipo(self, ctx: Context) -> None:
        self.expr.Tipo(ctx)
        branch_types = Counter([c.tipo for c in self.casos])
        for i,r in enumerate(branch_types):
            if branch_types[r] > 1:
                raise DUPLICATE_BRANCH(self.casos[i].linea,r)
        for caso in self.casos:
            ctx.add_case_scope({caso.nombre_variable:caso.tipo})
            caso.cuerpo.Tipo(ctx)
            ctx.exit_scope()
        self.cast = ctx.get_common_ancestor([c.cuerpo.cast for c in self.casos])

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_typcase\n'
        resultado += self.expr.str(n+2)
        resultado += ''.join([c.str(n+2) for c in self.casos])
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

@dataclass
class Nueva(Nodo):
    tipo: str

    def Tipo(self, ctx: Context) -> None:
        if not ctx.exists_type(self.tipo):
            raise EXPR_IN_UNDEFINED_TYPE(self.linea,self.tipo)
        self.cast = self.tipo

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_new\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado



@dataclass
class OperacionBinaria(Expresion):
    izquierda: Expresion
    derecha: Expresion

    def Tipo(self, ctx: Context) -> None:
        self.izquierda.Tipo(ctx)
        self.derecha.Tipo(ctx)
        if self.izquierda.cast != 'Int' or self.derecha.cast != 'Int':
            raise INCORRECT_BIN_OP_TYPES(self.linea,self.izquierda.cast, self.operando, self.derecha.cast)
        self.cast = 'Int'

@dataclass
class Suma(OperacionBinaria):
    operando: str = '+'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_plus\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Resta(OperacionBinaria):
    operando: str = '-'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_sub\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Multiplicacion(OperacionBinaria):
    operando: str = '*'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_mul\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado



@dataclass
class Division(OperacionBinaria):
    operando: str = '/'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_divide\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Menor(OperacionBinaria):
    operando: str = '<'

    def Tipo(self, ctx: Context) -> None:
        self.izquierda.Tipo(ctx)
        self.derecha.Tipo(ctx)
        if self.izquierda.cast != 'Int' or self.derecha.cast != 'Int':
            raise ILLEGAL_COMPARISON(self.linea)
        self.cast = 'Bool'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_lt\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

@dataclass
class LeIgual(OperacionBinaria):
    operando: str = '<='

    def Tipo(self, ctx: Context) -> None:
        self.izquierda.Tipo(ctx)
        self.derecha.Tipo(ctx)
        if self.izquierda.cast != 'Int' or self.derecha.cast != 'Int':
            raise ILLEGAL_COMPARISON(self.linea)
        self.cast = 'Bool'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_leq\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Igual(OperacionBinaria):
    operando: str = '='

    def Tipo(self, ctx: Context) -> None:
        self.izquierda.Tipo(ctx)
        self.derecha.Tipo(ctx)
        if self.izquierda.cast in ('Int', 'Bool', 'String'):
            if self.izquierda.cast != self.derecha.cast:
                raise ILLEGAL_COMPARISON(self.linea)
        self.cast = 'Bool'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_eq\n'
        resultado += self.izquierda.str(n+2)
        resultado += self.derecha.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado



@dataclass
class Neg(Expresion):
    expr: Expresion
    operador: str = '~'

    def Tipo(self, ctx: Context) -> None:
        self.expr.Tipo(ctx)
        if self.expr.cast != 'Int':
            # TODO Aqui igual crear excp para unary ops
            return self.set_default_cast()
        self.cast = 'Int'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_neg\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado



@dataclass
class Not(Expresion):
    expr: Expresion
    operador: str = 'NOT'

    def Tipo(self, ctx: Context) -> None:
        self.expr.Tipo(ctx)
        if self.expr.cast != 'Bool':
            # TODO Aqui igual crear excp para unary ops
            return self.set_default_cast()
        self.cast = 'Bool'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_comp\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class EsNulo(Expresion):
    expr: Expresion

    def Tipo(self, ctx: Context) -> None:
        self.expr.Tipo(ctx)
        self.cast = 'Bool'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_isvoid\n'
        resultado += self.expr.str(n+2)
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado




@dataclass
class Objeto(Expresion):
    nombre: str

    def Tipo(self, ctx: Context) -> None:
        tipo = ctx.get_variable_type(self.nombre)
        if not tipo:
            raise UNDECLARED_ID(self.linea,self.nombre)
        self.cast = tipo

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_object\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class NoExpr(Expresion):
    nombre: str = ''

    def Tipo(self, ctx: Context) -> None:
        self.cast = NULL

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_no_expr\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class Entero(Expresion):
    valor: int

    def Tipo(self, ctx: Context) -> None:
        self.cast = 'Int'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_int\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado


@dataclass
class String(Expresion):
    valor: str

    def Tipo(self, ctx: Context) -> None:
        self.cast = 'String'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_string\n'
        resultado += f'{(n+2)*" "}{self.valor}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado



@dataclass
class Booleano(Expresion):
    valor: bool
    
    def Tipo(self, ctx: Context) -> None:
        self.cast = 'Bool'

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_bool\n'
        resultado += f'{(n+2)*" "}{1 if self.valor else 0}\n'
        resultado += f'{(n)*" "}: {self.cast}\n'
        return resultado

@dataclass
class IterableNodo(Nodo):
    secuencia: List = field(default_factory=List)


class Programa(IterableNodo):

    def Tipo(self) -> str:
        ctx = Context()
        for clase in self.secuencia:
            attributes = [c for c in clase.caracteristicas if isinstance(c, Atributo)]
            methods = [c for c in clase.caracteristicas if isinstance(c, Metodo)]
            padre = clase.padre if clase.padre else 'Object'
            try:
                if ctx.structure.check_non_inheritable_classes(padre):
                    raise INHERIT_BASIC_CLASS(clase.linea, clase.nombre, padre)
                ctx.structure.add_new_class(
                    clase.linea, clase.nombre, padre,
                    { a.nombre:a.tipo for a in attributes },
                    { m.nombre: {
                        'type':m.tipo, 
                        'formals': { f.nombre_variable:f.tipo for f in m.formales } 
                    } for m in methods }
                )
            except CompilerError as err:
                return f'{clase.nombre_fichero}:{str(err)}'

        try:
            ctx.structure.check_no_main()
        except NO_MAIN as err:
            return str(err)

        for clase in self.secuencia:
            padre = clase.padre if clase.padre else 'Object'
            try:
                if not ctx.structure.check_undefined_inherit(padre):
                    raise UNDEFINED_INHERIT(clase.linea, clase.nombre, padre)
                clase.Tipo(ctx)
            except CompilerError as err:
                return f'{clase.nombre_fichero}:{str(err)}'

        return None

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{" "*n}_program\n'
        resultado += ''.join([c.str(n+2) for c in self.secuencia])
        return resultado


@dataclass
class Caracteristica(Nodo):
    nombre: str
    tipo: str
    cuerpo: Expresion


@dataclass
class Clase(Nodo):
    nombre: str
    padre: str
    nombre_fichero: str
    caracteristicas: List[Caracteristica] = field(default_factory=list)

    def Tipo(self, ctx: Context) -> None:
        ctx.create_class_scope(self.nombre)
        for c in self.caracteristicas:
            c.Tipo(ctx)
        ctx.exit_scope()
                
    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_class\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.padre}\n'
        resultado += f'{(n+2)*" "}"{self.nombre_fichero}"\n'
        resultado += f'{(n+2)*" "}(\n'
        resultado += ''.join([c.str(n+2) for c in self.caracteristicas])
        resultado += '\n'
        resultado += f'{(n+2)*" "})\n'
        return resultado

@dataclass
class Metodo(Caracteristica):
    formales: List[Formal]

    def Tipo(self, ctx: Context) -> None:
        ctx.add_method_scope(self.nombre)
        if not ctx.structure.check_valid_return_type(self.tipo):
            raise UNDEFINED_RETURN_TYPE(self.linea, self.tipo, self.nombre)
        for f,n in Counter(f.nombre_variable for f in self.formales).items():
            if n > 1: 
                raise REPEATED_FORMAL(self.linea, f)
        for formal in self.formales:
            if formal.nombre_variable == 'self':
                raise NO_PARAMETER_SELF(formal.linea)
            if formal.tipo == 'SELF_TYPE':
                raise SELF_TYPE_PARAMETER(formal.linea, formal.nombre_variable)
            ctx.structure.check_valid_redefined_formals(
                self.linea, ctx.current_class(),
                self.nombre,
                {f.nombre_variable:f.tipo for f in self.formales}
            )
        self.cuerpo.Tipo(ctx)
        if not ctx.inherits_from(self.cuerpo.cast, self.tipo):
            raise RETURN_NOT_CONFORM(self.cuerpo.linea, self.cuerpo.cast, self.nombre, self.tipo)
        ctx.exit_scope()

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_method\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += ''.join([c.str(n+2) for c in self.formales])
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        return resultado


class Atributo(Caracteristica):

    def Tipo(self, ctx: Context) -> None:
        self.cuerpo.Tipo(ctx)
        if self.nombre == 'self':
            raise NO_ATTRIBUTE_SELF(self.linea)
        if ctx.structure.check_repeated_inherited_attribute(ctx.current_class(), self.nombre):
            raise INHERITED_ATTRIBUTE(self.linea, self.nombre)
        if self.cuerpo.cast == NULL:
            return
        if not ctx.is_correct_type(self.tipo, self.cuerpo.cast):
            raise ASSIGN_TYPE_ERROR(self.cuerpo.linea, self.cuerpo.cast, self.tipo, self.nombre)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_attr\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        return resultado
