from src.entities import *
import os
import pandas as pd
import numpy as np


def read_excel_file(filename, filepath =os.path.dirname(os.getcwd()) + "/data/"):
    route = filepath + filename
    excel_file = pd.ExcelFile(route)
    sheet_names = pd.read_excel(excel_file, 'Conjuntos')
    parameter_sheet_names = pd.read_excel(excel_file, "Parametros")

    instance = Instance()

    # Lectura de datos de los conjuntos
    for row in range(len(sheet_names.index)):
        df = pd.read_excel(excel_file, sheet_names.loc[row, "NombreHoja"])
        type = sheet_names.loc[row, "Tipo"]
        set_name = sheet_names.loc[row, "Parametro"]
        if type == "Origen":
            instance.origins = configure_nodes(df, "Id", "Nombre")

        elif type == "NodoTransferencia":
            if set_name == "Puerto":
                instance.transfer_nodes = configure_ports(instance.transfer_nodes, df, "Id", "Nombre",
                                                          "CostoAlmacenamiento", "InventarioMeta",
                                                          "CostoPenalizacionInventario")

            else:
                instance.transfer_nodes = configure_transfer_nodes(instance.transfer_nodes, df, "Id", "Nombre",
                                                                   "CostoAlmacenamiento")
        elif type == "Destino":
            instance.destinations = configure_nodes(df, "Id", "Nombre")

        elif type == "Nrecursos":
            instance.shared_resources_nodes = configure_shared_resources_nodes(df)

        elif type == "MateriaPrima":
            instance.raw_materials = configure_raw_material(df, "Id", "Nombre", "FactorConversionContenedor")

        elif type == "Tiempo":
            instance.time_limit = df.loc[0, "Tmax"]

        elif type == "Arco":
            instance.arcs = configure_arc(df, "IdArco", "IdOrigen", "IdDestino", "LeadTime")
            #instance.forward_star = configure_forward_star(instance.arcs)
            #instance.reverse_star = configure_reverse_star(instance.arcs)

        elif type == "SubconjuntoTiempo":
            instance.time_subsets = configure_time_subset(df, "Id", "PeriodoInicial", "PeriodoFinal")

        elif type == "Consolidacion":
            instance.consolidation = configure_consolidation(df, "Id", "TipoConsolidacion", "Valor")

    # Lectura de datos de los parámetros

    for row in range(len(parameter_sheet_names.index)):
        df = pd.read_excel(excel_file, parameter_sheet_names.loc[row, "NombreHoja"])
        parameter_type = parameter_sheet_names.loc[row, "Parametro"]

        if parameter_type == "CostoCompra":
            instance.purchase_cost = set_purchase_cost(df, "Id", "IdOrigen", "IdMateriaPrima", "Periodo",
                                                       "CostoCompra")
        elif parameter_type == "DisponibilidadMP":
            instance.raw_material_availability = set_raw_material_availability(df, "Id", "IdOrigen", "IdMateriaPrima",
                                                                               "IdSubperiodo", "DisponibilidadMP")
        elif parameter_type == "CompraMinima":
            instance.min_purchase = set_min_purchase(df, "Id", "IdOrigen", "IdMateriaPrima", "IdSubperiodo",
                                                     "CompraMinima")

        elif parameter_type == "CostoProcesamiento":
            instance.processing_cost = set_processing_cost(df, "Id", "IdNodoIntermedio", "IdMateriaPrima",
                                                           "IdTipoConsolidacion", "CostoProcesamiento")

        elif parameter_type == "CostoDesconsolidacion":
            instance.deconsolidation_cost = set_deconsolidation_cost(df, "Id", "IdNodoIntermedio", "IdMateriaPrima",
                                                                     "CostoDesconsolidacion")

        elif parameter_type == "CostoDevolucion":
            instance.product_return_cost = set_product_return_cost(df, "Id", "IdNodoIntermedio", "Periodo",
                                                                   "CostoDevolucion")

        elif parameter_type == "CapacidadProcesamientoIn":
            instance.processing_capacity_at_the_entrance = \
                set_processing_capacity_at_entrance(df, "Id", "IdNodoIntermedio", "Periodo", "CapacidadProcesamientoIn")

        elif parameter_type == "CapacidadProcesamientoOut":
            instance.processing_capacity_at_the_exit = \
                set_processing_capacity_at_exit(df, "Id", "IdNodoIntermedio", "Periodo", "CapacidadProcesamientoOut")

        elif parameter_type == "CapacidadDesconsolidacion":
            instance.deconsolidation_capacity = set_deconsolidation_capacity(df, "Id", "IdNodoIntermedio", "Periodo",
                                                                             "CapacidadDesconsolidacion")

        elif parameter_type == "CapacidadAlmacenamiento":
            instance.storage_capacity = set_storage_capacity(df, "Id", "IdNodoIntermedio", "Periodo",
                                                             "CapacidadAlmacenamiento")

        elif parameter_type == "RequerimientoMP":
            instance.raw_material_requirement = set_raw_material_requirement(df, "Id", "IdDestino", "IdMateriaPrima",
                                                                             "Periodo", "Requerimiento")

        elif parameter_type == "CapacidadArco":
            instance.arc_capacity = set_arc_capacity(df, "Id", "IdArco", "IdTipoConsolidacion", "Periodo",
                                                     "CapacidadArco")

        elif parameter_type == "CostoTransporte":
            instance.transport_cost = set_transport_cost(df, "Id", "IdArco", "IdTipoConsolidacion", "CostoTransporte")

        elif parameter_type == "ConversionTransporte":
            instance.transport_conversion_factor = \
                set_transport_conversion_factor(df, "Id", "IdMateriaPrima", "IdTipoConsolidacion",
                                                     "FactorConversionTransporte")

        elif parameter_type == "InventarioInicial":
            instance.initial_inventory = set_initial_inventory(df, "Id", "IdNodo", "IdMateriaPrima",
                                                               "IdTipoConsolidacion", "Cantidad")

        elif parameter_type == "WACC":
            instance.wacc = df.loc[0, "WACC"]

        elif parameter_type == "AjusteWacc":
            instance.wacc_adjustment = df.loc[0, "AjusteWacc"]


    return instance





