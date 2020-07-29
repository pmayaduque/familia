import math
import os
from src.entities import *
import pandas as pd
import numpy as np


def read_excel_file():
    excel_file = pd.ExcelFile(
        r'E:\Dropbox\Dropbox\Daniel Villa\Consultoría\Proyecto Familia\Modelo matemático\20200722 - Datos de entrada del modelo V1.xlsx')
    sheet_names = pd.read_excel(excel_file, 'Main')

    instance = Instance()
    for row in range(len(sheet_names.index)):
        df = pd.read_excel(excel_file, sheet_names.loc[row, "NombreHoja"])
        type = sheet_names.loc[row, "Tipo"]
        if type == "Origen":
            for i in range(len(df.index)):
                origin = Origin(df.loc[i, "Id"], df.loc[i, "Nombre"])
                instance.origins.append(origin)

        elif type == "NodoTransferencia":
            if sheet_names.loc[row, "Parametro"] == "Puerto":
                for i in range(len(df.index)):
                    transfer_node = Port(df.loc[i, "Id"], df.loc[i, "Nombre"], df.loc[i, "CostoAlmacenamiento"],
                                         df.loc[i, "InventarioMeta"], df.loc[i, "CostoPenalizacionInventario"])
                    instance.transfer_nodes.append(transfer_node)

            else:
                for i in range(len(df.index)):
                    transfer_node = TransferNode(df.loc[i, "Id"], df.loc[i, "Nombre"], df.loc[i, "CostoAlmacenamiento"])
                    instance.transfer_nodes.append(transfer_node)


        elif type == "Destino":
            for i in range(len(df.index)):
                destination = Destination(df.loc[i, "Id"], df.loc[i, "Nombre"])
                instance.destinations.append(destination)

        elif type == "Nrecursos":
            for i in range(len(df.index)):
                n = len(df.values[i])
                list = []
                for j in range(1, n):
                    if not pd.isnull(df.values[i, j]):
                        list.append(df.values[i, j])
                id = df.values[i, 0]
                shared_resources = SharedResourcesNodes(id, list)
                instance.shared_resources_nodes.append(shared_resources)


        elif type == "MateriaPrima":
            for i in range(len(df.index)):
                raw_material = RawMaterial(df.loc[i, "Id"], df.loc[i, "Nombre"],
                                           df.loc[i, "FactorConversionContenedor"],
                                           df.loc[i, "FactorConversionTransporteContenedor"],
                                           df.loc[i, "FactorConversionTransporteDesconsolidado"])
                instance.raw_materials.append(raw_material)

        elif type == "Tiempo":
            instance.time_limit = df.loc[0, "Tmax"]

        elif type == "Arco":
            for i in range(len(df.index)):
                if not np.isnan(df.loc[i, "LeadTime"]):
                    arc = ArcFromOrigin(df.loc[i, "IdArco"], df.loc[i, "IdOrigen"], df.loc[i, "IdDestino"],
                                        df.loc[i, "costoTransporte"], df.loc[i, "LeadTime"])
                else:
                    arc = Arc(df.loc[i, "IdArco"], df.loc[i, "IdOrigen"], df.loc[i, "IdDestino"],
                              df.loc[i, "costoTransporte"])
                instance.arcs.append(arc)

    # Leer parámetros de los orígenes

    # Parámetros de compra
    df = pd.read_excel(excel_file, "EjemploCompra")

    for row in range(len(df.index)):
        purchase_cost = PurchaseCost(df.loc[row, "Id"], df.loc[row, "IdOrigen"], df.loc[row, "IdMateriaPrima"],
                                     df.loc[row, "Periodo"], df.loc[row, "costoCompra"])
        raw_material_availability = RawMaterialAvailability(df.loc[row, "Id"], df.loc[row, "IdOrigen"],
                                                            df.loc[row, "IdMateriaPrima"], df.loc[row, "Periodo"],
                                                            df.loc[row, "disponibilidadMP"])
        min_purchase = MinPurchase(df.loc[row, "Id"], df.loc[row, "IdOrigen"], df.loc[row, "IdMateriaPrima"],
                                   df.loc[row, "Periodo"], df.loc[row, "compraMinima"])
        instance.purchase_cost.append(purchase_cost)
        instance.raw_material_availability.append(raw_material_availability)
        instance.min_purchase.append(min_purchase)

    # Costo procesamiento y desconsolidación

    df = pd.read_excel(excel_file, "EjemploCostoProcesamiento")

    for row in range(len(df.index)):
        container_cost = df.loc[row, "CostoProcesamientoContenedor"]
        if not np.isnan(container_cost):
            processing_cost = ProcessingCost(df.loc[row, "Id"], df.loc[row, "IdNodoIntermedio"],
                                             df.loc[row, "IdMateriaPrima"], df.loc[row, "Periodo"], "C1",
                                             df.loc[row, "CostoProcesamientoContenedor"])
            instance.processing_cost.append(processing_cost)

        if not np.isnan(df.loc[row, "CostoProcesamientoDesconsolidado"]):
            processing_cost = ProcessingCost(df.loc[row, "Id"], df.loc[row, "IdNodoIntermedio"],
                                             df.loc[row, "IdMateriaPrima"], df.loc[row, "Periodo"], "C2",
                                             df.loc[row, "CostoProcesamientoDesconsolidado"])
            instance.processing_cost.append(processing_cost)

        deconsolidation_cost = DeconsolidationCost(df.loc[row, "Id"], df.loc[row, "IdNodoIntermedio"],
                                                   df.loc[row, "IdMateriaPrima"], df.loc[row, "Periodo"],
                                                   df.loc[row, "CostoDesconsolidacion"])
        instance.deconsolidation_cost.append(deconsolidation_cost)

    # Capacidades de procesamiento

    df = pd.read_excel(excel_file, "EjemploProcesamiento")

    for row in range(len(df.index)):
        id = df.loc[row, "Id"]
        transfer_node = df.loc[row, "NodoIntermedio"]
        time_frame = df.loc[row, "Periodo"]

        product_return_cost = ProductReturnCost(id, transfer_node, time_frame, df.loc[row, "costoDevolucion"])
        deconsolidation_capacity = DeconsolidationCapacity(id, transfer_node, time_frame,
                                                           df.loc[row, "capacidadDesconsolidacion"])
        input_throughput = InputThroughput(id, transfer_node, time_frame, df.loc[row, "capacidadProcesamientoIn"])
        output_throughput = OutputThroughput(id, transfer_node, time_frame, df.loc[row, "capacidadProcesamientoOut"])
        storage_capacity = StorageCapacity(id, transfer_node, time_frame, df.loc[row, "capacidadAlmacenamiento"])

        # Adding data to the instance
        instance.product_return_cost.append(product_return_cost)
        instance.deconsolidation_capacity.append(deconsolidation_capacity)
        instance.input_throughput.append(input_throughput)
        instance.output_throughput.append(output_throughput)
        instance.storage_capacity.append(storage_capacity)

    # Requerimiento de materia prima
    df = pd.read_excel(excel_file, "EjemploRequerimientoMP")

    for row in range(len(df.index)):
        requirement = RawMaterialRequirement(df.loc[row, "Id"], df.loc[row, "IdDestino"], df.loc[row, "IdMateriaPrima"],
                                             df.loc[row, "Periodo"], df.loc[row, "Requerimiento"])
        instance.raw_material_requirement.append(requirement)

    # Capacidad de los arcos
    df = pd.read_excel(excel_file, "EjemploTransporte")
    for row in range(len(df.index)):
        if df.loc[row, "TipoConsolidacion"] == "Contenedor":
            id_consolidation = "C1"
        else:
            id_consolidation = "C2"
        arc_capacity = ArcCapacity(df.loc[row, "Id"], df.loc[row, "IdArco"], df.loc[row, "IdOrigen"],
                                   df.loc[row, "IdDestino"], df.loc[row, "Periodo"], id_consolidation,
                                   df.loc[row, "capacidadArco"])
        instance.arc_capacity.append(arc_capacity)

    return instance


instance = read_excel_file()

for i in instance.processing_cost:
    print(i.id_consolidation)

"""
new_instance = Instance()
new_instance = read_excel_file()
print(new_instance)
"""
