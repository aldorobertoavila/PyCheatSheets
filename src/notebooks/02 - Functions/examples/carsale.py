from enum import Enum, unique

@unique
class Brand(Enum):
    AUDI = 'Audi'
    BMW = 'BMW'
    CADILLAC = 'Cadillac'
    CHEVROLET = 'Chevrolet'
    DODGE = 'Dodge'
    FORD = 'Ford'

def ask(brand : Brand):
    print(f'Hello, costumer! Are you interested in {brand.value} cars?')