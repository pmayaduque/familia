import os
import numpy as np


# Instance

class Instance:
    def __init__(self):
        self.origins = []
        self.transfer_nodes = []
        self.destinations = []
        self.shared_resources_nodes = []
        self.raw_materials = {}
        self.time_limit = 0
        self.arcs = []
        self.consolidation = []
        self.time_subsets = []
        self.forward_star: ForwardStar
        self.reverse_star: ReverseStar

        self.purchase_cost = {}
        self.min_purchase = {}
        self.raw_material_availability = {}
        self.lead_time = []
        self.processing_cost = []
        self.deconsolidation_cost = {}
        self.product_return_cost = []
        self.deconsolidation_capacity = {}
        self.processing_capacity_at_the_entrance = []
        self.processing_capacity_at_the_exit = []
        self.storage_capacity = {}
        self.raw_material_requirement = []
        self.arc_capacity = []
        self.transport_cost = {}
        self.transport_conversion_factor = []
        self.initial_inventory = []
        self.wacc: float = 0
        self.wacc_adjustment: float = 0


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
    def __init__(self, id, id_origin, id_destination):
        self.id = id
        self.id_origin = id_origin
        self.id_destination = id_destination


class ArcFromOrigin(Arc):
    def __init__(self, id, id_origin, id_destination, lead_time):
        self.id = id
        self.id_origin = id_origin
        self.id_destination = id_destination
        self.lead_time = lead_time

    # ¿Cómo se guardan los arcos de un grafo?
    # Backward star, forward star


class SharedResourcesNodes:
    def __init__(self, id, resources=[]):
        self.id = id
        self.resources = resources


class RawMaterial:
    def __init__(self, id, name, container_conversion_factor):
        self.id = id
        self.name = name
        self.container_conversion_factor = container_conversion_factor


class Consolidation:
    def __init__(self, id, name, consolidation_type):
        self.id = id
        self.name = name
        self.consolidation_type = consolidation_type

class TimeSubset:
    def __init__(self, id: int, time_frames: []):
        self.id: int = id
        self.time_frames = time_frames


# Parámetros

class PurchaseCost:
    def __init__(self, id, id_origin, id_raw_material, time_frame, value: float):
        self.id = id
        self.id_origin = id_origin
        self.id_raw_material = id_raw_material
        self.value = value
        self.time_frame = time_frame


class RawMaterialAvailability:
    def __init__(self, id, id_origin, id_raw_material, id_time_subset, value):
        self.id = id
        self.id_origin = id_origin
        self.id_raw_material = id_raw_material
        self.value = value
        self.id_time_subset = id_time_subset


class MinPurchase:
    def __init__(self, id, id_origin, id_raw_material, id_time_subset, value):
        self.id = id
        self.id_origin = id_origin
        self.id_raw_material = id_raw_material
        self.value = value
        self.id_time_subset = id_time_subset


class ProcessingCost:
    def __init__(self, id, id_transfer_node, id_raw_material, id_consolidation, cost):
        self.id = id
        self.id_transfer_node = id_transfer_node
        self.id_raw_material = id_raw_material
        self.id_consolidation = id_consolidation
        self.cost = cost


class DeconsolidationCost:
    def __init__(self, id, id_transfer_node, id_raw_material, cost):
        self.id = id
        self.id_transfer_node = id_transfer_node
        self.id_raw_material = id_raw_material
        self.cost = cost


class ProductReturnCost:
    def __init__(self, id, id_transfer_node, time_frame, cost):
        self.id = id
        self.id_transfer_node = id_transfer_node
        self.time_frame = time_frame
        self.cost = cost


class InitialInventory:
    def __init__(self, id, id_transfer_node, id_raw_material, id_consolidation, quantity):
        self.id = id
        self.id_transfer_node = id_transfer_node
        self.id_raw_material = id_raw_material
        self.id_consolidation = id_consolidation
        self.quantity = quantity


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
    def __init__(self, id, id_arc, id_consolidation, time_frame, capacity):
        self.id = id
        self.id_arc = id_arc
        self.time_frame = time_frame
        self.id_consolidation = id_consolidation
        self.capacity = capacity


class TransportCost:
    def __init__(self, id, id_arc, id_consolidation, cost):
        self.id = id
        self.id_arc = id_arc
        self.id_consolidation = id_consolidation
        self.cost = cost


class TransportConversionFactor:
    def __init__(self, id: int, id_raw_material: str, id_consolidation: str, conversion_factor: float):
        self.id = id
        self.id_raw_material = id_raw_material
        self.id_consolidation = id_consolidation
        self.conversion_factor = conversion_factor


class ForwardStar:
    def __init__(self, arcs, pointer, origins):
        self.pointer = pointer
        self.origins = origins
        self.arcs = arcs


class ReverseStar:
    def __init__(self, arcs, pointer):
        self.pointer = pointer
        self.arcs = arcs