# Métodos para la lectura de los conjuntos del modelo.

def configure_nodes(df: pd.DataFrame, id: str, name: str):
    nodes = []
    for row in range(len(df.index)):
        node = Node(df.loc[row, id], df.loc[row, name])
        nodes.append(node)
    return nodes


def configure_transfer_nodes(nodes: [], df: pd.DataFrame, id: str, name: str, storage_cost: str):
    for row in range(len(df.index)):
        node = TransferNode(df.loc[row, id], df.loc[row, name], df.loc[row, storage_cost])
        nodes.append(node)
    return nodes


def configure_ports(nodes: [], df: pd.DataFrame, id: str, name: str, storage_cost: str, target_inventory: str,
                    penalty_cost: str):
    for row in range(len(df.index)):
        node = Port(df.loc[row, id], df.loc[row, name], df.loc[row, storage_cost], df.loc[row, target_inventory],
                    df.loc[row, penalty_cost])
        nodes.append(node)
    return nodes


def configure_shared_resources_nodes(df: pd.DataFrame):
    nodes = []
    for i in range(len(df.index)):
        n = len(df.values[i])
        list = []
        for j in range(1, n):
            if not pd.isnull(df.values[i, j]):
                list.append(df.values[i, j])
        id = df.values[i, 0]
        node = SharedResourcesNodes(id, list)
        nodes.append(node)
    return nodes


def configure_raw_material(df: pd.DataFrame, id: str, name: str, container_conversion_factor: str):
    raw_materials = []
    for i in range(len(df.index)):
        raw_material = RawMaterial(df.loc[i, id], df.loc[i, name], df.loc[i, container_conversion_factor])
        raw_materials.append(raw_material)
    return raw_materials


