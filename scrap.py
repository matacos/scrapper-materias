from pathlib import Path
from collections import namedtuple
import re

def limpiar_codigo_materia(s):
    if "-" in s:
        return s.split("-")[0]
    if "_" in s:
        return s.split("_")[0]
    return s

here=Path(".")
path_carreras=Path("carreras")
Materia=namedtuple("Materia",["codigo_depto","codigo_materia","nombre"])

with Path("materias_deptos.sql").open("w") as sql:
    sql.write("""
        insert into departments(code,name) values
            ('CEX','Facultad de Ciencias Exactas y Naturales');
        insert into departments(code,name) values
            ('FYB','Facultad de Farmacia y Bioquímica');
        insert into departments(code,name) values
            ('AG','Facultad de Agronomía');
    """)

    materias=set()
    for filename in here.glob("*.txt"):
        nombre=str(filename).split(".")[0]

        codigos_depto=set()
        

        

        for linea in filename.open().read().split("\n"):
            if len(linea)==0:
                continue

            palabras=[p for p in linea.split(" ") if len(p)>0]
            codigo=palabras[0]
            nombre_materia=" ".join(palabras[1:-1])
            codigo_depto=codigo.split(".")[0]
            codigo_materia=limpiar_codigo_materia(codigo.split(".")[1])
            codigos_depto.add(codigo_depto)

            materias.add(Materia(codigo_depto,codigo_materia,nombre_materia))

            
        tuples = ",\n   ".join(["('{}','{}')".format(c,nombre) for c in codigos_depto])
        sql.write("insert into departments(code,name) values {};\n".format(tuples))
        
        
        
    values={}
    restricciones=set()
    Restriccion=namedtuple("Restriccion",["cm_para","cd_para","creditos","carrera"])
    Correlatividad=namedtuple("Correlatividad",["cm_para","cd_para","cm_necesario","cd_necesario","carrera"])
    correlativas=set()
    for filename in path_carreras.glob("*.txt"):
        carrera=str(filename).split("-")[0].split("/")[1]
        for linea in filename.open().read().split("\n"):
            if len(linea)==0:
                continue;

            campos=linea.split("	")
            nombre_materia=campos[1]

            codigo=campos[0]
            codigo_depto=""
            codigo_materia=""
            if len(codigo.split("."))==2:
                codigo_depto=codigo.split(".")[0]
                codigo_materia=limpiar_codigo_materia(codigo.split(".")[1])
            else:
                codigo_depto=codigo.split(" ")[0]
                codigo_materia=limpiar_codigo_materia(codigo.split(" ")[1])


            nombre_materia=campos[1]
            creditos_materia=campos[2]
            materias.add(Materia(codigo_depto,codigo_materia,nombre_materia))


            

            try:
                correlativas_texto=campos[3]
                correlativas_normales=re.findall("[0-9][0-9]\.[0-9][0-9]",correlativas_texto)
                for correlativa_normal in correlativas_normales:
                    codigo_depto_correlativa=correlativa_normal.split(".")[0]
                    codigo_materia_correlativa=limpiar_codigo_materia(correlativa_normal.split(".")[1])
                    correlativas.add(Correlatividad(
                        codigo_materia,
                        codigo_depto,
                        codigo_materia_correlativa,
                        codigo_depto_correlativa,
                        carrera
                    ))

                correlativas_raras=re.findall("[A-Z][A-Z][A-Z] [0-9]",correlativas_texto)
                for correlativa_raras in correlativas_raras:
                    codigo_depto_correlativa=correlativa_raras.split(" ")[0]
                    codigo_materia_correlativa=limpiar_codigo_materia(correlativa_raras.split(" ")[1])
                    correlativas.add(Correlatividad(
                        codigo_materia,
                        codigo_depto,
                        codigo_materia_correlativa,
                        codigo_depto_correlativa,
                        carrera
                    ))
                creditos_necesarios = re.findall("\d* créditos",correlativas_texto)
                if len(creditos_necesarios)>0:
                    creditos=creditos_necesarios[0].split(" ")[0]
                    restricciones.add(Restriccion(codigo_materia,codigo_depto,creditos,carrera))
            except Exception as e:
                print(e)
            
            

            materias.add(Materia(codigo_depto,codigo_materia,nombre_materia))

            values[codigo_depto+"."+codigo_materia+"."+carrera]=("('{}','{}','{}',{})/*{}*/".format(codigo_depto,codigo_materia,carrera,creditos_materia,linea))

    materias_filtradas={}
    for m in materias:
        materias_filtradas[m.codigo_depto+"."+m.codigo_materia]=m

    tuples=(",\n    ").join(["('{}','{}','{}')".format(m.codigo_depto,m.codigo_materia,m.nombre) for m in materias_filtradas.values()])
    sql.write("insert into subjects(department_code,code,name) values {};\n".format(tuples))
    sql.write("insert into credits(department_code,subject_code,degree,amount) values {};\n".format(",\n    ".join(list(values.values()))))

    correlative_tuples_text=",\n    ".join([
        "('{}','{}','{}','{}','{}')".format(c.cd_para,c.cm_para,c.cd_necesario,c.cm_necesario,c.carrera) 
        for c in correlativas
    ])
    sql.write("insert into requires(department_code,subject_code,dept_required,code_required,degree) values {};\n".format(correlative_tuples_text))

    requisite_tuples_text=",\n    ".join([
        "('{}','{}',{},'{}')".format(c.cd_para,c.cm_para,c.creditos,c.carrera) 
        for c in restricciones
    ])

    sql.write("insert into requires_credits(department_code,subject_code,amount,degree) values {};\n".format(requisite_tuples_text))

