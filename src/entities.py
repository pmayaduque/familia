import os
import numpy as np


# Instance

class Instance:
    def __init__(self):
        self.origins = []
        self.transfer_nodes = []
        self.destinations = []
        self.shared_resources_nodes = []
        self.raw_materials = []
        self.time_limit = 0
        self.arcs = []
        self.purchase_cost = []
        self.min_purchase = []
        self.raw_material_availability = []
        self.lead_time = []
        self.processing_cost = []
        self.deconsolidation_cost = []
        self.product_return_cost = []
        self.deconsolidation_capacity = []
        self.processing_capacity_at_the_entrance = []
        self.processing_capacity_at_the_exit = []
        self.storage_capacity = []
        self.raw_material_requirement = []
        self.arc_capacity = []


# Sets

class Node:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Origin(Node):
    def __init__(self, id, name):
        self.id = id
        self.name = name


class TransferNode(Node):
    def __init__(self, id, name, storage_cost):
        self.id = id
        self.name = name
        self.storage_cost = storage_cost


class Port(TransferNode):
    def __init__(self, id, name, storage_cost, target_inventory, penalty_cost):
        self.id = id
        self.name = name
        self.storage_cost = storage_cost
        self.target_inventory = target_inventory
        self.penalty_cost = penalty_cost


class Destination(Node):
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Arc:
    def __init__(self, id, id_origin, id_destination, transportation_cost):
        self.id = id
        self.id_origin = id_origin
        self.id_destination = id_destination
        self.transportation_cost = transportation_cost


class ArcFromOrigin(Arc):
    def __init__(self, id, id_origin, id_destination, transportation_cost, lead_time):
        self.id = id
        self.id_origin = id_origin
        self.id_destination = id_destination
        self.transportation_cost = transportation_cost
        self.lead_time = lead_time

    # ¿Cómo se guardan los arcos de un grafo?
    # Backward star, forward star


class SharedResourcesNodes:
    def __init__(self, id, resources=[]):
        self.id = id
        self.resources = resources


class RawMaterial:
    def __init__(self, id, name, container_conversion_factor, transport_conversion_factor_container,
                 transport_conversion_factor_deconsolidated):
        self.id = id
        self.name = name
        self.container_conversion_factor = container_conversion_factor
        self.transport_conversion_factor_container = transport_conversion_factor_container
        self.transport_conversion_factor_deconsolidated = transport_conversion_factor_deconsolidated


class Consolidation:
    def __init__(self, id, consolidation_type):
        self.id = id
        self.consolidation_type = consolidation_type


# Parámetros

class PurchaseCost:
    def __init__(self, id, id_origin, id_raw_material, time_frame, value):
        self.id = id
        self.id_origin = id_origin
        self.id_raw_material = id_raw_material
        self.value = value
        self.time_frame = time_frame


class RawMaterialAvailability:
    def __init__(self, id, id_origin, id_raw_material, time_frame, value):
        self.id = id
        self.id_origin = id_origin
        self.id_raw_material = id_raw_material
        self.value = value
        self.time_frame = time_frame


class MinPurchase:
    def __init__(self, id, id_origin, id_raw_material, time_frame, value):
        self.id = id
        self.id_origin = id_origin
        self.id_raw_material = id_raw_material
        self.value = value
        self.time_frame = time_frame


class ProcessingCost:
    def __init__(self, id, id_transfer_node, id_raw_material, time_frame, id_consolidation, cost):
        self.id = id
        self.id_transfer_node = id_transfer_node
        self.id_raw_material = id_raw_material
        self.time_frame = time_frame
        self.id_consolidation = id_consolidation
        self.cost = cost


class DeconsolidationCost:
    def __init__(self, id, id_transfer_node, id_raw_material, time_frame, cost):
        self.id = id
        self.id_transfer_node = id_transfer_node
        self.id_raw_material = id_raw_material
        self.time_frame = time_frame
        self.cost = cost


class ProductReturnCost:
    def __init__(self, id, id_transfer_node, time_frame, cost):
        self.id = id
        self.id_transfer_node = id_transfer_node
        self.time_frame = time_frame
        self.cost = cost


class DeconsolidationCapacity:
    def __init__(self, id, id_transfer_node, time_frame, capacity):
        self.id = id
        self.id_transfer_node = id_transfer_node
        self.time_frame = time_frame
        self.capacity = capacity


class ProcessingCapacityAtTheEntrance:
    def __init__(self, id, id_transfer_node, time_frame, capacity):
        self.id = id
        self.id_transfer_node = id_transfer_node
        self.time_frame = time_frame
        self.capacity = capacity


class ProcessingCapacityAtTheExit:
    def __init__(self, id, id_transfer_node, time_frame, capacity):
        self.id = id
        self.id_transfer_node = id_transfer_node
        self.time_frame = time_frame
        self.capacity = capacity


class StorageCapacity:
    def __init__(self, id, id_transfer_node, time_frame, capacity):
        self.id = id
        self.id_transfer_node = id_transfer_node
        self.time_frame = time_frame
        self.capacity = capacity


class RawMaterialRequirement:
    def __init__(self, id, id_destination, id_raw_material, time_frame, requirement):
        self.id = id
        self.id_destination = id_destination
        self.id_raw_material = id_raw_material
        self.requirement = requirement
        self.time_frame = time_frame


class ArcCapacity:
    def __init__(self, id, id_arc, id_origin, id_destination, time_frame, id_consolidation, capacity):
        self.id = id
        self.id_arc = id_arc
        self.id_origin = id_origin
        self.id_destination = id_destination
        self.time_frame = time_frame
        self.id_consolidation = id_consolidation
        self.capacity = capacity
