# Лабораторная работа №1 по дисциплине ЛОИС
# Выполнена студентом группы 021701 БГУИР Красоцким Максимом Денисовичем
# Файл содержит точку входа в программу, функции проверки правильность формулы и является ли она СКНФ
# 29.03.2023 версия 1  


from settings.constants import *
from settings.exceptions import InvalidFormulaException
from models import BinaryFormula, UnaryFormula
from logs.logs import logger

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
    except InvalidFormulaException as e:
        logger.error("Invalid formula %s", formula)
        raise


def test_valid_formula():
    with open("tests/test-valid-formula.json", "r") as f:
        data = json.load(f)
        
    valid_formulas = data[0]
    invalid_formulas = data[1]
    try:
        for formula, valid in valid_formulas.items():
            result = True
            a = LogicFormula(formula)
            assert result is valid
    except Exception as e:
        logger.error("Exception %s occured while test formula %s", type(e), formula)
        raise
    
    try:
        for formula, invalid in invalid_formulas.items():
            result = False
            a = LogicFormula(formula)
            assert invalid
    except InvalidFormulaException as e:
        assert not invalid  
    except AssertionError as e:
        logger.error("Formula %s is valid", formula)
        raise  
    logger.info("All valid formula tests are passed!")


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
        LogicFormula.literals = set()
    
    
class LogicFormula(): 
    literals = set()

    def __init__(self, formula: str):
        self.raw_formula = formula
        self.formula = None
        self.parse_formula()

    def parse_formula(self):
        formula = self.raw_formula.replace("/\\", CONJUCTION).replace("\\/", DISJUCTION).replace("->", IMPLICATION)
        formula = formula.replace("(", OPEN_BRACKET).replace(")", CLOSE_BRACKET)
        
        if not self.is_valid_syntax(formula):
            raise InvalidFormulaException
        
        if len(formula) == 1:
            self.formula = formula
            if self.formula not in LOGIC_CAPITAL_LETTER|LOGIC_CONSTANT:
                raise InvalidFormulaException
            return

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
        except Exception as e:
            raise InvalidFormulaException

        if len(formula) == 2: 
            self.formula = UnaryFormula(formula) 
        elif len(formula) == 3:
            self.formula = BinaryFormula(formula)
        else:
            raise InvalidFormulaException
        
    def is_valid_syntax(self, formula):
        for ch in formula:
            if (
                ch not in LOGIC_CAPITAL_LETTER|LOGIC_CONSTANT
            ) and (
                ch not in (NEGATIVE, CONJUCTION, DISJUCTION, IMPLICATION, EQUAL, OPEN_BRACKET, CLOSE_BRACKET)
            ):
                return False
        return True
                
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
                if self.formula.action != DISJUCTION:
                    return False
                return self.formula.is_simple_disjuction()

        if not any([
            isinstance(self.formula.actor, BinaryFormula|UnaryFormula),
            isinstance(self.formula.actored, BinaryFormula|UnaryFormula),
        ]):
            logger.debug("formula '%s' has all chars", self.formula)
            return False

        if not all([
            self._check_sknf_sub_formuls(self.formula.actor),
            self._check_sknf_sub_formuls(self.formula.actored)
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

    def _check_sknf_sub_formuls(self, sf) -> bool:
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
            self._check_sknf_sub_formuls(sf.actor),
            self._check_sknf_sub_formuls(sf.actored)
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
        test_valid_formula()
        test_valid_sknf()
        logger.info("All tests ale passed!!!")
    except AssertionError as e:
        logger.error("Tests Failed!!!")
    except InvalidFormulaException as e:
        pass

    # while True:
    #     formula = input("Enter formula: ")
    #     try:
    #         a = LogicFormula(formula)        
    #         logger.info("formula '%s' is %s", a.raw_formula, a.is_sknf())
    #     except InvalidFormulaException as e:
    #         logger.error("Invalid formula!")
