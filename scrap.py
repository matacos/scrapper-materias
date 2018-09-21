from pathlib import Path
from collections import namedtuple
import re
here=Path(".")
Materia=namedtuple("Materia",["codigo_depto","codigo_materia","nombre"])
with Path("materias_deptos.sql").open("w") as sql:
    for filename in here.glob("*.txt"):
        nombre=str(filename).split(".")[0]

        codigos_depto=set()
        materias=[]

        

        for linea in filename.open().read().split("\n"):
            if len(linea)==0:
                continue

            palabras=[p for p in linea.split(" ") if len(p)>0]
            codigo=palabras[0]
            nombre_materia=" ".join(palabras[1:-1])
            codigo_depto=codigo.split(".")[0]
            codigo_materia=codigo.split(".")[1]
            materias.append(Materia(codigo_depto,codigo_materia,nombre_materia))
            codigos_depto.add(codigo_depto)

        print(codigos_depto)
        print(materias)
            
        tuples = ",\n   ".join(["('{}','{}')".format(c,nombre) for c in codigos_depto])
        sql.write("insert into departments(code,name) values {};\n".format(tuples))
        
        tuples=(",\n    ").join(["('{}','{}','{}')".format(m.codigo_depto,m.codigo_materia,m.nombre) for m in materias])
        sql.write("insert into subjects(department_code,code,name) values {};\n".format(tuples))

