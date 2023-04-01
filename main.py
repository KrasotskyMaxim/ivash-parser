from constants import *
from exceptions import InvalidFormulaException


class LogicFormula(): 
    def __init__(self, formula: str):
        self.raw_formula = formula
        self.logic_tree = []
        self.parse_formula()
    
    def parse_formula(self):
        if len(self.raw_formula) == 1:
            if self.raw_formula in LOGIC_CONSTANT | LOGIC_CAPITAL_LETTER:
                self.logic_tree.append(self.raw_formula)
            else:
                raise InvalidFormulaException("Invalid formula!")
            
        bracket_counter = 0
        open_bracket_index = None
        close_bracket_index = None
        for i, ch in enumerate(self.raw_formula):
            if ch == OPEN_BRACKET:
                bracket_counter += 1
                open_bracket_index = i
                for j, nch in enumerate(self.raw_formula[i+1:]):
                    if ch == OPEN_BRACKET: bracket_counter += 1
                    if ch == CLOSE_BRACKET: bracket_counter -= 1
                    if bracket_counter == 0:
                        close_bracket_index = j
                        break
                               

    def is_sknf(self):
        pass




def main():
    while True:
        formula = input("Enter formula: ")
        a = LogicFormula(formula)
        # A
        # (!A)
        # (A/\A)
        # (!((A/\0)->B))
        # ((A/\B)/\C)
        # [["A", "/\\", "B"], "/\\", "C"]

if __name__ == '__main__':
    # main()
    print()
