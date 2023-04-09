from constants import *
from exceptions import InvalidFormulaException
from models import BinaryFormula, UnaryFormula
from logs import logger

from contextlib import contextmanager
import json


def test_valid_sknf():
    with open("tests/test-valid-sknf.json", "r") as f:
        data = json.load(f)

    try:
        for formula, sknf in data.items():
            a = LogicFormula(formula)
            assert a.is_sknf() == sknf
        logger.info("Tests valid SKNF are passed!")
    except AssertionError as e:
        logger.error("Test failed: %s not %s", formula, sknf)
        raise

@contextmanager
def clear_bf_components():
    try:
        logger.debug("Enter in clear_bf_components contextmanager")
        # Enter the context
        # Perform any setup operations
        yield
    finally:
        logger.debug("Clear Formulas components")
        BinaryFormula.self_components = []
        BinaryFormula.other_components = []
        LogicFormula.literals = set()
    
    
class LogicFormula(): 
    literals = set()

    def __init__(self, formula: str):
        self.raw_formula = formula
        self.formula = None
        self.parse_formula()

    def parse_formula(self):
        if len(self.raw_formula) == 1:
            self.formula = self.raw_formula
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
        result = eval(formula)
        self.formula = UnaryFormula(result) if len(result) == 2 else BinaryFormula(result)
            
        
    def is_sknf(self) -> bool:
        if not isinstance(self.formula, BinaryFormula|UnaryFormula):
            logger.debug("formula '%s' is a char", self.formula)
            return self.formula not in LOGIC_CONSTANT
        
        if isinstance(self.formula, UnaryFormula):
            logger.debug("formula '%s' is UnaryFormula", self.formula)
            self.formula, result = self.formula.cut()
            return result    
            
        if self.formula.action != CONJUCTION:
            with clear_bf_components():    
                logger.debug("formula '%s' has not conjuction", self.formula)
                return self.formula.is_simple_disjuction()

        if not any([
            isinstance(self.formula.actor, BinaryFormula|UnaryFormula),
            isinstance(self.formula.actored, BinaryFormula|UnaryFormula),
        ]):
            logger.debug("formula '%s' has all chars", self.formula)
            return False

        if not all([
            self._check_sknf_sub_formuls(self.formula.actor, type="actor"),
            self._check_sknf_sub_formuls(self.formula.actored, type="actored")
        ]):
            logger.debug("formula '%s' has invalid subformuls", self.formula)
            return False 

        with clear_bf_components():
            if self.formula.actor == self.formula.actored:
                logger.debug("formula %s has equal sub_formuls", self.formula)
                return False

        with clear_bf_components():
            actor_chars = LogicFormula.get_literals(self.formula.actor)
        with clear_bf_components():
            actored_chars = LogicFormula.get_literals(self.formula.actored)
            
        if actor_chars != actored_chars:
            logger.debug("Formulas has not all chars")
            return False        
        
        return True

    def _check_sknf_sub_formuls(self, sf, type) -> bool:
        if not isinstance(sf, BinaryFormula|UnaryFormula):
            logger.debug("sub formula '%s' of formula '%s' is a char", sf, self.formula)
            return sf not in LOGIC_CONSTANT
        
        if isinstance(sf, UnaryFormula):
            logger.debug("sub formula '%s' of formula '%s' if UnaryFormula", sf, self.formula)
            return sf.is_simple()

        if sf.action == CONJUCTION:
            temp = LogicFormula("A")
            temp.formula = sf
            return temp.is_sknf()

        if sf.action != DISJUCTION:
            logger.debug("sub formula '%s' of formula '%s' has not disjuction", sf, self.formula)
            return False
        
        with clear_bf_components():           
            if not sf.is_simple_disjuction():
                return False
        
        if not all([
            self._check_sknf_sub_formuls(sf.actor, type="actor"),
            self._check_sknf_sub_formuls(sf.actored, type="actored")
        ]):
            logger.debug("sub formula '%s' has invalid subformuls", sf)
            return False 
        
        return True
    
    @classmethod
    def get_literals(cls, formula):
        if not isinstance(formula, BinaryFormula|UnaryFormula):
            LogicFormula.literals.add(formula)
        elif isinstance(formula, UnaryFormula):
            formula, _ = formula.cut()
            LogicFormula.literals.add(formula.actored if isinstance(formula, UnaryFormula) else formula)
        else:
            if not isinstance(actor := formula.actor, BinaryFormula|UnaryFormula):
                LogicFormula.literals.add(actor)
            elif isinstance(actor := formula.actor, UnaryFormula):
                actor, _ = actor.cut()
                LogicFormula.literals.add(actor.actored if isinstance(actor, UnaryFormula) else actor)
            else:
                LogicFormula.get_literals(formula.actor)

            if not isinstance(actored := formula.actored, BinaryFormula|UnaryFormula):
                LogicFormula.literals.add(actored)
            elif isinstance(actored := formula.actored, UnaryFormula):
                actored, _ = actored.cut()
                LogicFormula.literals.add(actored.actored if isinstance(actored, UnaryFormula) else actored)
            else:
                LogicFormula.get_literals(formula.actored)

        return LogicFormula.literals


if __name__ == '__main__':
    try:
        test_valid_sknf()
        logger.info("All tests ale passed!!!")
    except AssertionError as e:
        logger.error("Tests Failed!!!")
    
    # while True:
    #     formula = input("Enter formula: ")
    #     a = LogicFormula(formula)
    #     logger.info("formula '%s' is %s", a.raw_formula, a.is_sknf())
