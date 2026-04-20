from dataclasses import dataclass

@dataclass
class Images:
    redvelvet = "images/cake_redvelvet.png"
    redvelvet_sliced = "images/cake_redvelvet_sliced.png"

@dataclass
class Assets:
    images = Images()
