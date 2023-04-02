from constants import *
from exceptions import InvalidFormulaException


class BinaryFormula:
    def __init__(self, raw_components):
        self.raw_components = raw_components
        self.parse_components()
        
    def parse_components(self):
        if isinstance(actor := self.raw_components[0], list):
            self.actor = BinaryFormula(actor) if len(actor) == 3 else UnaryFormula(actor)
        else: self.actor = actor
        
        self.action = self.raw_components[1]
        
        if isinstance(actored := self.raw_components[2], list):
            self.actored = BinaryFormula(actored) if len(actored) == 3 else UnaryFormula(actored) 
        else: self.actored = actored


class UnaryFormula:
    def __init__(self, raw_components):
        self.raw_components = raw_components
        self.parse_components()

    def parse_components(self):
        self.action = self.raw_components[0]
        
        if isinstance(actored := self.raw_components[1], list):
            self.actored = BinaryFormula(actored) if len(actored) == 3 else UnaryFormula(actored) 
        else: self.actored = actored

    
class LogicFormula(): 
    def __init__(self, formula: str):
        self.raw_formula = formula
        self.formula = None
        self.parse_formula()

    def parse_formula(self):
        if len(self.raw_formula) == 1:
            self.raw_components.append(self.raw_formula)
            return 

        formula = self.raw_formula.replace("/\\", CONJUCTION).replace("\\/", DISJUCTION).replace("->", IMPLICATION)
        formula = formula.replace("(", OPEN_BRACKET).replace(")", CLOSE_BRACKET)
        formula = " ".join(formula)

        black_list = []
        fcopy = formula
        for i, ch in enumerate(fcopy):
            if ch not in (OPEN_BRACKET, BLANK) and ch not in black_list:
                formula = formula.replace(ch, f"{ch},") if ch == CLOSE_BRACKET else formula.replace(ch, f"'{ch}',")
                black_list.append(ch)

        formula = formula[:-1]    
        result = eval(formula)
        self.formula = UnaryFormula(result) if len(result) == 2 else BinaryFormula(result)
            
        
    def is_sknf(self):
        pass


if __name__ == '__main__':
    formula = "(!(!A))"
    a = LogicFormula(formula)
    a.is_sknf()
    