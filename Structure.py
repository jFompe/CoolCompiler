from os import O_RANDOM
from Exceptions import *
from collections import defaultdict, Counter
from pprint import pformat, pprint


BASIC_CLASSES = [
    'Int', 'String', 'Bool', 'IO', 'Object'
]

NON_INHERITABLE_CLASSES = [
    'Int', 'String', 'Bool'
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

    def add_new_class(self, name: str, parent: str, attributes: dict, methods: dict):
        if name in BASIC_CLASSES:
            raise REDEFINITION_OF_BASIC_CLASS(name)
        if name in self.structure:
            raise REDEFINED_CLASS(name)
        self.structure[name] = {
            'parent': parent,
            'attributes': attributes,
            'methods': methods
        }

    def has_type(self, type: str) -> bool:
        return type in self.structure

    def check_classes(self):
        self.check_no_main()
        for k,v in self.structure.items():
            parent = v['parent']
            self.check_undefined_inherit(k, parent)
            self.check_non_inheritable_classes(k, parent)
            self.check_self_attribute(k)
            self.check_repeated_inherited_attribute(k)
            self.check_undefined_return_type(k)
            self.check_self_type_parameters(k)
            self.check_self_parameter(k)
            self.check_repeated_formals(k)
            self.check_redefined_arguments(k)

    def check_repeated_formals(self, className: str):
        for mv in self.structure[className]['methods'].values():
            formal_counts = Counter(mv['formals'].keys())
            for f in formal_counts:
                if formal_counts[f] > 1:
                    raise REPEATED_FORMAL(f)

    def check_redefined_arguments(self, className: str):
        methods = self.structure[className]['methods']
        methodNames = set(m for m in methods)
        parent = self.structure[className]['parent']
        while parent and methodNames:
            parMethods = set(m for m in self.structure[parent]['methods'])
            for m in methodNames.intersection(parMethods):
                self.check_redefined_methods(
                    m,
                    self.structure[className]['methods'][m],
                    self.structure[parent]['methods'][m]
                )
            parent = self.structure[parent]['parent']

    def check_redefined_methods(self, name, m1, m2):
        if len(m1['formals']) != len(m2['formals']):
            raise NUMBER_FORMAL_PARAMETERS(name)
        for f1,f2 in zip(m1['formals'], m2['formals']):
            if f1['type'] != f2['type']:
                raise WRONG_REDEFINED_ARGUMENTS(name,f1['type'],f2['type'])

    def check_no_main(self):
        if not self.has_main():
            raise NO_MAIN

    def check_self_type_parameters(self, className):
        for method in self.structure[className]['methods'].values():
            for formal in method['formals']:
                if formal == 'self':
                    raise NO_PARAMETER_SELF

    def check_self_parameter(self, className):
        for method in self.structure[className]['methods'].values():
            for name, type in method['formals'].items():
                if type == 'SELF_TYPE':
                    raise SELF_TYPE_PARAMETER(name)

    def check_undefined_inherit(self, className, parent):
        if parent is not None and parent not in self.structure:
            raise UNDEFINED_INHERIT(className, parent)

    def check_non_inheritable_classes(self, className, parent):
        if parent in NON_INHERITABLE_CLASSES:
                raise INHERIT_BASIC_CLASS(className, parent)

    def check_undefined_return_type(self, className):
        methods = self.structure[className]['methods']
        for m,v in methods.items():
            if v['type'] not in self.structure and v['type'] != 'SELF_TYPE':
                raise UNDEFINED_RETURN_TYPE(v['type'], m)

    def check_self_attribute(self, className: str) -> bool:
        if any(attr == 'self' for attr in self.get_class_proper_attributes(className)):
            raise NO_ATTRIBUTE_SELF

    def check_repeated_inherited_attribute(self, className: str) -> dict:
        inh_attrs = self.get_class_inherited_attributes(className)
        for attr in self.get_class_proper_attributes(className):
            if attr in inh_attrs:
                raise INHERITED_ATTRIBUTE(attr)

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
        
        return self.structure[typeid]['methods'].get(methodName, None)

    def get_method_attributes(self, className: str, methodName: str) -> dict:
        return self.structure[className]['methods'][methodName]

    def get_common_ancestor(self, typeid1: str, typeid2: str) -> str:
        '''

        '''
        
        if typeid1 == typeid2:
            return typeid1

        ancestors1, ancetors2 = [], []
        parent1, parent2 = typeid1, typeid2
        while parent1:
            ancestors1.insert(0, parent1)
            parent1 = self.structure[parent1]['parent']
        while parent2:
            ancetors2.insert(0, parent2)
            parent2 = self.structure[parent2]['parent']

        while (a1 := ancestors1.pop(0)) == ancetors2.pop(0):
            common_ancestor = a1

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