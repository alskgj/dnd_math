
class Example:
    def __init__(self, name, url, notes=None):
        self.name = name
        self.url = url
        self.notes = notes


examples = [
    Example(
        name="Magic Missile vs Chromatic Orb",
        url="http://0.0.0.0:8000/short/W3sic3ViX2F0dGFja3MiOiBbeyJhdHRhY2siOiAi"
            "M2Q0KzMifV19LCB7InN1Yl9hdHRhY2tzIjogW3siYXR0YWNrIjogIis1IDNkOCJ9XX"
            "1d",
        notes="""Magic Missile against Chromatic Orb, with +5 to hit.
Both spells are cast using a first level spell slot."""
    ),
    Example(
        name="Advantage",
        url="http://0.0.0.0:8000/short/W3sic3ViX2F0dGFja3MiOiBbeyJhdHRhY2siOiAi"
            "ICs4IDFkOCs1In1dfSwgeyJzdWJfYXR0YWNrcyI6IFt7ImF0dGFjayI6ICJhZHZhbn"
            "RhZ2UgKzggMWQ4KzUifV19XQ%3D%3D",
        notes="Compare an attack with +8 to hit and 1d8+5 damage with advantage to the same attack without advantage."
    )
]
