from ninja import ModelSchema
from .models import UnitsOfMeasurement, PackagingTypes, Items, PackagingInstructions, BillOfMaterials, WorkOrders,PackagingMaterials,Warehouse,SalesOrder1,Customer,Supplier
from .enums import PackagingLevel
from typing import List
from pydantic import BaseModel
from typing import Optional
from ninja import Schema,FilterSchema,Field
from datetime import datetime


class UnitsOfMeasurementSchema(ModelSchema):
    class Config:
        model = UnitsOfMeasurement
        model_fields = ['id', 'name', 'abbreviation']
        from_attributes = True


class PackagingMaterialsSchema(ModelSchema):
    class Config:
        model = PackagingMaterials
        model_fields = ['id', 'name', 'description', 'cost', 'available_quantity', 'created_at', 'updated_at']
        from_attributes = True




class ParentPackagingTypeSchema(ModelSchema):
    class Config:
        model = PackagingTypes
        model_fields = ['id', 'name', 'description','cost', 'level', 'parent']
        from_attributes = True

class PackagingTypesSchema(ModelSchema):
    level: PackagingLevel
    material: PackagingMaterialsSchema
    parent: Optional[ParentPackagingTypeSchema] = None

    class Config:
        model = PackagingTypes
        model_fields = [
            'id', 'name', 'description', 'weight', 'volume', 'length',
            'width', 'height', 'material', 'cost', 'quantity', 'level',
            'parent'
        ]
        from_attributes = True

class ParentAssignmentSchema(BaseModel):
    parent_id: int

PackagingTypesSchema.update_forward_refs()


class WarehouseSchema(ModelSchema):
    packaging_materials: Optional[PackagingMaterialsSchema]
    packaging_types: Optional[PackagingTypesSchema]
    class Config:
        model = Warehouse
        model_fields = ['id', 'code', 'name', 'warehouse_type', 'description', 'total_capacity', 'available_capacity','packaging_materials']
        from_attributes = True


class ItemsSchema(ModelSchema):
    warehouse: WarehouseSchema  # Add this line
    packaging_type: PackagingTypesSchema  # Changed to packaging_type
    uom: UnitsOfMeasurementSchema 
    class Config:
        model = Items
        model_fields = [
            'id', 'name', 'description', 'type', 'uom', 'cost', 'weight', 
            'volume', 'length', 'width', 'height', 'packaging_type', 
            'stock_quantity', 'reorder_level', 'warehouse'
        ]
        from_attributes = True



class PackagingInstructionsSchema(ModelSchema):
    packaging_type: PackagingTypesSchema  # Changed to packaging_type
    class Config:
        model = PackagingInstructions
        model_fields = ['id', 'name', 'description', 'packaging_type', 'steps', 'required_tools']
        from_attributes = True



class BillOfMaterialsSchema(ModelSchema):
  
    class Config:
        model = BillOfMaterials
        model_fields = ['id', 'product', 'quantity', 'unit_cost', 'total_cost']
        from_attributes = True


class WorkOrdersSchema(ModelSchema):
    class Config:
        model = WorkOrders
        model_fields = ['id', 'bom', 'status', 'start_date', 'end_date', 'assigned_to', 'priority']
        from_attributes = True


class SalesOrderSchema(ModelSchema):
    packaging_type_ids: List[int] = Field(..., alias='packaging_types', description="List of packaging type IDs")
    customer_id: int = Field(..., alias='customer', description="ID of the customer")

    class Config:
        model = SalesOrder1
        model_fields = ['id', 'order_number', 'order_date','status']
        from_attributes = True


class CustomerSchema(ModelSchema):
    class Config:
        model = Customer
        model_fields = ['id', 'name', 'email', 'phone', 'address']



class SalesOrderResponseSchema(ModelSchema):
    packaging_types: List[PackagingTypesSchema]
    customer: CustomerSchema  # Assuming you have a CustomerSchema defined

    class Config:
        model = SalesOrder1
        model_fields = ['id', 'order_number', 'order_date', 'packaging_types', 'customer','status']
        from_attributes = True


class SupplierSchema(ModelSchema):
    packaging_material_ids: List[int] = Field(..., alias='packaging_materials', description="List of packaging material IDs")

    class Config:
        model = Supplier
        model_fields = ['id', 'name', 'contact_person', 'phone', 'email']
        from_attributes = True

class SupplierResponseSchema(ModelSchema):
    packaging_materials: List[PackagingMaterialsSchema]

    class Config:
        model = Supplier
        model_fields = ['id', 'name', 'contact_person', 'phone', 'email', 'packaging_materials']
        from_attributes = True

#________________________________________________________________________________________________________________________________#




class OptimizationInputSchema(BaseModel):
    length: float
    width: float
    height: float
    max_weight: float
    max_cost: float

class OptimizationOutputSchema(BaseModel):
    material_id: int
    material_name: str
    total_cost: float
    total_weight: float


class FileResponseSchema(Schema):
    filename: str
    content_type: str
    file_data: str  # base64 encoded file data
#________________________________________________________________________________________________________________________________#

class PrintLabelRequestSchema(Schema):
    packaging_type_id: int
    priority: Optional[int] = 1

