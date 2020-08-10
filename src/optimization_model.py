import pyomo.environ as pe
from src.entities import *


# Definición de los parámetros del modelo


def create_supply_model(instance: Instance):
    model = pe.ConcreteModel(name="SupplyModel")

    # Definición de conjuntos
    origins = [o.id for o in instance.origins]
    destinations = [d.id for d in instance.destinations]
    transfer_nodes = [i.id for i in instance.transfer_nodes]
    shared_resources_nodes = [i.id for i in instance.shared_resources_nodes]
    arcs = [(i.get('id_origin'), i.get('id_destination')) for i in instance.arcs.values()]
    raw_materials = [m.id for m in instance.raw_materials]
    consolidation = [c.id for c in instance.consolidation]
    time_subsets = [h.id for h in instance.time_subsets]

    model.O = pe.Set(initialize=origins)
    model.I = pe.Set(initialize=transfer_nodes)
    model.D = pe.Set(initialize=destinations)
    model.N = pe.Set(initialize=model.O | model.I | model.D)
    model.Nresources = pe.Set(initialize=shared_resources_nodes)
    model.A = pe.Set(initialize=arcs)
    model.M = pe.Set(initialize=raw_materials)
    model.C = pe.Set(initialize=consolidation)
    model.T = pe.Set(initialize=T_init(instance.time_limit))
    model.H = pe.Set(initialize=time_subsets)

    model.time_subsets = pe.Set(initialize=time_subsets_init(instance.time_subsets))

    # Conjuntos auxiliares

    omt = [key for key in instance.purchase_cost.keys()]
    omh = [key for key in instance.raw_material_availability]
    dmt = [key for key in instance.raw_material_requirement]

    model.OMT = pe.Set(initialize=omt)
    model.OMH = pe.Set(initialize=omh)
    model.AMCT = pe.Set(initialize=amct_set_init(instance, model))
    model.IMCT = pe.Set(initialize=imct_set_init)
    model.DMT = pe.Set(initialize=dmt)

    # Definición de parámetros

    # Parámetros del tipo de consolidación

    model.consolidation_type = pe.Param(model.C, initialize=consolidation_type_init(instance))

    # Parámetros asociados a la compra

    model.purchase_cost = pe.Param(model.O, model.M, model.T, initialize=instance.purchase_cost)
    model.min_purchase = pe.Param(model.O, model.M, model.H, initialize=instance.min_purchase)
    model.raw_material_availability = pe.Param(model.O, model.M, model.H, initialize=instance.raw_material_availability)

    # Parámetros asociados a los arcos

    model.transport_cost = pe.Param(model.A, model.C, initialize=transport_cost_init(instance))
    model.arc_capacity = pe.Param(model.A, model.C, model.T, initialize=arc_capacity_init(instance))
    model.processing_cost = pe.Param(model.I, model.M, model.C, initialize=instance.processing_cost)

    # Parámetros de los nodos intermedios

    model.initial_inventory = pe.Param(model.I, model.M, model.C, initialize=initial_inventory_init(model, instance))
    model.storage_cost = pe.Param(model.I, initialize=storage_cost_init(instance))

    # Parámetros asociados a los destinos de MP

    model.requirement = pe.Param(model.D, model.M, model.T, initialize=instance.raw_material_requirement)

    # Definición de variables de decisión

    model.purchase_quantity = pe.Var(model.OMT, within=pe.NonNegativeReals)
    model.transport = pe.Var(model.AMCT, within=pe.NonNegativeReals)
    model.inventory = pe.Var(model.IMCT, within=pe.NonNegativeReals)
    model.deconsolidation = pe.Var(model.I, model.M, model.T, within=pe.NonNegativeReals)

    # fix_initial_inventory_values(model, instance)

    # Función objetivo

    def total_purchase_cost_rule(model):
        return sum(model.purchase_cost[o, m, t] * model.purchase_quantity[o, m, t]
                   for o in model.O for m in model.M for t in model.T if (o, m, t) in model.OMT)

    model.total_purchase_cost = pe.Expression(rule=total_purchase_cost_rule)

    def total_transport_cost_rule(model):
        return sum(model.transport_cost[i, j, c] * model.transport[i, j, m, c, t]
                   for i, j in model.A for m in model.M for c in model.C for t in model.T
                   if (i, j, m, c, t) in model.AMCT)

    model.total_transport_cost = pe.Expression(rule=total_transport_cost_rule)

    def total_inventory_cost_rule(model):
        return sum(model.inventory[i, m, c, t] * model.storage_cost[i] for i, m, c, t in model.IMCT)

    model.total_inventory_cost = pe.Expression(rule=total_inventory_cost_rule)

    model.logistic_cost = pe.Expression(expr=model.total_transport_cost)

    model.objective = pe.Objective(expr=model.total_purchase_cost + model.logistic_cost + model.total_inventory_cost)

    # Restricciones del modelo

    # Compra entre el valor mínimo y el máximo

    def min_purchase_rule(model, o, m, h):
        if (o, m, h) in model.OMH:
            return sum(model.purchase_quantity[o, m, t] for t in model.time_subsets[h] if (o, m, t) in model.OMT) \
                   >= model.min_purchase[o, m, h]
        else:
            return pe.Constraint.Skip

    model.min_purchase_rule = pe.Constraint(model.O, model.M, model.H, rule=min_purchase_rule)

    def max_availability_rule(model, o, m, h):
        if (o, m, h) in model.OMH:
            return sum(model.purchase_quantity[o, m, t] for t in model.time_subsets[h] if (o, m, t) in model.OMT) \
                   <= model.raw_material_availability[o, m, h]
        else:
            return pe.Constraint.Skip

    model.max_availability_rule = pe.Constraint(model.O, model.M, model.H, rule=max_availability_rule)

    # Restricciones de flujo

    # Lo que se compra está en los arcos de entrada

    def flow_from_origins_rule(model, o, m, t):
        if (o, m, t) in model.OMT:
            return sum(model.transport[o, j, m, c, t] for c in model.C
                       for j in model.N if (o, j, m, c, t) in model.AMCT) == model.purchase_quantity[o, m, t]
        else:
            return pe.Constraint.Skip

    model.flow_from_origins_rule = pe.Constraint(model.O, model.M, model.T, rule=flow_from_origins_rule)

    # Se calcula el inventario en los nodos intermedios, de acuerdo con el flujo de entrada y salida

    def inventory_in_time_one_rule(model, i, m, c):
        if (i, m, c, 1) in model.IMCT:
            return model.inventory[i, m, c, 1] == model.initial_inventory[i, m, c] + \
                   sum(model.transport[k, i, m, c, 1] for k in model.O | model.I if (k, i, m, c, 1) in model.AMCT) - \
                   sum(model.transport[i, j, m, c, 1] for j in model.I | model.D if (i, j, m, c, 1) in model.AMCT) + \
                   model.consolidation_type[c] * model.deconsolidation[i, m, 1]
        else:
            return pe.Constraint.Skip

    model.inventory_in_time_one_rule = pe.Constraint(model.I, model.M, model.C,
                                                     rule=inventory_in_time_one_rule)

    def flow_in_transfer_nodes_rule(model, i, m, c, t):
        if (i, m, c, t) in model.IMCT and t > 1:
            return model.inventory[i, m, c, t] == model.inventory[i, m, c, t - 1] + \
                   sum(model.transport[k, i, m, c, t] for k in model.O | model.I if (k, i, m, c, t) in model.AMCT) - \
                   sum(model.transport[i, j, m, c, t] for j in model.I | model.D if (i, j, m, c, t) in model.AMCT) + \
                   model.consolidation_type[c] * model.deconsolidation[i, m, t]
        else:
            return pe.Constraint.Skip

    model.flow_in_transfer_nodes_rule = pe.Constraint(model.I, model.M, model.C, model.T,
                                                      rule=flow_in_transfer_nodes_rule)

    # Flujo para cumplir los requerimientos de MP en las plantas

    def raw_material_requirement_rule(model, d, m, t):
        if (d, m, t) in model.DMT:
            return sum(model.transport[i, d, m, c, t] for i in model.O | model.I for c in model.C
                       if (i, d, m, c, t) in model.AMCT) >= model.requirement[d, m, t]
        else:
             return pe.Constraint.Skip

    model.raw_material_requirement_rule = pe.Constraint(model.D, model.M, model.T, rule=raw_material_requirement_rule)

    return model



