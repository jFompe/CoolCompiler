# coding: utf-8
from dataclasses import dataclass, field
from typing import List

from collections import Counter

from Context import Context
from Exceptions import *


DEFAULT_CAST = 'Object'


# NO_MAIN = lambda: 'Class Main is not defined.'
# RETURN_NOT_CONFORM = lambda type1,method,type2: f'Inferred return type {type1} of method {method} does not conform to declared return type {type2}.'
# INITIALIZATION_NOT_CONFORM = lambda type1,id,type2: f'Inferred type {type1} of initialization of {id} does not conform to identifier\'s declared type {type2}.'
# EXPR_NOT_CONFORM = lambda type1,type2: f'Expression type {type1} does not conform to declared static dispatch type {type2}.'
# EXPR_IN_UNDEFINED_TYPE = lambda expr,clase: f'\'{expr}\' used with undefined class {clase}.'
# UNDEFINED_RETURN_TYPE = lambda type,method: f'Undefined return type {type} in method {method}.'
# NO_ATTRIBUTE_SELF = lambda name: f'\'{name}\' cannot be the name of an attribute.'
# ASSIGN_TYPE_ERROR = lambda type1, type2, id: f'Type {type1} of assigned expression does not conform to declared type {type2} of identifier {id}.'
# UNDECLARED_ID = lambda id: f'Undeclared identifier {id}.'
# INHERITED_ATTRIBUTE = lambda id: f'Attribute {id} is an attribute of an inherited class.'
# INCORRECT_ARGUMENT = lambda method, type1, id, type2 : f'In call of method {method}, type {type1} of parameter {id} does not conform to declared type {type2}.'
# INCORRECT_BIN_OP_TYPES = lambda type1, op, type2: f'non-Int arguments: {type1} {op} {type2}'
# DISPATCH_UNDEFINED = lambda id: f'Dispatch to undefined method {id}.'
# ILLEGAL_COMPARISON = lambda: f'Illegal comparison with a basic type.'
# REDEFINITION_OF_BASIC_CLASS = lambda cl: f'Redefinition of basic class {cl}.'
# INHERIT_BASIC_CLASS = lambda cl1, cl2: f'Class {cl1} cannot inherit class {cl2}.'
# INCORRECT_LOOP_CONDITION = lambda: f'Loop condition does not have type Bool.'
# DUPLICATE_BRANCH = lambda type: f'Duplicate branch {type} in case statement.'
# REPEATED_FORMAL = lambda id: f'Formal parameter {id} is multiply defined.'
# NOT_BOUNDABLE_IN_LET = lambda id: f'\'{id}\' cannot be bound in a \'let\' expression.'
# UNDEFINED_INHERIT = lambda cl1, cl2: f'Class {cl1} inherits from an undefined class {cl2}.'
# WRONG_REDIFINED_ARGUMENTS = lambda method,type1,type2: f'In redefined method {method}, parameter type {type1} is different from original type {type2}'
# REDEFINED_CLASS = lambda cl: f'Class {cl} was previously defined.'
# SELF_ASSIGNMENT = lambda: f'Cannot assign to \'self\'.'
# NO_PARAMETER_SELF = lambda: f'\'self\' cannot be the name of a formal parameter.'
# SELF_TYPE_PARAMETER = lambda id: f'Formal parameter {id} cannot have type SELF_TYPE.'
# NUMBER_FORMAL_PARAMETERS = lambda method: f'Incompatible number of formal parameters in redefined method {method}.'



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
        tipo = ctx.get_variable_type(self.nombre)
        if not tipo:
            raise UNDECLARED_ID(self.nombre)
        self.cuerpo.Tipo(ctx)
        if tipo == 'self':
            raise SELF_ASSIGNMENT
        if tipo != self.cuerpo.cast:
            raise ASSIGN_TYPE_ERROR(self.cuerpo.cast, tipo, self.nombre)
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
            raise EXPR_NOT_CONFORM(self.cuerpo.cast, self.clase)
        ctx.check_method(
            self.clase, self.nombre_metodo, 
            [arg.cast for arg in self.argumentos])
        self.cast = self.cuerpo.cast

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
        # TODO Check nombre en scope y cuerpo igual al tipo
        self.cuerpo.Tipo(ctx)
        for arg in self.argumentos:
            arg.Tipo(ctx)
        clase = (ctx.current_class() 
            if self.cuerpo.nombre == 'self' 
            else self.cuerpo.cast) 
        ctx.check_method(
            clase, self.nombre_metodo,
            [arg.cast for arg in self.argumentos])
        self.cast = self.cuerpo.cast

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
            return self.set_default_cast()
        self.cast = ctx.structure.get_common_ancestor(self.verdadero.cast, self.falso.cast)

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
            raise INCORRECT_LOOP_CONDITION
        self.cast = self.cuerpo.cast

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
            raise NOT_BOUNDABLE_IN_LET
        if self.tipo.cast != self.inicializacion.tipo:
            raise INITIALIZATION_NOT_CONFORM(self.inicializacion.cast, self.nombre, self.tipo.cast)
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
        self.expresiones[-1].Tipo(ctx)
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
        branch_types = Counter([c.tipo for c in self.casos])
        for r in branch_types:
            if branch_types[r] > 1:
                raise DUPLICATE_BRANCH(r)
        self.cast = 'Object'

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
            raise EXPR_IN_UNDEFINED_TYPE(self.tipo)
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
            raise INCORRECT_BIN_OP_TYPES(self.izquierda.cast, self.operando, self.derecha.cast)
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
            raise ILLEGAL_COMPARISON
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
            raise ILLEGAL_COMPARISON
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
                raise ILLEGAL_COMPARISON
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
            raise UNDECLARED_ID(self.nombre)
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
        self.cast = 'Null'

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

    def Tipo(self) -> list:
        ctx = Context()
        for clase in self.secuencia:
            attributes = [c for c in clase.caracteristicas if isinstance(c, Atributo)]
            methods = [c for c in clase.caracteristicas if isinstance(c, Metodo)]
            ctx.structure.add_new_class(
                clase.nombre, clase.padre,
                { a.nombre:a.tipo for a in attributes },
                { m.nombre: {
                    'type':m.tipo, 
                    'formals': { f.nombre_variable:f.tipo for f in m.formales } 
                } for m in methods }
            )
        # print(ctx.structure)

        try:
            ctx.structure.check_no_main()
        except NO_MAIN as err:
            ctx.add_error(str(err))
            return ctx.errores

        for clase in self.secuencia:
            try:
                clase.Tipo(ctx)
            except CompilerError as err:
                ctx.add_error(f'{clase.nombre_fichero}:{self.linea}: {str(err)}')
                return ctx.errores

        return ctx.errores

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
        self.cuerpo.Tipo(ctx)
        if self.cuerpo.cast != self.tipo:
            return RETURN_NOT_CONFORM(self.cuerpo.cast, self.nombre, self.tipo)
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
        if not self.cuerpo.cast in (self.tipo, 'Null'):
            raise ASSIGN_TYPE_ERROR(self.cuerpo.cast, self.tipo, self.nombre)

    def str(self, n):
        resultado = super().str(n)
        resultado += f'{(n)*" "}_attr\n'
        resultado += f'{(n+2)*" "}{self.nombre}\n'
        resultado += f'{(n+2)*" "}{self.tipo}\n'
        resultado += self.cuerpo.str(n+2)
        return resultado