class PrintLabelResponseSchema(Schema):
    message: str
    queue_position: int

class LabelSchema(Schema):
    packaging_type_id: int
    name: str
    priority: int
    timestamp: str
    status: str
    barcode_number: str
    
class RemoveLabelRequestSchema(Schema):
    packaging_type_id: int


class UpdateLabelStatusRequestSchema(Schema):
    packaging_type_id: int
    status: str

class BarcodeAndLabelResponseSchema(Schema):
    barcode_number: str
    label: str


class ValidateBarcodeRequestSchema(Schema):
    barcode_number: str

class ValidateBarcodeResponseSchema(Schema):
    valid: bool
    packaging_type_info: Optional[PackagingTypesSchema]



class BatchBarcodeRequestSchema(Schema):
    packaging_type_ids: List[int]

class BatchBarcodeResponseSchema(Schema):
    packaging_type_id: int
    barcode_number: str
    packaging_type_name: str


class ItemFilterSchema(FilterSchema):
    name: Optional[str] = None
    type: Optional[str] = None
    warehouse__code: Optional[str] = None
    cost: Optional[float] = None
    # page_num: Optional[int] = 1  
    # page_size: Optional[int] = 10


class PackagingTypeFilterSchema(FilterSchema):
    name: Optional[str] = None
    cost: Optional[float] = None
    material__name: Optional[str] = None


class UnitsOfMeasurementFilterSchema(FilterSchema):
    name: Optional[str] = None
    abbreviation: Optional[str] = None

class PackagingMaterialsFilterSchema(FilterSchema):
    name: Optional[str] = None
    cost: Optional[float] = None
    description: Optional[str] = None 



class WorkOrdersFilterSchema(FilterSchema):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: Optional[int] = None

    

class WarehouseFilterSchema(FilterSchema):
    code: Optional[str] = None
    name: Optional[str] = None
    warehouse_type: Optional[int] = None
    total_capacity: Optional[int] = None
    available_capacity: Optional[int] = None
    packaging_types__name:Optional[str] = None
    packaging_materials__name: Optional[str] = None

class SortingSchema(Schema):
    sort_by: Optional[str] = None
    sort_order: Optional[str] = 'asc'

class SalesOrderFilterSchema(FilterSchema):
    order_number: Optional[str] = None
    customer_name: Optional[str] = None
    order_date: Optional[str] = None

class SupplierFilterSchema(FilterSchema):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None



class MaterialRequestItemSchema(BaseModel):
    material_id: int = Field(..., description="ID of the packaging material")
    quantity: float = Field(..., description="Quantity requested")

class MaterialRequestSchema(BaseModel):
    supplier_id: int = Field(..., description="ID of the supplier")
    material_requests: List[MaterialRequestItemSchema] = Field(..., description="List of material requests")


class PackagingCostUpdateSchema(Schema):
    packaging_type_id: int
    cost: float

class CustomerFilterSchema(FilterSchema):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class PackageRequestSchema(Schema):
    customer_id: int
    packaging_type_ids: List[int]
    order_number: str
    order_date: datetime

class PackageDeliverySchema(Schema):
    order_id: int



class UpdateQuantitySchema(BaseModel):
    quantity: float



class PackagingHierarchyNode(Schema):
    id: int
    name: str
    children: List['PackagingHierarchyNode'] = []


class SalesRecordFilterSchema(FilterSchema):
    order_number: Optional[str] = None
    package_id: Optional[int] = None
    sale_date_start: Optional[datetime] = None
    sale_date_end: Optional[datetime] = None







class BillItemSchema(Schema):
    order_number: str
    package_name: str
    quantity: int
    total_cost: float

class BillSchema1(Schema):
    customer_name: str
    total_amount: float
    details: List[BillItemSchema]



class SalesRecordSchema(Schema):
    order_number: str
    package_id: int
    quantity: int
    total_cost: float
    customer_name: Optional[str]  # Add this field
    status: str  # Add the status field


class CreateSalesSchema(BaseModel):
    order_number: str
    package_id: int
    quantity: int
    customer_id: int

class SalesRecordRequestSchema(BaseModel):
    order_number: str
    package_id: int
    quantity: int
    total_cost: float
    customer_id: int


class PackagingTypeDetail(Schema):
    id: int
    name: str
    cost: float
    count: int

class BillSchema(Schema):
    parent_id: int
    parent_name: str
    parent_cost: float
    total_cost: float
    children_count: int
    details: List[PackagingTypeDetail]

class OrderFulfillmentSchema(BaseModel):
    pending_orders: int
    completed_orders: int
    delayed_orders: int


class InventoryReportSchema(Schema):
    packaging_type_id: int
    packaging_type_name: str
    total_count: int
    total_cost: float

class SupplierOrderReportSchema(Schema):
    supplier_name: str
    material_name: str
    requested_quantity: float
    available_quantity: float
    total_cost: float


class BulkCostUpdateSchema(Schema):
    material_id: int
    new_cost: float

class SupplierMaterialUsageSchema(Schema):
    material_name: str
    total_usage: float
    remaining_stock: float
    average_cost: float