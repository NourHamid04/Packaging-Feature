import pytest
from inventory.models import UnitsOfMeasurement, PackagingMaterials, PackagingTypes, Items, Warehouse, BillOfMaterials, WorkOrders,PackagingInstructions
from inventory.schemas import (
    UnitsOfMeasurementSchema, PackagingMaterialsSchema, PackagingTypesSchema,
    WarehouseSchema, ItemsSchema, PackagingInstructionsSchema, BillOfMaterialsSchema,
    WorkOrdersSchema, OptimizationInputSchema, OptimizationOutputSchema, 
    PrintLabelRequestSchema, PrintLabelResponseSchema, LabelSchema, 
    RemoveLabelRequestSchema, UpdateLabelStatusRequestSchema, BarcodeAndLabelResponseSchema,
    ValidateBarcodeRequestSchema, ValidateBarcodeResponseSchema, BatchBarcodeRequestSchema, BatchBarcodeResponseSchema
)
from inventory.enums import PackagingLevel
from django.utils import timezone
from datetime import date

@pytest.mark.django_db
def test_units_of_measurement_schema():
    uom = UnitsOfMeasurement.objects.create(name="Kilogram", abbreviation="kg")
    schema = UnitsOfMeasurementSchema.from_orm(uom)
    assert schema.id == uom.id
    assert schema.name == "Kilogram"
    assert schema.abbreviation == "kg"

@pytest.mark.django_db
def test_packaging_materials_schema():
    pm = PackagingMaterials.objects.create(name="Cardboard", description="Sturdy cardboard", cost=2.5, available_quantity=100.0)
    schema = PackagingMaterialsSchema.from_orm(pm)
    assert schema.id == pm.id
    assert schema.name == "Cardboard"
    assert schema.description == "Sturdy cardboard"
    assert schema.cost == 2.5
    assert schema.available_quantity == 100.0

@pytest.mark.django_db
def test_packaging_types_schema():
    pm = PackagingMaterials.objects.create(name="Plastic", description="Durable plastic", cost=1.5, available_quantity=200.0)
    pt = PackagingTypes.objects.create(name="Box", description="Plastic box", weight=0.5, volume=1.0, length=30.0, width=30.0, height=30.0, material=pm, cost=1.0, quantity=50, level=PackagingLevel.PRIMARY)
    schema = PackagingTypesSchema.from_orm(pt)
    assert schema.id == pt.id
    assert schema.name == "Box"
    assert schema.description == "Plastic box"
    assert schema.weight == 0.5
    assert schema.volume == 1.0
    assert schema.length == 30.0
    assert schema.width == 30.0
    assert schema.height == 30.0
    assert schema.material.name == "Plastic"
    assert schema.cost == 1.0
    assert schema.quantity == 50
    assert schema.level == PackagingLevel.PRIMARY

@pytest.mark.django_db
def test_warehouse_schema():
    pm = PackagingMaterials.objects.create(name="Plastic", description="Durable plastic", cost=1.5, available_quantity=200.0)
    pt = PackagingTypes.objects.create(name="Box", description="Plastic box", weight=0.5, volume=1.0, length=30.0, width=30.0, height=30.0, material=pm, cost=1.0, quantity=50, level=PackagingLevel.PRIMARY)
    wh = Warehouse.objects.create(code="WH001", name="Main Warehouse", warehouse_type=1, description="Primary storage", total_capacity=1000, available_capacity=500)
    schema = WarehouseSchema.from_orm(wh)
    assert schema.id == wh.id
    assert schema.code == "WH001"
    assert schema.name == "Main Warehouse"
    assert schema.warehouse_type == 1
    assert schema.description == "Primary storage"
    assert schema.total_capacity == 1000
    assert schema.available_capacity == 500

