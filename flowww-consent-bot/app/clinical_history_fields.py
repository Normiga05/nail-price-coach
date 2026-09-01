"""Lista de enfermedades/condiciones del cuestionario de Historia Clínica,
tomada tal cual del formulario real de la clínica. Vive en un solo lugar
para que el formulario (HTML) y el PDF generado usen exactamente los mismos
campos, en el mismo orden.
"""

DISEASES = [
    ("diabetes", "Diabetes"),
    ("marcapasos", "Es portador/a de marcapasos"),
    ("hipertension", "Hipertensión arterial"),
    ("hepatitis", "Hepatitis"),
    ("tiroides", "Problemas de tiroides"),
    ("higado", "Problemas del hígado"),
    ("cardiacas", "Enfermedades cardiacas"),
    ("mareos", "Se desmaya o marea con facilidad"),
    ("vih_sida", "VIH/SIDA"),
    ("cancer", "Cáncer"),
    ("artritis_lupus", "Artritis / lupus / otra enfermedad inmunológica"),
    ("queloides", "Queloides / problemas de cicatrización"),
    ("reflujo", "Reflujo, hernia hiatal, gastritis, úlceras"),
    ("hormonales", "Enfermedades hormonales"),
    ("rinones", "Problemas de los riñones, insuficiencia renal"),
    ("anemias", "Anemias / otras enfermedades de la sangre"),
    ("psicologicas", "Enfermedades psicológicas (depresión, gran ansiedad, etc.)"),
    ("neurologica", "Enfermedad neurológica, cerebral, nerviosa, epilepsia"),
    ("bronquitis", "Bronquitis, asma, enfisema"),
    ("alimentacion", "Trastornos de la alimentación (bulimia/anorexia)"),
]
