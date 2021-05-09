from typing import List
from Scope import Scope
from Structure import Structure

from Exceptions import *

class Context:

    def __init__(self) -> None:
        self.structure = Structure()
        self.scopes = []
        self.errores = []

    def add_error(self, error: str):
        self.errores.append(error)

    def check_classes(self):
        return self.structure.check_classes()

    def exists_type(self, type: str) -> bool:
        return self.structure.has_type(type)

    def check_method(self, className: str, methodName: str, arguments: List[str]) -> bool:
        metodo = self.structure.get_method_info(className, methodName)
        if not metodo:
            raise DISPATCH_UNDEFINED(methodName)
        # if ret_type != metodo['type']:
        #     raise RETURN_NOT_CONFORM(ret_type, methodName, metodo['type'])
        methodArgs = list(metodo.values())
        if len(methodArgs) != len(arguments):
            raise INCORRECT_ARGUMENTS_LENGTH
        for argVal, argTarget in zip(arguments, methodArgs):
            if not self.structure.is_correct_type(argTarget, argVal):
                raise INCORRECT_ARGUMENT(methodName,argVal,id,argTarget)

    def current_class(self):
        return self.scopes[0].get_current_class()

    def create_class_scope(self, className: str):
        attributes = self.structure.get_class_attributes(className)
        self.scopes.append(Scope(className, attributes))

    def add_method_scope(self, methodName: str):
        currentClass = self.current_class()
        formals = self.structure.get_method_attributes(currentClass, methodName)
        self.scopes.append(Scope(currentClass, formals))

    def add_let_scope(self, variables: dict):
        currentClass = self.current_class()
        self.scopes.append(Scope(currentClass, variables))

    def exit_scope(self):
        self.scopes.pop()

    def get_variable_type(self, name: str):
        for sc in reversed(self.scopes):
            var_type = sc.get_variable_type(name)
            if var_type:
                return var_type
        return None