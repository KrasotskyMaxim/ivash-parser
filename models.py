# Лабораторная работа №1 по дисциплине ЛОИС
# Выполнена студентом группы 021701 БГУИР Красоцким Максимом Денисовичем
# Файл содержит модели для хранения формул и методы для работы с ними
# 29.03.2023 версия 1  


from constants import *
from exceptions import InvalidFormulaException


class BinaryFormula: 
    
    self_components = []

    def __init__(self, raw_components):
        self.raw_components = raw_components
        self.parse_components()
        
    def __eq__(self, other):
        if not isinstance(other, BinaryFormula):
            if self.action == CONJUCTION:
                return other == self.action or other == self.actored
                
        sc = self._get_all_components(components=set())
        oc = other._get_all_components(components=set())

        return sc == oc or sc in oc

    def parse_components(self):
        if isinstance(actor := self.raw_components[0], list):
            if len(actor) == 2:
                self.actor = UnaryFormula(actor)
            elif len(actor) == 3:
                self.actor = BinaryFormula(actor)
            else:
                raise InvalidFormulaException
        else:
            if actor in LOGIC_CAPITAL_LETTER|LOGIC_CONSTANT:
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

    def is_simple_disjuction(self):
        simple_actor = None
        simple_actored = None
        
        if not isinstance(actor := self.actor, BinaryFormula|UnaryFormula):
            simple_actor = not actor in LOGIC_CONSTANT
        elif isinstance(actor := self.actor, UnaryFormula):
            actor, result = actor.cut()
            simple_actor = result
        else:
            simple_actor = self.actor.is_simple_disjuction()
        
        if not isinstance(actored := self.actored, BinaryFormula):
            if self.actor in self.self_components:
                return False
            else:
                self.self_components.append(self.actor)
        
        if not isinstance(actored := self.actored, BinaryFormula|UnaryFormula):
            simple_actored = not actored in LOGIC_CONSTANT
        elif isinstance(actored := self.actored, UnaryFormula):
            actored, result = actored.cut()
            simple_actored = result
        else:
            simple_actored = self.actored.is_simple_disjuction()

        if not isinstance(actored := self.actored, BinaryFormula):
            if self.actored in self.self_components:
                return False
            else:
                self.self_components.append(self.actored)

        return simple_actor and simple_actored

    def _get_all_components(self, components: set = set()):
        if self.action == CONJUCTION:
            subcomponents = set()
            if not isinstance(actor := self.actor, BinaryFormula|UnaryFormula):
                subcomponents.add(actor)
            elif isinstance(actor := self.actor, UnaryFormula):
                actor, _ = actor.cut()
                subcomponents.add(actor)
            else:
                subcomponents.add(self.actor._get_all_components(components))
                
            if not isinstance(actored := self.actored, BinaryFormula|UnaryFormula):
                subcomponents.add(actored)
            elif isinstance(actored := self.actored, UnaryFormula):
                actored, _ = actored.cut()
                subcomponents.add(actored)
            else:
                subcomponents.add(self.actored._get_all_components(components))
                
            subcomponents = frozenset(subcomponents)
            return subcomponents
        else:        
            if not isinstance(actor := self.actor, BinaryFormula|UnaryFormula):
                components.add(actor)
            elif isinstance(actor := self.actor, UnaryFormula):
                actor, _ = actor.cut()
                components.add(actor)
            else:
                self.actor._get_all_components(components)
                
            if not isinstance(actored := self.actored, BinaryFormula|UnaryFormula):
                components.add(actored)
            elif isinstance(actored := self.actored, UnaryFormula):
                actored, _ = actored.cut()
                components.add(actored)
            else:
                self.actored._get_all_components(components)
                
            return frozenset(components)


class UnaryFormula:
    def __init__(self, raw_components):
        self.raw_components = raw_components
        self.parse_components()
        
    def __hash__(self):
        return hash((self.action, self.actored))
        
    def __eq__(self, other):
        if not isinstance(other, UnaryFormula):
            if isinstance(other, str):            
                if other in LOGIC_CAPITAL_LETTER:
                    cut_self, _ = self.cut()
                    if not isinstance(cut_self, str):
                        return False
                    return cut_self == other
            return False

        cut_self, _ = self.cut()
        cut_other, _ = other.cut()
        
        if type(cut_self) != type(cut_other):
            return False
        
        if isinstance(cut_self, UnaryFormula):
            return cut_self.action == cut_other.action and cut_self.actored == cut_other.actored    
        
        return cut_self == cut_other

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
        
    def is_simple(self):
        if not isinstance(self.actored, BinaryFormula|UnaryFormula):
            return not self.actored in LOGIC_CONSTANT
        
        if isinstance(self.actored, BinaryFormula):
            return False
        
        return self.actored.is_simple()
    
    def cut(self, is_unary: bool = True):
        if not self.is_simple():
            return self, False
        
        if not isinstance(self.actored, BinaryFormula|UnaryFormula):
            if not is_unary:
                return self.actored, True
            return UnaryFormula([NEGATIVE, self.actored]), True
        
        return self.actored.cut(not is_unary)
