from Exceptions import *
from pprint import pformat


BASIC_CLASSES = [
    'Int', 'String', 'Bool', 'IO', 'Object', 'SELF_TYPE'
]

NON_INHERITABLE_CLASSES = [
    'Int', 'String', 'Bool', 'SELF_TYPE'
]


class Structure:
    ''' Class for representing the structure of a program

    '''

    def __init__(self) -> None:
        self.structure = {}

        self._register_basic_classes()
        self.non_inheritable_classes = NON_INHERITABLE_CLASSES

    def __repr__(self) -> str:
        return pformat(self.structure)

    def __contains__(self, x) -> str:
        for c in self.structure:
            if x in self.structure[c]['methods']:
                return c
        return None

    def has_main(self):
        return self.structure.get('Main', None) is not None

    def _register_basic_classes(self):
        self._register_object_class()
        self._register_string_class()
        self._register_io_class()
        self._register_int_class()
        self._register_bool_class()

    def _register_object_class(self):
        self.structure['Object'] = {
            'parent': None,
            'attributes': {},
            'methods': {
                'abort': {'type': 'Object', 'formals': {}},
                'type_name': {'type': 'String', 'formals': {}},
                'copy': {'type': 'SELF_TYPE', 'formals': {}},
            }
        }

    def _register_string_class(self):
        self.structure['String'] = {
            'parent': 'Object',
            'attributes': {},
            'methods': {
                'length': {'type': 'Int', 'formals': {}},
                'concat': {'type': 'String', 'formals': {'s': 'String'}},
                'substr': {'type': 'String', 'formals': {'i': 'Int', 'l': 'Int'}},
            }
        }

    def _register_io_class(self):
        self.structure['IO'] = {
            'parent': 'Object',
            'attributes': {},
            'methods': {
                'out_string': {'type': 'SELF_TYPE', 'formals': {'x': 'String'}},
                'out_int': {'type': 'SELF_TYPE', 'formals': {'x': 'Int'}},
                'in_string': {'type': 'String', 'formals': {}},
                'in_int': {'type': 'Int', 'formals': {}}
            }
            
        }

    def _register_int_class(self):
        self.structure['Int'] = {
            'parent': 'Object',
            'attributes': {},
            'methods': {}
        }

    def _register_bool_class(self):
        self.structure['Bool'] = {
            'parent': 'Object',
            'attributes': {},
            'methods': {}
        }

    def add_new_class(self, linea: int, name: str, parent: str, attributes: dict, methods: dict):
        if name in BASIC_CLASSES:
            raise REDEFINITION_OF_BASIC_CLASS(linea, name)
        if name in self.structure:
            raise REDEFINED_CLASS(linea, name)
        self.structure[name] = {
            'parent': parent,
            'attributes': attributes,
            'methods': methods
        }

    def has_type(self, type: str) -> bool:
        return type in self.structure

    def check_valid_redefined_formals(self, linea: int, className: str, methodName: str, formals: dict):
        parent = self.structure[className]['parent']
        while parent:
            parent_method = self.structure[parent]['methods'].get(methodName, None)
            if parent_method:
                if len(parent_method['formals']) != len(formals):
                    raise NUMBER_FORMAL_PARAMETERS(linea, methodName)
                for m in formals:
                    if m in parent_method['formals']: 
                        if formals[m] != parent_method['formals'][m]:
                            raise WRONG_REDEFINED_ARGUMENTS(linea, methodName, formals[m], parent_method['formals'][m])
            parent = self.structure[parent]['parent']

    def inherits_from(self, type1: str, type2: str):
        if type1 == type2:
            return True
        parent = self.structure[type1]['parent']
        while parent:
            if parent == type2:
                return True
            parent = self.structure[parent]['parent']
        return False

    def check_no_main(self):
        if not self.has_main():
            raise NO_MAIN(0)

    def check_undefined_inherit(self, parent):
        return parent in self.structure

    def check_non_inheritable_classes(self, parent):
        return parent in NON_INHERITABLE_CLASSES

    def check_valid_return_type(self, ret_type):
        return ret_type in self.structure or ret_type == 'SELF_TYPE'

    def check_repeated_inherited_attribute(self, className: str, attr: str) -> dict:
        inh_attrs = self.get_class_inherited_attributes(className)
        return attr in inh_attrs

    def get_class_attributes(self, className: str) -> dict:
        return {
            **self.get_class_proper_attributes(className),
            **self.get_class_inherited_attributes(className)
        }

    def get_class_inherited_attributes(self, className: str) -> dict:
        inherited_attributes = {}
        parent = self.structure[className]['parent']
        while parent:
            inherited_attributes.update(self.structure[parent]['attributes'])
            parent = self.structure[parent]['parent']
        return inherited_attributes

    def get_class_proper_attributes(self, className: str) -> dict:
        return self.structure[className]['attributes']

    def get_type_info(self, typeid: str) -> dict:
        '''
        
        '''

        type = self.structure[typeid]
        methods = set(type['methods'])
        parent = type['parent']
        while parent:
            methods.add(parent['methods'])
            parent = self.structure[parent]['parent']

        return {
            'parent': type['parent'],
            'methods': list(methods)
        }

    def get_method_info(self, typeid: str, methodName: str) -> dict:
        '''

        '''
        
        if metodo := self.structure[typeid]['methods'].get(methodName, None):
            return metodo
        
        parent = self.structure[typeid]['parent']
        while parent:
            if metodo := self.structure[parent]['methods'].get(methodName, None):
                return metodo
            parent = self.structure[parent]['parent']

        return None

    def get_method_attributes(self, className: str, methodName: str) -> dict:
        return self.structure[className]['methods'][methodName]

    def get_common_ancestor(self, typeid1: str, typeid2: str) -> str:
        '''

        '''
        
        if typeid1 == typeid2:
            return typeid1

        ancestors1, ancestors2 = [], []
        parent1, parent2 = typeid1, typeid2
        while parent1:
            ancestors1.insert(0, parent1)
            parent1 = self.structure[parent1]['parent']
        while parent2:
            ancestors2.insert(0, parent2)
            parent2 = self.structure[parent2]['parent']

        while ancestors1 and ancestors2:
            a1 = ancestors1.pop(0)
            a2 = ancestors2.pop(0)
            if a1 == a2:
                common_ancestor = a1
            else: 
                break

        return common_ancestor

    def is_correct_type(self, target, value):
        '''
        '''

        if target == value:
            return True
        parent = value
        while parent:
            if target == parent:
                return True
            parent = self.structure[parent]['parent']
        return False

if __name__ == '__main__':
    struct = Structure()
    print(struct.get_common_ancestor('IO', 'Int'))