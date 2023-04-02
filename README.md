# LOIS logic parser

## Example:

> raw_formula = "((A/\\0)->B)"
> 
> logic_formula_obj = LogicFormula(raw_formula)
>
> logic_formula = logic_formula_obj.formula
>
> Output: BinaryFormula object([['A', '/\\', '0'], '->', 'B'])
> 
> print(logic_formula.actor)
>
> Output: BinaryFormula object(['A', '/\\', '0'])
>
> print(logic_formula.action)
>
> Output: '->'
>
> print(logic_formula.actored)
>
> Output: 'B'