@pytest.mark.django_db
def test_items_schema():
    uom = UnitsOfMeasurement.objects.create(name="Piece", abbreviation="pc")
    wh = Warehouse.objects.create(code="WH001", name="Main Warehouse", warehouse_type=1, description="Primary storage", total_capacity=1000, available_capacity=500)
    pm = PackagingMaterials.objects.create(name="Plastic", description="Durable plastic", cost=1.5, available_quantity=200.0)
    pt = PackagingTypes.objects.create(name="Box", description="Plastic box", weight=0.5, volume=1.0, length=30.0, width=30.0, height=30.0, material=pm, cost=1.0, quantity=50, level=PackagingLevel.PRIMARY)
    item = Items.objects.create(name="Item1", description="Sample item", type="Type1", uom=uom, cost=10.0, weight=1.0, volume=1.0, length=10.0, width=10.0, height=10.0, packaging_type=pt, stock_quantity=100, reorder_level=10, warehouse=wh)
    schema = ItemsSchema.from_orm(item)
    assert schema.id == item.id
    assert schema.name == "Item1"
    assert schema.description == "Sample item"
    assert schema.type == "Type1"
    assert schema.uom.name == "Piece"
    assert schema.uom.abbreviation == "pc"
    assert schema.cost == 10.0
    assert schema.weight == 1.0
    assert schema.volume == 1.0
    assert schema.length == 10.0
    assert schema.width == 10.0
    assert schema.height == 10.0
    assert schema.packaging_type.name == "Box"
    assert schema.packaging_type.description == "Plastic box"
    assert schema.stock_quantity == 100
    assert schema.reorder_level == 10
    assert schema.warehouse.name == "Main Warehouse"
    assert schema.warehouse.description == "Primary storage"

@pytest.mark.django_db
def test_packaging_instructions_schema():
    pt = PackagingTypes.objects.create(name="Box", description="Plastic box", weight=0.5, volume=1.0, length=30.0, width=30.0, height=30.0, material=PackagingMaterials.objects.create(name="Plastic", description="Durable plastic", cost=1.5, available_quantity=200.0), cost=1.0, quantity=50, level=PackagingLevel.PRIMARY)
    pi = PackagingInstructions.objects.create(name="Instruction1", description="Sample instruction", packaging_type=pt, steps="Step1, Step2", required_tools="Tool1, Tool2")
    schema = PackagingInstructionsSchema.from_orm(pi)
    assert schema.id == pi.id
    assert schema.name == "Instruction1"
    assert schema.description == "Sample instruction"
    assert schema.packaging_type.name == "Box"
    assert schema.steps == "Step1, Step2"
    assert schema.required_tools == "Tool1, Tool2"

@pytest.mark.django_db
def test_bill_of_materials_schema():
    uom = UnitsOfMeasurement.objects.create(name="Piece", abbreviation="pc")
    wh = Warehouse.objects.create(code="WH001", name="Main Warehouse", warehouse_type=1, description="Primary storage", total_capacity=1000, available_capacity=500)
    pm = PackagingMaterials.objects.create(name="Plastic", description="Durable plastic", cost=1.5, available_quantity=200.0)
    pt = PackagingTypes.objects.create(name="Box", description="Plastic box", weight=0.5, volume=1.0, length=30.0, width=30.0, height=30.0, material=pm, cost=1.0, quantity=50, level=PackagingLevel.PRIMARY)
    item = Items.objects.create(name="Item1", description="Sample item", type="Type1", uom=uom, cost=10.0, weight=1.0, volume=1.0, length=10.0, width=10.0, height=10.0, packaging_type=pt, stock_quantity=100, reorder_level=10, warehouse=wh)
    bom = BillOfMaterials.objects.create(product=item, quantity=10.0, unit_cost=10.0, total_cost=100.0)
    schema = BillOfMaterialsSchema.from_orm(bom)
    assert schema.id == bom.id
    assert schema.product == item.id
    assert schema.quantity == 10.0
    assert schema.unit_cost == 10.0
    assert schema.total_cost == 100.0



@pytest.mark.django_db
def test_work_orders_schema():
    # Create required related objects
    uom = UnitsOfMeasurement.objects.create(name="Piece", abbreviation="pc")
    wh = Warehouse.objects.create(code="WH001", name="Main Warehouse", warehouse_type=1, description="Primary storage", total_capacity=1000, available_capacity=500)
    pm = PackagingMaterials.objects.create(name="Plastic", description="Durable plastic", cost=1.5, available_quantity=200.0)
    pt = PackagingTypes.objects.create(name="Box", description="Plastic box", weight=0.5, volume=1.0, length=30.0, width=30.0, height=30.0, material=pm, cost=1.0, quantity=50, level=PackagingLevel.PRIMARY)
    item = Items.objects.create(name="Item1", description="Sample item", type="Type1", uom=uom, cost=10.0, weight=1.0, volume=1.0, length=10.0, width=10.0, height=10.0, packaging_type=pt, stock_quantity=100, reorder_level=10, warehouse=wh)
    bom = BillOfMaterials.objects.create(product=item, quantity=10.0, unit_cost=10.0, total_cost=100.0)
    work_order = WorkOrders.objects.create(
        bom=bom,
        status="In Progress",
        start_date=date(2023, 1, 1),
        end_date=date(2023, 1, 31),
        assigned_to="John Doe",
        priority="High"
    )
    schema = WorkOrdersSchema.from_orm(work_order)
    assert schema.id == work_order.id
    assert schema.bom == bom.id
    assert schema.status == "In Progress"
    assert schema.start_date.isoformat() == date(2023, 1, 1).isoformat()
    assert schema.end_date.isoformat() == date(2023, 1, 31).isoformat()
    assert schema.assigned_to == "John Doe"
    assert schema.priority == "High"

