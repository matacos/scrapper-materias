from pathlib import Path
from collections import namedtuple
import re
here=Path(".")
path_carreras=Path("carreras")
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
            #materias.append(Materia(codigo_depto,codigo_materia,nombre_materia))
            codigos_depto.add(codigo_depto)

        print(codigos_depto)
        print(materias)
            
        tuples = ",\n   ".join(["('{}','{}')".format(c,nombre) for c in codigos_depto])
        sql.write("insert into departments(code,name) values {};\n".format(tuples))
        
        
        
    materias=[] 
    values=[]
    Correlativas=namedtuple("Correlativas",["cm_para","cd_para","cm_necesario","cd_necesario"])
    for filename in path_carreras.glob("*.txt"):
        carrera=str(filename).split("-")[0].split("/")[1]
        for linea in filename.open().read().split("\n"):
            if len(linea)==0:
                continue;
            print(filename)
            print(linea)

            campos=linea.split("	")
            nombre_materia=campos[1]
            codigo=campos[0]
            codigo_depto=""
            codigo_materia=""
            if len(codigo.split("."))==2:
                codigo_depto=codigo.split(".")[0]
                codigo_materia=codigo.split(".")[1]
            else:
                codigo_depto=codigo.split(" ")[0]
                codigo_materia=codigo.split(" ")[1]
            nombre_materia=campos[1]
            creditos_materia=campos[2]
            correlativas_texto=campos[3]
            correlativas=re.findall("[0-9][0-9]\.[0-9][0-9]",correlativas_texto)
            correlativas_materia=""
            try:
                correlativas_materia=campos[3]#lo de las correlativas lo dejamos para más adelante
            except:
                pass
            
            

            materias.append(Materia(codigo_depto,codigo_materia,nombre_materia))

            values.append("('{}','{}','{}',{})/*{}*/".format(codigo_depto,codigo_materia,carrera,creditos_materia,linea))
    tuples=(",\n    ").join(["('{}','{}','{}')".format(m.codigo_depto,m.codigo_materia,m.nombre) for m in materias])
    sql.write("insert into subjects(department_code,code,name) values {};\n".format(tuples))
    sql.write("insert into credits(department_code,subject_code,degree,amount) values {};\n".format(",\n    ".join(values)))