def configure_arc(df: pd.DataFrame, id_arc: str, id_origin: str, id_destination: str, lead_time: str):
    arcs = {}
    for i in range(len(df.index)):
        if not np.isnan(df.loc[i, lead_time]):
            arc = ArcFromOrigin(df.loc[i, id_arc], df.loc[i, id_origin], df.loc[i, id_destination],
                                df.loc[i, lead_time])
        else:
            arc = Arc(df.loc[i, id_arc], df.loc[i, id_origin], df.loc[i, id_destination])
        arcs[arc.id] = arc.__dict__
    return arcs

def configure_forward_star(arcs: {}):
    key_value = 'id_origin'
    sorted_list = sorted(arcs.items(), key=lambda x: x[1][key_value], reverse=False)
    pointer = [0]
    origins = [sorted_list[0][1].get(key_value)]
    ordered_arcs = [sorted_list[0][1].get('id')]
    for i in range(1, len(sorted_list)):
        prev_origin = sorted_list[i-1][1].get(key_value)
        dictionary = sorted_list[i][1]
        ordered_arcs.append(dictionary.get('id'))
        if dictionary.get(key_value) != prev_origin:
            origins.append(dictionary.get(key_value))
            pointer.append(i)
    forward_star = ForwardStar(ordered_arcs, pointer, origins)
    return forward_star


def configure_reverse_star(arcs: {}):
    key_value = 'id_destination'
    sorted_list = sorted(arcs.items(), key=lambda x: x[1][key_value], reverse=False)
    pointer = [0]
    ordered_arcs = [sorted_list[0][1].get('id')]
    for i in range(1, len(sorted_list)):
        prev_destination = sorted_list[i-1][1].get(key_value)
        dictionary = sorted_list[i][1]
        ordered_arcs.append(dictionary.get('id'))
        if dictionary.get(key_value) != prev_destination:
            pointer.append(i)
    reverse_star = ReverseStar(ordered_arcs, pointer)
    return reverse_star



def configure_time_subset(df: pd.DataFrame, id: str, lower_time: int, upper_time: int):
    subsets = []
    for row in range(len(df.index)):
        id_subset = df.loc[row, id]
        start_time = df.loc[row, lower_time]
        end_time = df.loc[row, upper_time] + 1
        time_frames = []
        for i in range(start_time, end_time):
            time_frames.append(i)
        subset = TimeSubset(id_subset, time_frames)
        subsets.append(subset)
    return subsets


def configure_consolidation(df: pd.DataFrame, id: str, name: str, consolidation_type: str):
    consolidations = []
    for row in range(len(df.index)):
        consolidation = Consolidation(df.loc[row, id], df.loc[row, name], df.loc[row, consolidation_type])
        consolidations.append(consolidation)
    return consolidations


# Métodos para la lectura de datos de los parámetros del modelo
"""
def set_purchase_cost(df: pd.DataFrame, id: str, id_origin: str, id_raw_material: str, id_time_subset: str,
                      purchase_cost_heading: str):
    purchase_costs = []
    for row in range(len(df.index)):
        purchase_cost = PurchaseCost(df.loc[row, id], df.loc[row, id_origin], df.loc[row, id_raw_material],
                                     df.loc[row, id_time_subset], df.loc[row, purchase_cost_heading])
        purchase_costs.append(purchase_cost)
    return purchase_costs


"""
def set_purchase_cost(df: pd.DataFrame, id: str, id_origin: str, id_raw_material: str, time_frame_heading: str,
                      purchase_cost_heading: str):
    purchase_costs = {}
    for row in range(len(df.index)):
        purchase_cost = PurchaseCost(df.loc[row, id], df.loc[row, id_origin], df.loc[row, id_raw_material],
                                     df.loc[row, time_frame_heading], df.loc[row, purchase_cost_heading])
        my_list = [purchase_cost.id_origin, purchase_cost.id_raw_material, purchase_cost.time_frame]
        my_tuple = tuple(my_list)
        purchase_costs[my_tuple] = purchase_cost.value

    return purchase_costs

