from enum import Enum, unique

@unique
class Demog(Enum):
    POPULATION = 47.35

    def __str__(self):
        return f'{self.value}M'