
class VariableAlreadyDefined(Exception):
    pass

class Scope:
    ''' Class for representing the scope of a program
    
    '''

    def __init__(self, className: str, variables: dict) -> None:
        self.current_class = className
        self.variables = variables

    def get_variable_type(self, var: str) -> str:
        ''' Gets a variable type
        
        '''

        return self.variables.get(var, None)

    def get_current_class(self) -> str:
        '''
        
        '''

        return self.current_class