"""
def set_min_purchase(df: pd.DataFrame, id: str, id_origin: str, id_raw_material: str, id_time_subset: str,
                     min_purchase_heading: str):
    min_purchases = []
    for row in range(len(df.index)):
        min_purchase = MinPurchase(df.loc[row, id], df.loc[row, id_origin], df.loc[row, id_raw_material],
                                   df.loc[row, id_time_subset], df.loc[row, min_purchase_heading])
        min_purchases.append(min_purchase)
    return min_purchases


def set_raw_material_availability(df: pd.DataFrame, id: str, id_origin: str, id_raw_material: str, id_time_subset: str,
                                  availability_heading: str):
    availabilities = []
    for row in range(len(df.index)):
        material_availability = PurchaseCost(df.loc[row, id], df.loc[row, id_origin], df.loc[row, id_raw_material],
                                             df.loc[row, id_time_subset], df.loc[row, availability_heading])
        availabilities.append(material_availability)
    return availabilities
"""
def set_min_purchase(df: pd.DataFrame, id: str, id_origin: str, id_raw_material: str, id_time_subset: str,
                     min_purchase_heading: str):
    min_purchases = {}
    for row in range(len(df.index)):
        min_purchase = MinPurchase(df.loc[row, id], df.loc[row, id_origin], df.loc[row, id_raw_material],
                                   df.loc[row, id_time_subset], df.loc[row, min_purchase_heading])
        my_list = [min_purchase.id_origin, min_purchase.id_raw_material, min_purchase.id_time_subset]
        my_tuple = tuple(my_list)
        min_purchases[my_tuple] = min_purchase.value
    return min_purchases


def set_raw_material_availability(df: pd.DataFrame, id: str, id_origin: str, id_raw_material: str, id_time_subset: str,
                                  availability_heading: str):
    availabilities = {}
    for row in range(len(df.index)):
        availability = RawMaterialAvailability(df.loc[row, id], df.loc[row, id_origin], df.loc[row, id_raw_material],
                                             df.loc[row, id_time_subset], df.loc[row, availability_heading])
        my_list = [availability.id_origin, availability.id_raw_material, availability.id_time_subset]
        my_tuple = tuple(my_list)
        availabilities[my_tuple] = availability.value
    return availabilities


def set_processing_cost(df: pd.DataFrame, id: str, id_transfer_node: str, id_raw_material: str, id_consolidation: str,
                        cost_heading: str):
    costs = {}
    for row in range(len(df.index)):
        cost = ProcessingCost(df.loc[row, id], df.loc[row, id_transfer_node], df.loc[row, id_raw_material],
                              df.loc[row, id_consolidation], df.loc[row, cost_heading])
        costs[(cost.id_transfer_node, cost.id_raw_material, cost.id_consolidation)] = cost.cost
    return costs


def set_deconsolidation_cost(df: pd.DataFrame, id: str, id_transfer_node: str, id_raw_material: str, cost_heading: str):
    costs = {}
    for row in range(len(df.index)):
        cost = DeconsolidationCost(df.loc[row, id], df.loc[row, id_transfer_node], df.loc[row, id_raw_material],
                                   df.loc[row, cost_heading])
        costs[(cost.id_transfer_node, cost.id_raw_material)] = cost.cost
    return costs


def set_product_return_cost(df: pd.DataFrame, id: str, id_transfer_node: str, time_frame: str, cost_heading: str):
    costs = []
    for row in range(len(df.index)):
        cost = ProductReturnCost(df.loc[row, id], df.loc[row, id_transfer_node], df.loc[row, time_frame],
                                 df.loc[row, cost_heading])
        costs.append(cost)
    return costs