def test_optimization_input_schema():
    data = {
        "length": 10.0,
        "width": 10.0,
        "height": 10.0,
        "max_weight": 5.0,
        "max_cost": 50.0
    }
    schema = OptimizationInputSchema(**data)
    assert schema.length == 10.0
    assert schema.width == 10.0
    assert schema.height == 10.0
    assert schema.max_weight == 5.0
    assert schema.max_cost == 50.0

def test_optimization_output_schema():
    data = {
        "material_id": 1,
        "material_name": "Material1",
        "total_cost": 50.0,
        "total_weight": 5.0
    }
    schema = OptimizationOutputSchema(**data)
    assert schema.material_id == 1
    assert schema.material_name == "Material1"
    assert schema.total_cost == 50.0
    assert schema.total_weight == 5.0

def test_print_label_request_schema():
    data = {
        "packaging_type_id": 1,
        "priority": 1
    }
    schema = PrintLabelRequestSchema(**data)
    assert schema.packaging_type_id == 1
    assert schema.priority == 1

def test_print_label_response_schema():
    data = {
        "message": "Label added to printing queue",
        "queue_position": 1
    }
    schema = PrintLabelResponseSchema(**data)
    assert schema.message == "Label added to printing queue"
    assert schema.queue_position == 1

def test_label_schema():
    data = {
        "packaging_type_id": 1,
        "name": "Label1",
        "priority": 1,
        "timestamp": "2023-01-01T00:00:00",
        "status": "pending",
        "barcode_number": "1234567890"
    }
    schema = LabelSchema(**data)
    assert schema.packaging_type_id == 1
    assert schema.name == "Label1"
    assert schema.priority == 1
    assert schema.timestamp == "2023-01-01T00:00:00"
    assert schema.status == "pending"
    assert schema.barcode_number == "1234567890"

def test_remove_label_request_schema():
    data = {
        "packaging_type_id": 1
    }
    schema = RemoveLabelRequestSchema(**data)
    assert schema.packaging_type_id == 1

def test_update_label_status_request_schema():
    data = {
        "packaging_type_id": 1,
        "status": "printed"
    }
    schema = UpdateLabelStatusRequestSchema(**data)
    assert schema.packaging_type_id == 1
    assert schema.status == "printed"

def test_barcode_and_label_response_schema():
    data = {
        "barcode_number": "1234567890",
        "label": "Label1"
    }
    schema = BarcodeAndLabelResponseSchema(**data)
    assert schema.barcode_number == "1234567890"
    assert schema.label == "Label1"

def test_validate_barcode_request_schema():
    data = {
        "barcode_number": "1234567890"
    }
    schema = ValidateBarcodeRequestSchema(**data)
    assert schema.barcode_number == "1234567890"

def test_validate_barcode_response_schema():
    data = {
        "valid": True,
        "packaging_type_info": None
    }
    schema = ValidateBarcodeResponseSchema(**data)
    assert schema.valid is True
    assert schema.packaging_type_info is None

def test_batch_barcode_request_schema():
    data = {
        "packaging_type_ids": [1, 2, 3]
    }
    schema = BatchBarcodeRequestSchema(**data)
    assert schema.packaging_type_ids == [1, 2, 3]

def test_batch_barcode_response_schema():
    data = {
        "packaging_type_id": 1,
        "barcode_number": "1234567890",
        "packaging_type_name": "Box"
    }
    schema = BatchBarcodeResponseSchema(**data)
    assert schema.packaging_type_id == 1
    assert schema.barcode_number == "1234567890"
    assert schema.packaging_type_name == "Box"
