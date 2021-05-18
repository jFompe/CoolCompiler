from typing import List
from Scope import Scope
from Structure import Structure

from Exceptions import *

class Context:

    def __init__(self) -> None:
        self.structure = Structure()
        self.scopes = []

    def exists_type(self, type: str) -> bool:
        return type == 'SELF_TYPE' or self.structure.has_type(type)

    def check_method(self, linea: int, className: str, methodName: str, arguments: List[str]) -> bool:
        metodo = self.get_method_info(className, methodName)
        if not metodo:
            raise DISPATCH_UNDEFINED(linea, methodName)
        methodArgs = metodo['formals']
        if len(methodArgs) != len(arguments):
            raise INCORRECT_ARGUMENTS_LENGTH(linea)
        for argVal, argTarget in zip(arguments, methodArgs):
            if not self.is_correct_type(methodArgs[argTarget], argVal):
                raise INCORRECT_ARGUMENT(linea,methodName,argVal,argTarget,methodArgs[argTarget])

    def get_method_info(self, className, methodName):
        if className == 'SELF_TYPE':
            className = self.current_class()
        return self.structure.get_method_info(className, methodName)
    
    def get_method_type(self, className, methodName):
        if className == 'SELF_TYPE':
            className = self.current_class()
        return self.structure.get_method_info(className, methodName)['type']

    def is_correct_type(self, target, value):
        if value == 'SELF_TYPE':
            value = self.current_class()
        return self.structure.is_correct_type(target, value)

    def current_class(self):
        return self.scopes[0].get_current_class()

    def create_class_scope(self, className: str):
        attributes = self.structure.get_class_attributes(className)
        self.scopes.append(Scope(className, attributes))

    def add_method_scope(self, methodName: str):
        currentClass = self.current_class()
        formals = self.structure.get_method_attributes(currentClass, methodName)['formals']
        self.scopes.append(Scope(currentClass, formals))

    def add_let_scope(self, variables: dict):
        currentClass = self.current_class()
        self.scopes.append(Scope(currentClass, variables))

    def add_case_scope(self, variable: dict):
        currentClass = self.current_class()
        self.scopes.append(Scope(currentClass, variable))

    def exit_scope(self):
        self.scopes.pop()

    def get_variable_type(self, name: str):
        if name == 'self':
            return 'SELF_TYPE'
            # return self.current_class()
        for sc in reversed(self.scopes):
            var_type = sc.get_variable_type(name)
            if var_type:
                return var_type
        return None

    def inherits_from(self, type1, type2):
        if type1 == type2:
            return True
        if type1 == 'SELF_TYPE':
            type1 = self.current_class()
        return self.structure.inherits_from(type1, type2)

    def get_common_ancestor(self, classes: List[str]):
        for i,c in enumerate(classes):
            if c == 'SELF_TYPE':
                classes[i] = self.current_class()

        if len(classes) == 1:
            return classes[0]
        if len(classes) == 2:
            return self.structure.get_common_ancestor(classes[0], classes[1])

        c = classes[0]
        for i in range(1,len(classes)):
            c = self.structure.get_common_ancestor(c, classes[i])
        return c
        