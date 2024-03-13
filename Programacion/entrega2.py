from gurobipy import Model, GRB, quicksum
from collections import defaultdict

U = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
M = []
N = []
Lista1 = defaultdict(list)

list_cursos = []
list_salas = []

dd_s_aforo = {}  # salas
dd_s_wifi = {}

dd_s_curso = defaultdict(dict)  # cursos
dd_s_modulo = defaultdict(dict)

with open('cursos.csv', 'r', encoding = "ISO-8859-1") as cursos:
   for linea in cursos:
        nombre, seccion, modulo, alu_inscritos = linea.strip().split(',')
        if nombre != "Nombre (i)" and alu_inscritos != "Alumnos inscritos (a_i)":
            dd_s_curso[nombre][int(seccion)] = int(alu_inscritos)
            dd_s_modulo[nombre][int(seccion)] = int(modulo)
            Lista1[nombre].append(int(seccion))
            if nombre not in N:
                N.append(nombre)

dd_s_curso = dict(dd_s_curso)
dd_s_modulo = dict(dd_s_modulo)
Lista1 = dict(Lista1)

with open('salas.csv', 'r', encoding = "ISO-8859-1") as salas:
   for linea in salas:
        nombre, c_n, wifi, aforo = linea.strip().split(',')
        if nombre != "Sala (j)":
            dd_s_aforo[nombre] = int(aforo)
            dd_s_wifi[nombre] = int(wifi)
            if nombre not in M:
                M.append(nombre)

dd_s_aforo = dict(dd_s_aforo)
dd_s_wifi = dict(dd_s_wifi)

d_s_m10 = {}
for ramo in dd_s_modulo:
    d_s_m10[ramo] = {}

    for seccion in dd_s_modulo[ramo]:
        d_s_m10[ramo][int(seccion)] = []

        for modulo in U:

            if modulo == dd_s_modulo[ramo][int(seccion)]:
                d_s_m10[ramo][int(seccion)].append(1)

            else:
                d_s_m10[ramo][int(seccion)].append(0)

dd_s_modulo = d_s_m10

subindices = [(i, j, mu, k) for i in N for j in M for mu in U for k in Lista1[i]]

modelo = Model()

# variables

x = modelo.addVars(subindices, vtype=GRB.BINARY, name="x")
y = modelo.addVars(subindices, vtype=GRB.BINARY, name="y")

modelo.addConstrs(quicksum(x[i,j,mu,k] + y[i,j,mu,k] for j in M) <= 1 for i in N for mu in U for k in Lista1[i])
modelo.addConstrs(quicksum(x[i,j,mu,k] + y[i,j,mu,k] for i in N for k in Lista1[i]) <= 1 for j in M for mu in U)
modelo.addConstrs(x[i,j,mu,k] <= dd_s_modulo[i][k][mu-1] for i in N for j in M for mu in U for k in Lista1[i])
modelo.addConstrs(y[i,j,mu,k] <= dd_s_modulo[i][k][mu-1] for i in N for j in M for mu in U for k in Lista1[i])
modelo.addConstrs(x[i,j,mu,k]*(dd_s_curso[i][k] + 1) <= dd_s_aforo[j] for i in N for j in M for mu in U for k in Lista1[i])
modelo.addConstrs(y[i,j,mu,k]*(dd_s_curso[i][k]/2 + 1) <= dd_s_aforo[j] for i in N for j in M for mu in U for k in Lista1[i])
modelo.addConstrs(y[i,j,mu,k]*(dd_s_curso[i][k]/2 + 1) <= dd_s_wifi[j] for i in N for j in M for mu in U for k in Lista1[i])
modelo.addConstrs(quicksum(x[i,j,mu,k] for j in M for mu in U) == quicksum(x[i,j,mu,l] for j in M for mu in U) for i in N for k in Lista1[i] for l in Lista1[i])
modelo.addConstrs(quicksum(y[i,j,mu,k] for j in M for mu in U) == quicksum(y[i,j,mu,l] for j in M for mu in U) for i in N for k in Lista1[i] for l in Lista1[i])

# funcion objetivo

modelo.setObjective(quicksum(
    x[i, j, mu, k] * dd_s_curso[i][k] + y[i, j, mu, k] * (dd_s_curso[i][k] / 2) for i in N for j in M for mu in U for k
    in Lista1[i]), GRB.MAXIMIZE)  # revisar el sub indice k que no esta en el latex

modelo.optimize()

for i in modelo.getVars():
    if round(i.x, 2) > 0:
        print(str(i.VarName) + ": " + str(round(i.x, 2)))

print("\nFunción objetivo: ", str(round(modelo.ObjVal, 2)))