import src.utilities as ut
from pyomo.environ import *
from src.optimization_model import create_supply_model

route = r'20200730 - Datos de entrada del modelo V2 - Prueba modelo.xlsx '
instance = ut.read_excel_file(route)

#Solver information
solvername = 'glpk'
solverpath_exe = 'E:\Documentos\PythonProjects\winglpk-4.65\glpk-4.65\w64\glpsol'
solver = SolverFactory(solvername, executable=solverpath_exe)

#Create model
model = create_supply_model(instance)
solver.solve(model)
model.purchase_quantity.pprint()
model.transport.pprint()
model.inventory.pprint()
model.deconsolidation.pprint()

print(value(model.total_purchase_cost))
print(value(model.objective))