def set_processing_capacity_at_entrance(df: pd.DataFrame, id: str, id_transfer_node: str, time_frame: str,
                                        capacity_heading: str):
    capacities = []
    for row in range(len(df.index)):
        capacity = ProcessingCapacityAtTheEntrance(df.loc[row, id], df.loc[row, id_transfer_node],
                                                   df.loc[row, time_frame], df.loc[row, capacity_heading])
        capacities.append(capacity)
    return capacities


def set_processing_capacity_at_exit(df: pd.DataFrame, id: str, id_transfer_node: str, time_frame: str,
                                    capacity_heading: str):
    capacities = []
    for row in range(len(df.index)):
        capacity = ProcessingCapacityAtTheExit(df.loc[row, id], df.loc[row, id_transfer_node],
                                               df.loc[row, time_frame], df.loc[row, capacity_heading])
        capacities.append(capacity)
    return capacities


def set_deconsolidation_capacity(df: pd.DataFrame, id: str, id_transfer_node: str, time_frame: str,
                                 capacity_heading: str):
    capacities = {}
    for row in range(len(df.index)):
        cap = DeconsolidationCapacity(df.loc[row, id], df.loc[row, id_transfer_node], df.loc[row, time_frame],
                                           df.loc[row, capacity_heading])
        capacities[(cap.id_transfer_node, cap.time_frame)] = cap.capacity
    return capacities


def set_storage_capacity(df: pd.DataFrame, id: str, id_transfer_node: str, time_frame: str, capacity_heading: str):
    capacities = {}
    for row in range(len(df.index)):
        cap = StorageCapacity(df.loc[row, id], df.loc[row, id_transfer_node],
                                   df.loc[row, time_frame], df.loc[row, capacity_heading])
        capacities[(cap.id_transfer_node, cap.time_frame)] = cap.capacity
    return capacities


def set_raw_material_requirement(df: pd.DataFrame, id: str, id_destination: str, id_raw_material: str, time_frame: str,
                                 requirement_heading: str):
    requirements = {}
    for row in range(len(df.index)):
        req = RawMaterialRequirement(df.loc[row, id], df.loc[row, id_destination], df.loc[row, id_raw_material],
                                             df.loc[row, time_frame], df.loc[row, requirement_heading])
        requirements[(req.id_destination, req.id_raw_material, req.time_frame)] = req.requirement
    return requirements


def set_arc_capacity(df: pd.DataFrame, id: str, id_arc, id_consolidation, time_frame, capacity_heading):
    capacities = []
    for row in range(len(df.index)):
        capacity = ArcCapacity(df.loc[row, id], df.loc[row, id_arc], df.loc[row, id_consolidation],
                               df.loc[row, time_frame], df.loc[row, capacity_heading])
        capacities.append(capacity)
    return capacities


def set_transport_cost(df: pd.DataFrame, id: str, id_arc, id_consolidation, cost_heading):
    capacities = []
    for row in range(len(df.index)):
        cost = TransportCost(df.loc[row, id], df.loc[row, id_arc], df.loc[row, id_consolidation],
                               df.loc[row, cost_heading])
        capacities.append(cost)
    return capacities


def set_transport_conversion_factor(df: pd.DataFrame, id: str, id_raw_material: str, id_consolidation: str,
                                         conversion_factor_heading: str):
    factors = []
    for row in range(len(df.index)):
        factor = TransportConversionFactor(df.loc[row, id], df.loc[row, id_raw_material],
                                                df.loc[row, id_consolidation], df.loc[row, conversion_factor_heading])
        factors.append(factor)
    return factors

def set_initial_inventory(df: pd.DataFrame, id: str, id_transfer_node: str, id_raw_material: str,
                          id_consolidation: str, quantity_header: str):
    init = {}
    for row in range(len(df.index)):
        inv = InitialInventory(df.loc[row, id], df.loc[row, id_transfer_node], df.loc[row, id_raw_material],
                                     df.loc[row, id_consolidation], df.loc[row, quantity_header])
        init[(inv.id_transfer_node, inv.id_raw_material, inv.id_consolidation, 0)] = inv.quantity
    return init

