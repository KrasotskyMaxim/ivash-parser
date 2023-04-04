class MyClass:
    def __init__(self, field1, field2):
        self.field1 = field1
        self.field2 = field2
    
    def __eq__(self, other):
        return isinstance(other, MyClass) and self.field1 == other.field1 and self.field2 == other.field2

# пример использования
my_list = [MyClass('value1', 10), MyClass('value2', 20)]
new_obj = MyClass('value1', 10)

if new_obj in my_list:
    print("Объект с такими полями уже есть в списке")
