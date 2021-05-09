class CompilerError(Exception):
    pass

class NO_MAIN(CompilerError):
    def __str__(self) -> str:
        return 'Class Main is not defined.'

class RETURN_NOT_CONFORM(CompilerError):
    def __init__(self, type1, method, type2) -> None:
        self.type1 = type1
        self.method = method
        self.type2 = type2
    def __str__(self) -> str:
        return f'Inferred return type {self.type1} of method {self.method} does not conform to declared return type {self.type2}.'

class INITIALIZATION_NOT_CONFORM(CompilerError):
    def __init__(self, type1,id,type2) -> None:
        self.type1 = type1
        self.id = id
        self.type2 = type2
    def __str__(self) -> str:
        return f'Inferred type {self.type1} of initialization of {self.id} does not conform to identifier\'s declared type {self.type2}.'

class EXPR_NOT_CONFORM(CompilerError):
    def __init__(self, type1,type2) -> None:
        self.type1 = type1
        self.type2 = type2
    def __str__(self) -> str:
        return f'Expression type {self.type1} does not conform to declared static dispatch type {self.type2}.'

class EXPR_IN_UNDEFINED_TYPE(CompilerError):
    def __init__(self, clase) -> None:
        self.clase = clase
    def __str__(self) -> str:
        return f'\'new\' used with undefined class {self.clase}.'

class UNDEFINED_RETURN_TYPE(CompilerError):
    def __init__(self, type,method) -> None:
        self.type = type
        self.method = method
    def __str__(self) -> str:
        return f'Undefined return type {self.type} in method {self.method}.'

class NO_ATTRIBUTE_SELF(CompilerError):
    def __str__(self) -> str:
        return f'\'self\' cannot be the name of an attribute.'

class ASSIGN_TYPE_ERROR(CompilerError):
    def __init__(self, type1, type2, id) -> None:
        self.type1 = type1
        self.type2 = type2 
        self.id = id 
    def __str__(self) -> str:
        return f'Type {self.type1} of assigned expression does not conform to declared type {self.type2} of identifier {self.id}.'

class UNDECLARED_ID(CompilerError):
    def __init__(self, id) -> None:
        self.id = id
    def __str__(self) -> str:
        return f'Undeclared identifier {self.id}.'

class INHERITED_ATTRIBUTE(CompilerError):
    def __init__(self, id) -> None:
        self.id = id
    def __str__(self) -> str:
        return f'Attribute {self.id} is an attribute of an inherited class.'

class INCORRECT_ARGUMENT(CompilerError):
    def __init__(self, method, type1, id, type2) -> None:
        self.method = method
        self.type1 = type1
        self.id = id 
        self.type2 = type2 
    def __str__(self) -> str:
        return f'In call of method {self.method}, type {self.type1} of parameter {self.id} does not conform to declared type {self.type2}.'

class INCORRECT_ARGUMENTS_LENGTH(CompilerError):
    def __str__(self) -> str:
        return f'Incorrect arguments length'

class INCORRECT_BIN_OP_TYPES(CompilerError):
    def __init__(self, type1, op, type2) -> None:
        self.type1 = type1
        self.op = op 
        self.type2 = type2 
    def __str__(self) -> str:
        return f'non-Int arguments: {self.type1} {self.op} {self.type2}'

class DISPATCH_UNDEFINED(CompilerError):
    def __init__(self, id) -> None:
        self.id = id
    def __str__(self) -> str:
        return f'Dispatch to undefined method {self.id}.'

class ILLEGAL_COMPARISON(CompilerError):
    def __str__(self) -> str:
        return f'Illegal comparison with a basic type.'

class REDEFINITION_OF_BASIC_CLASS(CompilerError):
    def __init__(self, cl) -> None:
        self.cl = cl
    def __str__(self) -> str:
        return f'Redefinition of basic class {self.cl}.'

class INHERIT_BASIC_CLASS(CompilerError):
    def __init__(self, cl1, cl2) -> None:
        self.cl1 = cl1
        self.cl2 = cl2
    def __str__(self) -> str:
        return f'Class {self.cl1} cannot inherit class {self.cl2}.'

class INCORRECT_LOOP_CONDITION(CompilerError):
    def __str__(self) -> str:
        return f'Loop condition does not have type Bool.'

class DUPLICATE_BRANCH(CompilerError):
    def __init__(self, type) -> None:
        self.type = type
    def __str__(self) -> str:
        return f'Duplicate branch {self.type} in case statement.'

class REPEATED_FORMAL(CompilerError):
    def __init__(self, id) -> None:
        self.id = id
    def __str__(self) -> str:
        return f'Formal parameter {self.id} is multiply defined.'

class NOT_BOUNDABLE_IN_LET(CompilerError):
    def __str__(self) -> str:
        return f'\'self\' cannot be bound in a \'let\' expression.'

class UNDEFINED_INHERIT(CompilerError):
    def __init__(self, cl1, cl2) -> None:
        self.cl1 = cl1
        self.cl2 = cl2
    def __str__(self) -> str:
        return f'Class {self.cl1} inherits from an undefined class {self.cl2}.'

class WRONG_REDEFINED_ARGUMENTS(CompilerError):
    def __init__(self, method,type1,type2) -> None:
        self.method = method
        self.type1 = type1
        self.type2 = type2
    def __str__(self) -> str:
        return f'In redefined method {self.method}, parameter type {self.type1} is different from original type {self.type2}'

class REDEFINED_CLASS(CompilerError):
    def __init__(self, cl) -> None:
        self.cl = cl
    def __str__(self) -> str:
        return f'Class {self.cl} was previously defined.'

class SELF_ASSIGNMENT(CompilerError):
    def __str__(self) -> str:
        return f'Cannot assign to \'self\'.'

class NO_PARAMETER_SELF(CompilerError):
    def __str__(self) -> str:
        return f'\'self\' cannot be the name of a formal parameter.'

class SELF_TYPE_PARAMETER(CompilerError):
    def __init__(self, id) -> None:
        self.id = id
    def __str__(self) -> str:
        return f'Formal parameter {self.id} cannot have type SELF_TYPE.'

class NUMBER_FORMAL_PARAMETERS(CompilerError):
    def __init__(self, method) -> None:
        self.method = method
    def __str__(self) -> str:
        return f'Incompatible number of formal parameters in redefined method {self.method}.'


