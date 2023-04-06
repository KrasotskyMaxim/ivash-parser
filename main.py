from constants import *
from exceptions import InvalidFormulaException


class BinaryFormula:
    def __init__(self, raw_components):
        self.raw_components = raw_components
        self.parse_components()
        
    def parse_components(self):
        if isinstance(actor := self.raw_components[0], list):
            if len(actor) == 2:
                self.actor = UnaryFormula(actor)
            elif len(actor) == 3:
                self.actor = BinaryFormula(actor)
            else:
                raise InvalidFormulaException
        else:
            if actor in (LOGIC_CAPITAL_LETTER | LOGIC_CONSTANT):
                self.actor = actor
            else:
                raise InvalidFormulaException
        
        if self.raw_components[1] in BINARY_LINK:
            self.action = self.raw_components[1]
        else:
            raise InvalidFormulaException
        
        if isinstance(actored := self.raw_components[2], list):
            if len(actored) == 2:
                self.actored = UnaryFormula(actored)
            elif len(actored) == 3:
                self.actored = BinaryFormula(actored)
            else:
                raise InvalidFormulaException
        else:
            if actored in (LOGIC_CAPITAL_LETTER | LOGIC_CONSTANT):
                self.actored = actored
            else:
                raise InvalidFormulaException


class UnaryFormula:
    def __init__(self, raw_components):
        self.raw_components = raw_components
        self.parse_components()

    def parse_components(self):
        if self.raw_components[0] in NEGATIVE:
            self.action = self.raw_components[0]
        else:
            raise InvalidFormulaException
        
        if isinstance(actored := self.raw_components[1], list):
            if len(actored) == 2:
                self.actored = UnaryFormula(actored)
            elif len(actored) == 3:
                self.actored = BinaryFormula(actored)
            else:
                raise InvalidFormulaException
        else:
            if actored in (LOGIC_CAPITAL_LETTER | LOGIC_CONSTANT):
                self.actored = actored
            else:
                raise InvalidFormulaException

    
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
        for ch in fcopy:
            if ch not in (OPEN_BRACKET, BLANK) and ch not in black_list:
                formula = formula.replace(ch, f"{ch},") if ch == CLOSE_BRACKET else formula.replace(ch, f"'{ch}',")
                black_list.append(ch)

        formula = formula[:-1]
        try:    
            formula = eval(formula)
        except:
            raise InvalidFormulaException
        if len(formula) == 2:
            self.formula = UnaryFormula(formula)
        elif len(formula) == 3:
            self.formula = BinaryFormula(formula)
        else:
            raise InvalidFormulaException
            
        
    def is_sknf(self):
        pass


if __name__ == '__main__':
    formula = "(/\\A)"
    a = LogicFormula(formula)
    print(type(a.formula))
    a.is_sknf()
    