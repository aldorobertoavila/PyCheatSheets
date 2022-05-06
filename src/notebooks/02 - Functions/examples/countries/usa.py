from enum import Enum, unique


@unique
class Demog(Enum):
    POPULATION = 329.5

    def __str__(self):
        return f'{self.value}M'
