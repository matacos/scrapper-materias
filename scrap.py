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
    Correlatividad=namedtuple("Correlatividad",["cm_para","cd_para","cm_necesario","cd_necesario"])
    correlativas=[]
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


            

            correlativas_materia=""
            try:
                correlativas_texto=campos[3]
                correlativas_normales=re.findall("[0-9][0-9]\.[0-9][0-9]",correlativas_texto)
                for correlativa_normal in correlativas_normales:
                    codigo_depto_correlativa=correlativa_normal.split(".")[0]
                    codigo_materia_correlativa=correlativa_normal.split(".")[1]
                    correlativas.append(Correlatividad(
                        codigo_materia,
                        codigo_depto,
                        codigo_materia_correlativa,
                        codigo_depto_correlativa
                    ))

                correlativas_raras=re.findall("[A-Z][A-Z][A-Z] [0-9]",correlativas_texto)
                for correlativa_raras in correlativas_raras:
                    codigo_depto_correlativa=correlativa_raras.split(" ")[0]
                    codigo_materia_correlativa=correlativa_raras.split(" ")[1]
                    correlativas.append(Correlatividad(
                        codigo_materia,
                        codigo_depto,
                        codigo_materia_correlativa,
                        codigo_depto_correlativa
                    ))
            except:
                pass
            
            

            materias.append(Materia(codigo_depto,codigo_materia,nombre_materia))

            values.append("('{}','{}','{}',{})/*{}*/".format(codigo_depto,codigo_materia,carrera,creditos_materia,linea))
    tuples=(",\n    ").join(["('{}','{}','{}')".format(m.codigo_depto,m.codigo_materia,m.nombre) for m in materias])
    sql.write("insert into subjects(department_code,code,name) values {};\n".format(tuples))
    sql.write("insert into credits(department_code,subject_code,degree,amount) values {};\n".format(",\n    ".join(values)))



    
    correlative_tuples_text=",\n    ".join([
        "('{}','{}','{}','{}')".format(c.cd_para,c.cm_para,c.cd_necesario,c.cm_necesario) 
        for c in correlativas
    ])
    print("correlative tuples:")
    #print(correlative_tuples_text)
    sql.write("insert into requires(dept,code,dept_required,code_required) values {};\n".format(correlative_tuples_text))



