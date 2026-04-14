# domino.py

from dataclasses import dataclass

@dataclass(frozen=True)
class Domino:
    """
    An immutable domino tile. Always stored with high >= low.
    e.g. Domino(6, 4) represents [6|4]
    
    We never store orientation here - orientation is decided at play time.
    """

    high: int
    low: int

    def __post_init__(self):
        if self.low > self.high:
            high, low = sorted((self.high, self.low), reverse=True)
            object.__setattr__(self, 'high', high)
            object.__setattr__(self, 'low', low)
        if self.high < 0 or self.low < 0:
            raise ValueError(f"Pip value must be non-negative: {self.high}, {self.low}")
    
    @property
    def pip_count(self) -> int:
            return self.high + self.low
    
    @property
    def is_double(self) -> bool:
         return self.high == self.low
    
    def matches(self, pip: int) -> bool:
         return self.high == pip or self.low == pip
    
    def other_end(self, pip: int) -> int:
         """
         Given that 'pip' is the connecting side, return the outward-facing side.

         e.g. Domino(6, 4).other_end(4) -> 6
              Domino(6, 4).other_end(6) -> 4
         """

         if pip == self.high:
              return self.low
         if pip == self.low:
              return self.high
         else:
            raise ValueError(f"{self} does not have a {pip} end")
         
    def __repr__(self) -> str:
         return f"[{self.high}|{self.low}]"
    
    def __str__(self) -> str:
         return self.__repr__()


if __name__ == "__main__":
    d1 = Domino(6, 4)
    d2 = Domino(4, 6)
    print(d1, d2)
    assert d1 == d2, "Domino(6,4) and Domino(4,6) should be equal"
    print(f"Normalization: {d1} == {d2} ✓")

    # pip_count
    assert Domino(6, 4).pip_count == 10
    print(f"Pip count: {Domino(6,4)}.pip_count == 10 ✓")

    # is_double
    assert Domino(6, 6).is_double
    assert not Domino(6, 4).is_double
    print("Is double: [6|6] is double ✓, [6|4] is not ✓")

    # matches
    assert Domino(6, 4).matches(6)
    assert Domino(6, 4).matches(4)
    assert not Domino(6, 4).matches(5)
    print("Matches: [6|4] matches 6 ✓, matches 4 ✓, not 5 ✓")

    # other_end
    assert Domino(6, 4).other_end(4) == 6
    assert Domino(6, 4).other_end(6) == 4
    assert Domino(6, 6).other_end(6) == 6 
    print("Other end: [6|4].other_end(4)==6 ✓, other_end(6)==4 ✓")

    # doubles
    d_double = Domino(8, 8)
    assert d_double.is_double
    assert d_double.pip_count == 16
    assert d_double.other_end(8) == 8
    print(f"Double behavior: {d_double} pip_count==16, other_end==8 ✓")

    # invalid pip in other_end
    try:
        Domino(6, 4).other_end(5)
        assert False, "Should have raised"
    except ValueError:
        print("Error handling:    other_end(5) on [6|4] raises ValueError ✓")

    print("\nAll checks passed.")