def T_init(time_limit: int):
    frames = []
    for i in range(1, time_limit + 1):
        frames.append(i)
    return frames


def time_subsets_init(values: []):
    init = []
    for h in values:
        value = h.time_frames
        init.append(value)
    return init


def consolidation_type_init(instance: Instance):
    init = {}
    for c in instance.consolidation:
        init[c.id] = c.consolidation_type
    return init


def transport_cost_init(instance: Instance):
    init = {}
    for i in instance.transport_cost:
        arc_dict = instance.arcs.get(i.id_arc)
        arc = (arc_dict.get('id_origin'), arc_dict.get('id_destination'))
        init[arc + (i.id_consolidation,)] = i.cost
    return init


def arc_capacity_init(instance: Instance):
    init = {}
    for i in instance.arc_capacity:
        arc_dict = instance.arcs.get(i.id_arc)
        arc = (arc_dict.get('id_origin'), arc_dict.get('id_destination'))
        init[arc + (i.id_consolidation, i.time_frame,)] = i.capacity
    return init


def amct_set_init(instance: Instance, model):
    init = []
    arc_capacity = arc_capacity_init(instance)
    for i, j in model.A:
        for c in model.C:
            for t in model.T:
                if (i, j, c, t) in arc_capacity:
                    for m in model.M:
                        init.append((i, j, m, c, t))
    return init


def imct_set_init(model):
    init = []
    for i, j, m, c, t in model.AMCT:
        if i in model.I:
            if (i, m, c, t) not in init:
                init.append((i, m, c, t))
                # if (i, m, c, 0) not in init:
                #    init.append((i, m, c, 0))
        if j in model.I:
            if (j, m, c, t) not in init:
                init.append((j, m, c, t))
                # if (j, m, c, 0) not in init:
                #    init.append((j, m, c, 0))
    return init


def fix_initial_inventory_values(model, instance):
    for i in model.I:
        for m in model.M:
            for c in model.C:
                if (i, m, c, 0) in model.IMCT:
                    value = instance.initial_inventory.get((i, m, c, 0))
                    if value is None:
                        model.inventory[i, m, c, 0].fix(0)
                    else:
                        model.inventory[i, m, c, 0].fix(value)


def initial_inventory_init(model, instance):
    init = {}
    for i in model.I:
        for m in model.M:
            for c in model.C:
                for t in model.T:
                    if (i, m, c, t) in model.IMCT:
                        value = instance.initial_inventory.get((i, m, c, 0))
                        if value is None:
                            init[i, m, c] = 0
                        else:
                            init[i, m, c] = value
                        continue
    return init

def storage_cost_init(instance: Instance):
    init = {}
    for i in instance.transfer_nodes:
        init[i.id] = i.storage_cost
    return init