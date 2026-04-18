from dataclasses import dataclass

@dataclass
class Images:
    bday_cake = "images/bday_cake.png"

@dataclass
class Assets:
    images = Images()
