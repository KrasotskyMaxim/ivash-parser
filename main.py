from constants import *
from exceptions import InvalidFormulaException
from logs import logger


class BinaryFormula: 
    
    self_components = []
    other_components = []
    
    def __init__(self, raw_components):
        self.raw_components = raw_components
        self.parse_components()
        
    def __eq__(self, other):
        if not isinstance(other, BinaryFormula):
            return False
        
        if (
            self.actor == other.actor and self.action == other.action and self.actored == other.actored
        ) or (
            self.actor == other.actored and self.action == other.action and self.actored == other.actor        
        ):
            return True
        
        self.self_components.extend([self.actor, self.actored])
        self.other_components.extend([other.actor, other.actored])
        
        return self.self_components == self.other_components

    def parse_components(self):
        if isinstance(actor := self.raw_components[0], list):
            self.actor = BinaryFormula(actor) if len(actor) == 3 else UnaryFormula(actor)
        else: self.actor = actor
        
        self.action = self.raw_components[1]
        
        if isinstance(actored := self.raw_components[2], list):
            self.actored = BinaryFormula(actored) if len(actored) == 3 else UnaryFormula(actored) 
        else: self.actored = actored
        
    def is_simple_disjuction(self):
        simple_actor = None
        simple_actored = None

        if not isinstance(actor := self.actor, BinaryFormula|UnaryFormula):
            simple_actor = not actor in LOGIC_CONSTANT
        elif isinstance(actor := self.actor, UnaryFormula):
            simple_actor = actor.is_simple()
        else:
            simple_actor = self.actor.is_simple_disjuction()
        
        if not isinstance(actored := self.actored, BinaryFormula|UnaryFormula):
            simple_actored = not actor in LOGIC_CONSTANT
        elif isinstance(actored := self.actored, UnaryFormula):
            simple_actored = actored.is_simple()
        else:
            simple_actored = self.actored.is_simple_disjuction()
        
        return simple_actor and simple_actored


class UnaryFormula:
    def __init__(self, raw_components):
        self.raw_components = raw_components
        self.parse_components()
        
    def __eq__(self, other):
        if not isinstance(other, UnaryFormula):
            return False
        
        return self.action == other.action and self.actored == other.actored

    def parse_components(self):
        self.action = self.raw_components[0]
        
        if isinstance(actored := self.raw_components[1], list):
            self.actored = BinaryFormula(actored) if len(actored) == 3 else UnaryFormula(actored) 
        else: self.actored = actored
        
    def is_simple(self):
        if not isinstance(self.actored, BinaryFormula|UnaryFormula):
            return not self.actored in LOGIC_CONSTANT
        
        if isinstance(self.actored, BinaryFormula):
            return False
        
        return self.actored.is_simple()

    
class LogicFormula(): 
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
            return self.formula.is_simple()
        
        if self.formula.action != CONJUCTION:
            logger.debug("formula '%s' has not conjuction", self.formula)
            return self.formula.is_simple_disjuction()

        try:
            if self.formula.actor == self.formula.actored:
                logger.debug("formula %s has equal sub_formuls")
                return False
        except Exception as e:
            raise
        finally:
            BinaryFormula.self_components = []
            BinaryFormula.other_components = []

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
        
        return True


    def _check_sknf_sub_formuls(self, sf) -> bool:
        if not isinstance(sf, BinaryFormula|UnaryFormula):
            logger.debug("sub formula '%s' of formula '%s' is a char", sf, self.formula)
            return sf not in LOGIC_CONSTANT
        
        if isinstance(sf, UnaryFormula):
            logger.debug("sub formula '%s' of formula '%s' if UnaryFormula", sf, self.formula)
            return sf.is_simple()

        if sf.action != DISJUCTION:
            logger.debug("sub formula '%s' of formula '%s' has not disjuction", sf, self.formula)
            return False

        if not all([
            self._check_sknf_sub_formuls(sf.actor),
            self._check_sknf_sub_formuls(sf.actored)
        ]):
            logger.debug("sub formula '%s' has invalid subformuls", sf)
            return False 
        
        return True

if __name__ == '__main__':
    while True:
        formula = input("Enter formula: ")
        a = LogicFormula(formula)
        logger.info("formula '%s' is %s", a.raw_formula, a.is_sknf())
    
# A - True +
# 1 - False +
# (!A) - True +
# (!(!A)) - True +
# (A/\A) - False +
# (A/\(!A)) - True +
# (A/\B) - False +
# (A\/B) - True +
# (A\/A) - False
# (A\/(!A)) - True +
# ((A\/(!B))/\((!B)\/A)) - False +
# ((A\/B)/\((!A)\/B)) - True +
# ((A\/(B\/C))/\((!C)\/(A\/B))) - True
# ((A\/(B\/C))/\(C\/(B\/A))) - False

