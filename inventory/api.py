from ninja import NinjaAPI

from django.shortcuts import get_object_or_404
from .models import UnitsOfMeasurement, PackagingTypes, Items, PackagingInstructions, BillOfMaterials, WorkOrders,PackagingMaterials,Warehouse,SalesOrder1,Supplier,Customer,SalesRecord
from .schemas import (
    UnitsOfMeasurementSchema, PackagingTypesSchema, ItemsSchema,
    PackagingInstructionsSchema, BillOfMaterialsSchema, WorkOrdersSchema,PackagingMaterialsSchema,OptimizationInputSchema,OptimizationOutputSchema,WarehouseSchema,FileResponseSchema,
    PrintLabelRequestSchema,PrintLabelResponseSchema,LabelSchema,RemoveLabelRequestSchema,UpdateLabelStatusRequestSchema,BarcodeAndLabelResponseSchema,
    ValidateBarcodeRequestSchema,ValidateBarcodeResponseSchema,BatchBarcodeRequestSchema,BatchBarcodeResponseSchema,ItemFilterSchema,PackagingTypeFilterSchema,UnitsOfMeasurementFilterSchema,
    PackagingMaterialsFilterSchema,WorkOrdersFilterSchema,WarehouseFilterSchema,SortingSchema,SalesOrderSchema,SalesOrderResponseSchema,SupplierResponseSchema,SupplierSchema,SalesOrderFilterSchema,SupplierFilterSchema,
    MaterialRequestSchema,PackagingCostUpdateSchema,CustomerSchema,CustomerFilterSchema,PackageRequestSchema,PackageDeliverySchema,ParentAssignmentSchema,UpdateQuantitySchema,PackagingHierarchyNode,SalesRecordFilterSchema,
    BillItemSchema,BillSchema1,SalesRecordSchema,CreateSalesSchema,SalesRecordRequestSchema,PackagingTypeDetail,BillSchema,OrderFulfillmentSchema

)
from typing import List,Optional
from .enums import PackagingLevel
from pydantic import BaseModel, ValidationError
from django.db.models import Sum, Avg
from django.db.models import Count
from ninja.errors import HttpError
from django.db.models import F
from django.db.models import Max
from django.db.models import FloatField
from django.db.models import ExpressionWrapper
from datetime import datetime
from ninja import Schema,Query
from .utils import generate_barcode, generate_label
from django.http import FileResponse
import base64
import random,time
import uuid
from ninja.pagination import paginate, PageNumberPagination
from .permissions import permission_required
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from ninja.security import HttpBearer
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
import datetime
from datetime import date, timedelta

def calculate_total_cost(packaging_type):
    total_cost = packaging_type.cost
    children = PackagingTypes.objects.filter(parent=packaging_type)
    for child in children:
        total_cost += calculate_total_cost(child)
    return total_cost

class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            token_obj = Token.objects.get(key=token)
            return token_obj.user
        except Token.DoesNotExist:
            return None

api = NinjaAPI(auth=GlobalAuth())



class TokenResponseSchema(Schema):
    token: str


#------------------------------------------------------------------------------------------------#


# Error handlers
def bad_request(request, exc):
    return api.create_response(request, {"detail": str(exc)}, status=400)

def not_found(request, exc):
    return api.create_response(request, {"detail": "The requested resource was not found."}, status=404)

def internal_server_error(request, exc):
    return api.create_response(request, {"detail": "Internal server error, please try again later."}, status=500)

def validation_error(request, exc):
    return api.create_response(request, {"detail": str(exc)}, status=422)

# Register exception handlers
api.add_exception_handler(HttpError, bad_request)
api.add_exception_handler(ValidationError, validation_error)
api.add_exception_handler(Exception, internal_server_error)


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'page_size'


@api.get("/warehouses", response=List[WarehouseSchema])
@permission_required('inventory.view_warehouses')
@paginate(CustomPagination)
def get_warehouses(request, filters: WarehouseFilterSchema = Query(...), sorting: SortingSchema = Query(...)):
    try:
        warehouses = Warehouse.objects.all()
        warehouses = filters.filter(warehouses)
        if sorting.sort_by:
            sort_order = '' if sorting.sort_order == 'asc' else '-'
            sort_by_field = sorting.sort_by
            warehouses = warehouses.order_by(f'{sort_order}{sort_by_field}')

        return warehouses

    except Exception as e:
        print(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")



@api.get("/units_of_measurement", response=List[UnitsOfMeasurementSchema], url_name='units_of_measurement')
@paginate(CustomPagination)
@permission_required('inventory.view_unitsofmeasurement')
def get_units_of_measurement(request, filters: UnitsOfMeasurementFilterSchema = Query(...), sorting: SortingSchema = Query(...)):
    try:
        units = UnitsOfMeasurement.objects.all()
        units = filters.filter(units)
        if sorting.sort_by:
            sort_order = '' if sorting.sort_order == 'asc' else '-'
            sort_by_field = sorting.sort_by
            units = units.order_by(f'{sort_order}{sort_by_field}')

        return units

    except Exception as e:
        print(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")



@api.get("/packaging_types", response=List[PackagingTypesSchema], url_name='packaging_types')
@paginate(CustomPagination)
@permission_required('inventory.view_packagingtypes')

def get_packaging_types(request, filters: PackagingTypeFilterSchema = Query(...)):
    packaging_types = PackagingTypes.objects.all()
    packaging_types = filters.filter(packaging_types)

    return packaging_types

@api.get("/items", response=List[ItemsSchema])
@paginate(PageNumberPagination, page_size=10)  # Default page size is 10
@permission_required('inventory.view_items')

def get_items(request, filters: ItemFilterSchema = Query(...)):
    items = Items.objects.all()
    items=filters.filter(items)
    return items


@api.get("/packaging_materials", response=List[PackagingMaterialsSchema])
@paginate(CustomPagination)
@permission_required('inventory.view_packagingmaterials')

def get_packaging_materials(request, filters: PackagingMaterialsFilterSchema = Query(...)):
    packaging_materials = PackagingMaterials.objects.all()
    packaging_materials=filters.filter(packaging_materials)

    return packaging_materials



@api.get("/work_orders", response=List[WorkOrdersSchema])
@paginate(CustomPagination)
@permission_required('inventory.view_workorders')
def get_work_orders(request, filters: WorkOrdersFilterSchema = Query(...)):
    work_orders = WorkOrders.objects.all()
    work_orders=filters.filter(work_orders)
    
    return work_orders

#________________________________________________________________________________________________________________________________#




@api.post("/packaging_materials", response=PackagingMaterialsSchema)
@permission_required('inventory.add_packagingmaterials')

def create_packaging_material(request, payload: PackagingMaterialsSchema):
    try:
        packaging_material = PackagingMaterials.objects.create(**payload.dict())
        return PackagingMaterialsSchema.from_orm(packaging_material)
    except ValidationError as e:
        raise HttpError(400, str(e))


@api.put("/packaging_materials/{packaging_material_id}", response=PackagingMaterialsSchema)
@permission_required('inventory.change_packagingmaterials')
def update_packaging_material(request, packaging_material_id: int, payload: PackagingMaterialsSchema):
    try:
        packaging_material = get_object_or_404(PackagingMaterials, id=packaging_material_id)
        for attr, value in payload.dict().items():
            setattr(packaging_material, attr, value)
        packaging_material.save()
        return PackagingMaterialsSchema.from_orm(packaging_material)
    except ValidationError as e:
        raise HttpError(400, str(e))



@api.delete("/packaging_materials/{packaging_material_id}")
@permission_required('inventory.delete_packagingmaterials')
def delete_packaging_material(request, packaging_material_id: int):
    try:
        packaging_material = get_object_or_404(PackagingMaterials, id=packaging_material_id)
        packaging_material.delete()
        return {"success": True}
    except ValidationError as e:
        raise HttpError(400, str(e))

#----------------------------------------------------------------   --------------------------------#
#CRUD methods FOR ITEMS
# CRUD operations for Items...
@api.post("/items", response=ItemsSchema)
@permission_required('inventory.add_items')
def create_item(request, name: str, description: str, type: str, uom_id: int, cost: float, weight: float, volume: float,
                length: float, width: float, height: float, packaging_type_id: int, stock_quantity: int, reorder_level: int, warehouse_id: int):
    try:
        uom = get_object_or_404(UnitsOfMeasurement, id=uom_id)
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        packaging_type = get_object_or_404(PackagingTypes, id=packaging_type_id)
        
        item = Items.objects.create(
            name=name,
            description=description,
            type=type,
            uom=uom,
            cost=cost,
            weight=weight,
            volume=volume,
            length=length,
            width=width,
            height=height,
            packaging_type=packaging_type,
            stock_quantity=stock_quantity,
            reorder_level=reorder_level,
            warehouse=warehouse
        )
        return ItemsSchema.from_orm(item)
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")


@api.put("/items/{item_id}", response=ItemsSchema)
@permission_required('inventory.change_items')
def update_item(request, item_id: int, name: str, description: str, type: str, uom_id: int, cost: float, weight: float, volume: float,
                length: float, width: float, height: float, packaging_type_id: int, stock_quantity: int, reorder_level: int, warehouse_id: int):
    try:
        item = get_object_or_404(Items, id=item_id)
        uom = get_object_or_404(UnitsOfMeasurement, id=uom_id)
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        packaging_type = get_object_or_404(PackagingTypes, id=packaging_type_id)
        
        item.name = name
        item.description = description
        item.type = type
        item.uom = uom
        item.cost = cost
        item.weight = weight
        item.volume = volume
        item.length = length
        item.width = width
        item.height = height
        item.packaging_type = packaging_type
        item.stock_quantity = stock_quantity
        item.reorder_level = reorder_level
        item.warehouse = warehouse
        item.save()
        return ItemsSchema.from_orm(item)
    except ValidationError as e:
        raise HttpError(400, str(e))
#---------------------------------------------------------------- ----------------------------------#
#CRUD methods FOR uniteofmeasurement


@api.post("/units_of_measurement", response=UnitsOfMeasurementSchema)
@permission_required('inventory.can_create_unit_of_measurement')
def create_unit_of_measurement(request, payload: UnitsOfMeasurementSchema):
    try:
        unit = UnitsOfMeasurement.objects.create(**payload.dict())
        return UnitsOfMeasurementSchema.from_orm(unit)
    except ValidationError as e:
        raise HttpError(400, str(e))


@api.put("/units_of_measurement/{unit_id}", response=UnitsOfMeasurementSchema)
@permission_required('inventory.can_edit_unit_of_measurement')
def update_unit_of_measurement(request, unit_id: int, payload: UnitsOfMeasurementSchema):
    try:
        unit = get_object_or_404(UnitsOfMeasurement, id=unit_id)
        for attr, value in payload.dict().items():
            setattr(unit, attr, value)
        unit.save()
        return UnitsOfMeasurementSchema.from_orm(unit)
    except ValidationError as e:
        raise HttpError(400, str(e))



@api.delete("/units_of_measurement/{unit_id}")
@permission_required('inventory.delete_unitsofmeasurement')
def delete_unit_of_measurement(request, unit_id: int):
    try:
        unit = get_object_or_404(UnitsOfMeasurement, id=unit_id)
        unit.delete()
        return {"success": True}
    except ValidationError as e:
        raise HttpError(400, str(e))
#----------------------------------------------------------------   --------------------------------#
import logging

logger = logging.getLogger(__name__)

@api.post("/packaging_types", response=PackagingTypesSchema)
@permission_required('inventory.add_packagingtypes')
def create_packaging_type(request, payload: PackagingTypesSchema):
    try:
        material_id = payload.material.id
        material = get_object_or_404(PackagingMaterials, id=material_id)
        
        if material.available_quantity < payload.quantity:
            raise HttpError(400, "Not enough material available")

        packaging_type_data = payload.dict()
        packaging_type_data['material'] = material
        
        packaging_type = PackagingTypes.objects.create(**packaging_type_data)
        return PackagingTypesSchema.from_orm(packaging_type)
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HttpError(422, str(e))
    except PackagingMaterials.DoesNotExist:
        logger.error("Packaging material does not exist")
        raise HttpError(400, "Packaging material does not exist")
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")

@api.put("/packaging_types/{packaging_type_id}/assign_parent", response=PackagingTypesSchema)
@permission_required('inventory.change_packagingtypes')
def assign_parent(request, packaging_type_id: int, payload: ParentAssignmentSchema):
    try:
        packaging_type = get_object_or_404(PackagingTypes, id=packaging_type_id)
        parent = get_object_or_404(PackagingTypes, id=payload.parent_id)

        packaging_type.parent = parent
        packaging_type.save()
        return PackagingTypesSchema.from_orm(packaging_type)
    except PackagingTypes.DoesNotExist:
        logger.error("Packaging type or parent does not exist")
        raise HttpError(400, "Packaging type or parent does not exist")
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")


@api.put("/packaging_types/{packaging_type_id}", response=PackagingTypesSchema)
@permission_required('inventory.change_packagingtypes')
def update_packaging_type(request, packaging_type_id: int, payload: PackagingTypesSchema):
    try:
        packaging_type = get_object_or_404(PackagingTypes, id=packaging_type_id)
        material_id = payload.material.id
        material = get_object_or_404(PackagingMaterials, id=material_id)

        if material.available_quantity < payload.quantity:
            raise HttpError(400, "Not enough material available")

        for attr, value in payload.dict().items():
            if attr == "material":
                setattr(packaging_type, attr, material)
            elif attr == "parent":
                if value is not None:
                    parent_id = value['id']
                    parent = get_object_or_404(PackagingTypes, id=parent_id)
                    setattr(packaging_type, attr, parent)
                else:
                    setattr(packaging_type, attr, None)
            else:
                setattr(packaging_type, attr, value)

        packaging_type.save()
        return PackagingTypesSchema.from_orm(packaging_type)
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HttpError(422, str(e))
    except PackagingMaterials.DoesNotExist:
        logger.error("Packaging material does not exist")
        raise HttpError(400, "Packaging material does not exist")
    except PackagingTypes.DoesNotExist:
        logger.error("Parent packaging type does not exist")
        raise HttpError(400, "Parent packaging type does not exist")
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")



@api.delete("/packaging_types/{packaging_type_id}")
@permission_required('inventory.delete_packagingtypes')
def delete_packaging_type(request, packaging_type_id: int):
    try:
        packaging_type = get_object_or_404(PackagingTypes, id=packaging_type_id)
        packaging_type.delete()
        return {"success": True}
    except ValidationError as e:
        raise HttpError(400, str(e))
#________________________________________________________________________________________________________________________________#


                                # Added functionalities other that crud operations:

# #________________________________________________________________________________________________________________________________#







# Endpoint for fetching packaging materials statistics
@api.get("/statistics", response=dict)
@permission_required('inventory.view_statistics')

def get_packaging_materials_statistics(request):
    total_cost = PackagingMaterials.objects.aggregate(total_cost=Sum('cost'))['total_cost']
    average_weight = PackagingTypes.objects.aggregate(average_weight=Avg('weight'))['average_weight']
    average_volume = PackagingTypes.objects.aggregate(average_volume=Avg('volume'))['average_volume']
    total_available_quantity = PackagingMaterials.objects.aggregate(total_quantity=Sum('available_quantity'))['total_quantity']
    average_cost_per_weight = PackagingMaterials.objects.aggregate(avg_cost_per_weight=Avg('cost')/Avg('available_quantity'))['avg_cost_per_weight']
    most_used_material = PackagingMaterials.objects.annotate(usage_count=Count('packagingtypes')).order_by('-usage_count').first()
    inventory_value = PackagingMaterials.objects.aggregate(inventory_value=Sum(F('cost') * F('available_quantity')))['inventory_value']
    out_of_stock_count = PackagingMaterials.objects.filter(available_quantity=0).count()
    
    return {
        "total_cost": total_cost,
        "average_weight": average_weight,
        "average_volume": average_volume,
        "total_available_quantity": total_available_quantity,
        "average_cost_per_weight": average_cost_per_weight,
        "most_used_material": most_used_material.name if most_used_material else None,
        "inventory_value": inventory_value,
        "out_of_stock_count": out_of_stock_count
    }





#________________________________________________________________________________________________________________________________#




@api.get("/usage_report", response=List[dict])
@permission_required('inventory.view_usage_report')

def get_material_usage_report(request):
    # Calculate total usage count for percentage calculations
    total_usage = PackagingMaterials.objects.annotate(
        usage_count=Count('packagingtypes')
    ).aggregate(total_usage=Sum('usage_count'))['total_usage']

    # Generate the usage report with additional fields
    report = PackagingMaterials.objects.annotate(
        usage_count=Count('packagingtypes'),
        total_cost=Sum(ExpressionWrapper(F('cost') * F('packagingtypes__quantity'), output_field=FloatField())),
        last_used=Max('packagingtypes__updated_at'),
    ).values(
        'id', 'name', 'usage_count', 'total_cost', 'last_used'
    )

    # Calculate usage percentage for each item
    for item in report:
        item['usage_percentage'] = (item['usage_count'] / total_usage) * 100 if total_usage else 0

    return list(report)





#________________________________________________________________________________________________________________________________#

@api.post("/packaging_optimization", response=OptimizationOutputSchema)
@permission_required('inventory.optimize_packaging')
def optimize_packaging(request, length: float, width: float, height: float, max_weight: float, max_cost: float):
    try:
        optimal_material = PackagingMaterials.objects.filter(
            packagingtypes__length__lte=length,
            packagingtypes__width__lte=width,
            packagingtypes__height__lte=height,
            packagingtypes__weight__lte=max_weight,
            packagingtypes__cost__lte=max_cost
        ).annotate(
            total_cost=Sum('packagingtypes__cost'),
            total_weight=Sum('packagingtypes__weight')
        ).order_by('total_cost').first()

        if not optimal_material:
            raise HttpError(404, "No suitable material found")

        return {
            "material_id": optimal_material.id,
            "material_name": optimal_material.name,
            "total_cost": optimal_material.total_cost,
            "total_weight": optimal_material.total_weight
        }
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")


#________________________________________________________________________________________________________________________________



class CostFilter(Schema):
    min_cost: Optional[float] = None
    max_cost: Optional[float] = None

@api.get("/filter_by_cost", response=List[PackagingMaterialsSchema])
@permission_required('inventory.filter_by_cost')
def filter_by_cost(request, filters: CostFilter = Query(...)):
    try:
        materials = PackagingMaterials.objects.all()

        # Filtering by cost
        if filters.min_cost is not None:
            materials = materials.filter(cost__gte=filters.min_cost)
        if filters.max_cost is not None:
            materials = materials.filter(cost__lte=filters.max_cost)

        # Annotating additional fields
        materials = materials.annotate(
            remaining_value=ExpressionWrapper(F('cost') * F('available_quantity'), output_field=FloatField())
        ).values(
            'id', 'name', 'description', 'cost', 'available_quantity', 'created_at', 'updated_at', 'remaining_value'
        )

        return list(materials)
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")

    #_______________________________________________________________________________#

#Function that Returns the list of packaging types that match the given name.

class NameFilterSchema:
    name: Optional[str] = None

@api.get("/search_packaging_types", response=List[PackagingTypesSchema])
@permission_required('inventory.search_packagingtypes')

def search_packaging_types(request, name: Optional[str] = Query(None)):
    try:
        packaging_types = PackagingTypes.objects.all()

        # Filtering by name
        if name:
            packaging_types = packaging_types.filter(name__icontains=name)

        return list(packaging_types)
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")


    #------------------------------------------------------------------------------------------------#
    #------------------------------------------------------------------------------------------------#


                                        #WARHOUSE OPERATIONS

    #------------------------------------------------------------------------------------------------#

# CRUD operations for Warehouse


    
@api.post("/warehouses", response=WarehouseSchema)
@permission_required('inventory.add_warehouses')

def create_warehouse(request, code: str, name: str, warehouse_type: int, description: str, total_capacity: int, available_capacity: int, packaging_materials_id: Optional[int] = None, packaging_types_id: Optional[int] = None):
    try:
        warehouse = Warehouse.objects.create(
            code=code,
            name=name,
            warehouse_type=warehouse_type,
            description=description,
            total_capacity=total_capacity,
            available_capacity=available_capacity,
            packaging_materials_id=packaging_materials_id,
            packaging_types_id=packaging_types_id
        )
        return WarehouseSchema.from_orm(warehouse)
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")

@api.put("/warehouses/{warehouse_id}", response=WarehouseSchema)
@permission_required('inventory.change_warehouses')
def update_warehouse(request, warehouse_id: int, code: str, name: str, warehouse_type: int, description: str, total_capacity: int, available_capacity: int, packaging_materials_id: Optional[int] = None, packaging_types_id: Optional[int] = None):
    try:
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        warehouse.code = code
        warehouse.name = name
        warehouse.warehouse_type = warehouse_type
        warehouse.description = description
        warehouse.total_capacity = total_capacity
        warehouse.available_capacity = available_capacity
        warehouse.packaging_materials_id = packaging_materials_id
        warehouse.packaging_types_id = packaging_types_id
        warehouse.save()
        return WarehouseSchema.from_orm(warehouse)
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")

@api.delete("/warehouses/{warehouse_id}")
@permission_required('inventory.delete_warehouses')

def delete_warehouse(request, warehouse_id: int):
    try:
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        warehouse.delete()
        return {"success": True}
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")

#------------------------------------------------------------------------------------------------#
@api.get("/warehouses_overview", response=dict)
@permission_required('inventory.view_warehouses_overview')
def get_warehouses_overview(request):
    try:
        warehouses = Warehouse.objects.all()
        overview = []

        for warehouse in warehouses:
            used_capacity = warehouse.total_capacity - warehouse.available_capacity
            total_initial_capacity = warehouse.total_capacity 
            overview.append({
                "warehouse_id": warehouse.id,
                "total_initial_capacity": total_initial_capacity,
                "used_capacity": used_capacity,
                "available_capacity": warehouse.available_capacity,
            })

        return {"warehouses_overview": overview}
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")



# Explanation of the Function:
# Purpose: To alert the user about items that need to be reordered.
# Logic:
# It filters items in the database where the current stock quantity is less than or equal to the reorder level.
# This means it looks for items that have reached or fallen below the minimum threshold for stock quantity, indicating that these items should be reordered.

@api.get("/reorder_alerts", response=List[ItemsSchema])
@permission_required('inventory.view_reorder_alerts')
def get_reorder_alerts(request):
    try:
        items = Items.objects.filter(stock_quantity__lte=F('reorder_level'))
        return items
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")

    #------------------------------------------------------------------------------------------------#



@api.post("/allocate_materials", response=dict)
@permission_required('inventory.allocate_materials')
def allocate_materials(request, warehouse_id: int, material_id: int, quantity: float):
    try:
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        material = get_object_or_404(PackagingMaterials, id=material_id)

        if warehouse.available_capacity < quantity:
            raise HttpError(400, "Not enough available capacity in the warehouse.")

        if material.available_quantity < quantity:
            raise HttpError(400, "Not enough material available.")

        material.available_quantity -= quantity
        material.save()

        warehouse.available_capacity -= quantity
        warehouse.save()

        return {
            "message": "Materials allocated successfully",
            "remaining_material_quantity": material.available_quantity,
            "remaining_warehouse_capacity": warehouse.available_capacity,
        }
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")




    # Suggest Packaging
@api.post("/suggest_packaging", response=PackagingTypesSchema)
@permission_required('inventory.suggest_packaging')
def suggest_packaging(request, item_id: int):
    item = get_object_or_404(Items, id=item_id)
    suitable_packaging = PackagingTypes.objects.filter(
        length__gte=item.length,
        width__gte=item.width,
        height__gte=item.height,
        weight__gte=item.weight
    ).order_by('cost').first()

    if not suitable_packaging:
        raise HttpError(404, "No suitable packaging type found.")

    return suitable_packaging 

#______________________________________________________________________________________#

                             #barcode and labeling
#______________________________________________________________________________________#






@api.post("/generate_packaging_type_barcode", response=BarcodeAndLabelResponseSchema)
@permission_required('inventory.generate_packaging_type_barcode')
def generate_packaging_type_barcode_endpoint(request, packaging_type_id: int):
    try:
        packaging_type = get_object_or_404(PackagingTypes, id=packaging_type_id)
        timestamp = int(time.time() * 1000)  # Get the current timestamp in milliseconds
        random_number = random.randint(1000, 9999)  # Generate a random 4-digit number
        barcode_number = f"{packaging_type.id}{timestamp}{random_number}"  # Generate a unique barcode number using the packaging type ID, timestamp, and random number
        label = f"{packaging_type.name} - {barcode_number}"  # Generate a label combining packaging type name and barcode number
        
        return {
            "barcode_number": barcode_number,
            "label": label
        }
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")

@api.post("/generate_batch_barcodes", response=List[BatchBarcodeResponseSchema])
@permission_required('inventory.generate_batch_barcodes')
def generate_batch_barcodes(request, payload: BatchBarcodeRequestSchema):
    response = []
    for packaging_type_id in payload.packaging_type_ids:
        packaging_type = get_object_or_404(PackagingTypes, id=packaging_type_id)
        barcode_number = f"{packaging_type.id}{random.randint(1000000000, 9999999999)}"
        response.append({
            "packaging_type_id": packaging_type_id,
            "barcode_number": barcode_number,
            "packaging_type_name": packaging_type.name
        })
    return response


@api.post("/validate_barcode", response=ValidateBarcodeResponseSchema)
@permission_required('inventory.validate_barcode')
def validate_barcode(request, payload: ValidateBarcodeRequestSchema):
    try:
        # Extract the packaging_type_id from the barcode by parsing the initial digits until the packaging type ID ends
        barcode_number = payload.barcode_number
        
        # Assuming the barcode_number follows the format: {packaging_type_id}{timestamp}{random_number}
        # We need to identify and extract the packaging_type_id correctly

        # Assuming packaging_type_id is always a small integer, we need to determine its length
        # Let's say the packaging_type_id is up to 6 digits long
        possible_length = 6

        # Try to find a valid packaging_type_id by extracting the first part of the barcode_number
        packaging_type_id = None
        for length in range(1, possible_length + 1):
            try:
                packaging_type_id = int(barcode_number[:length])
                # Check if this ID exists in the database
                if PackagingTypes.objects.filter(id=packaging_type_id).exists():
                    break
                packaging_type_id = None
            except ValueError:
                continue
        
        if packaging_type_id is None:
            raise PackagingTypes.DoesNotExist

        # Fetch the packaging type information
        packaging_type = PackagingTypes.objects.get(id=packaging_type_id)
        packaging_type_info = PackagingTypesSchema.from_orm(packaging_type)
        
        return {"valid": True, "packaging_type_info": packaging_type_info}
    except PackagingTypes.DoesNotExist:
        return {"valid": False, "packaging_type_info": None}
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")


label_queue = []



@api.post("/print_label", response=PrintLabelResponseSchema)
@permission_required('inventory.print_label')
def print_label(request, packaging_type_id: int, priority: int = 1):
    try:
        packaging_type = get_object_or_404(PackagingTypes, id=packaging_type_id)
        timestamp = int(time.time() * 1000)  # Get the current timestamp in milliseconds
        random_number = random.randint(1000, 9999)  # Generate a random 4-digit number
        barcode_number = f"{packaging_type.id}{timestamp}{random_number}"  # Generate a unique barcode number using the packaging type ID, timestamp, and random number
        label = {
            "packaging_type_id": packaging_type.id,
            "name": f"{packaging_type.name} - {packaging_type.id}",
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "barcode_number": barcode_number  # Add the barcode number to the label
        }

        # Prevent duplicate labels
        if label not in label_queue:
            label_queue.append(label)
            label_queue.sort(key=lambda x: x["priority"])  # Sort by priority
            return {
                "message": "Label added to printing queue",
                "queue_position": label_queue.index(label) + 1,
                "barcode_number": barcode_number  # Return the barcode number
            }
        else:
            return {
                "message": "Label already in the queue",
                "queue_position": label_queue.index(label) + 1,
                "barcode_number": barcode_number  # Return the barcode number
            }
    except ValidationError as e:
        raise HttpError(400, str(e))
    except Exception as e:
        raise HttpError(500, "Internal server error, please try again later.")


    # Prevent duplicate labels
    if label not in label_queue:
        label_queue.append(label)
        label_queue.sort(key=lambda x: x["priority"])  # Sort by priority
        return {
            "message": "Label added to printing queue",
            "queue_position": label_queue.index(label) + 1,
            "barcode_number": barcode_number  # Return the barcode number
        }
    else:
        return {
            "message": "Label already in the queue",
            "queue_position": label_queue.index(label) + 1,
            "barcode_number": barcode_number  # Return the barcode number
        }



@api.get("/label_queue", response=List[LabelSchema])
@permission_required('inventory.view_label_queue')
def get_label_queue(request):
    return label_queue



@api.delete("/remove_label", response=dict)
@permission_required('inventory.remove_label')
def remove_label(request, packaging_type_id: int):
    global label_queue
    label_queue = [label for label in label_queue if label["packaging_type_id"] != packaging_type_id]
    return {"message": "Label removed from the queue"}



@api.patch("/update_label_status", response=dict)
@permission_required('inventory.update_label_status')
def update_label_status(request, payload: UpdateLabelStatusRequestSchema):
    for label in label_queue:
        if label["packaging_type_id"] == payload.packaging_type_id:
            label["status"] = payload.status
            return {"message": "Label status updated"}
    return {"message": "Label not found in the queue"}



#=================================================================================#
#=================================================================================#
                        #Sales orders and Suply chain

# #=================================================================================#

@api.post("/suppliers", response=SupplierResponseSchema)
@permission_required('supply_chain.add_supplier')
def create_supplier(request, payload: SupplierSchema):
    try:
        supplier_data = payload.dict()
        packaging_material_ids = supplier_data.pop('packaging_material_ids', [])
        supplier = Supplier.objects.create(**supplier_data)

        if packaging_material_ids:
            packaging_materials = PackagingMaterials.objects.filter(id__in=packaging_material_ids)
            supplier.packaging_materials.add(*packaging_materials)
        
        supplier.save()
        return SupplierResponseSchema.from_orm(supplier)
    except ValidationError as e:
        print(f"Validation Error: {e}")
        raise HttpError(400, str(e))
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")
    

@api.post("/integration/sales/packaging-requirements/", response={200: dict})
@permission_required('sales.submit_packaging_requirements')
def submit_packaging_requirements(request, sales_order_id: int, packaging_requirements: List[int]):
    try:
        sales_order = get_object_or_404(SalesOrder1, id=sales_order_id)
        packaging_items = PackagingTypes.objects.filter(id__in=packaging_requirements)
        sales_order.packaging_types.add(*packaging_items)
        return {"message": "Packaging requirements submitted successfully"}
    except Exception as e:
        print(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")

@api.get("/sales_orders", response=List[SalesOrderResponseSchema])
@permission_required('sales.view_salesorder')
@paginate(CustomPagination)
def get_sales_orders(request, filters: SalesOrderFilterSchema = Query(...), sorting: SortingSchema = Query(...)):
    try:
        sales_orders = SalesOrder1.objects.all()
        sales_orders = filters.filter(sales_orders)

        if sorting.sort_by:
            sort_order = '' if sorting.sort_order == 'asc' else '-'
            sort_by_field = sorting.sort_by
            sales_orders = sales_orders.order_by(f'{sort_order}{sort_by_field}')

        return sales_orders

    except Exception as e:
        print(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")


@api.get("/suppliers", response=List[SupplierResponseSchema])
@paginate(CustomPagination)
@permission_required('supply_chain.view_supplier')
def get_suppliers(request, filters: SupplierFilterSchema = Query(...), sorting: SortingSchema = Query(...)):
    try:
        suppliers = Supplier.objects.all()
        suppliers = filters.filter(suppliers)
        
        if sorting.sort_by:
            sort_order = '' if sorting.sort_order == 'asc' else '-'
            sort_by_field = sorting.sort_by
            suppliers = suppliers.order_by(f'{sort_order}{sort_by_field}')
            
        return suppliers
    except Exception as e:
        print(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")
    


# Integration with Supply Chain
@api.post("/integration/supply-chain/suppliers/packaging-materials/", response={200: dict})
@permission_required('supply_chain.integrate_packaging_materials')
def integrate_suppliers_packaging_materials(request, supplier_id: int, packaging_materials: List[int]):
    try:
        supplier = get_object_or_404(Supplier, id=supplier_id)
        materials = PackagingMaterials.objects.filter(id__in=packaging_materials)
        supplier.packaging_materials.add(*materials)
        return {"message": "Packaging materials integrated successfully with supplier"}
    except Exception as e:
        print(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")


@api.post("/request-materials", response={200: dict})
@permission_required('supply_chain.request_materials')
def request_materials_from_supplier(request, payload: MaterialRequestSchema):
    try:
        supplier = get_object_or_404(Supplier, id=payload.supplier_id)
        material_requests = payload.material_requests
        response_data = []

        for request_item in material_requests:
            material = get_object_or_404(PackagingMaterials, id=request_item.material_id)

            # Check if supplier has the requested material
            if material in supplier.packaging_materials.all():
                # Assume the supplier can fulfill the request. You can add more logic here if needed.
                response_data.append({
                    "material_id": material.id,
                    "material_name": material.name,
                    "requested_quantity": request_item.quantity,
                    "available_quantity": material.available_quantity,  # Example of useful information
                    "supplier_name": supplier.name
                })
            else:
                response_data.append({
                    "material_id": material.id,
                    "material_name": material.name,
                    "requested_quantity": request_item.quantity,
                    "available_quantity": 0,
                    "supplier_name": supplier.name,
                    "message": "Supplier does not have the requested material"
                })

        return {"message": "Material request processed successfully", "data": response_data}

    except Exception as e:
        print(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")




@api.patch("/integration/finance/costs/packaging/", response={200: dict})
@permission_required('finance.track_packaging_costs')
def track_packaging_costs(request, payload: PackagingCostUpdateSchema):
    try:
        packaging_type = get_object_or_404(PackagingTypes, id=payload.packaging_type_id)
        packaging_type.cost = payload.cost
        packaging_type.save()
        return {"message": "Packaging costs updated successfully", "packaging_type_id": packaging_type.id, "new_cost": packaging_type.cost}
    except Exception as e:
        print(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")


@api.post("/customers", response=CustomerSchema)
@permission_required('sales.add_customer')
def create_customer(request, payload: CustomerSchema):
    try:
        customer = Customer.objects.create(**payload.dict())
        return CustomerSchema.from_orm(customer)
    except ValidationError as e:
        print(f"Validation Error: {e}")
        raise HttpError(400, str(e))
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")

@api.get("/customers", response=List[CustomerSchema])
@paginate(CustomPagination)
@permission_required('sales.view_customer')
def get_customers(request, filters: CustomerFilterSchema = Query(...)):
    try:
        customers = Customer.objects.all()
        customers = filters.filter(customers)

        return customers
    except Exception as e:
        print(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")




@api.post("/customer/deliver-package", response={200: dict})
@permission_required('sales.deliver_package')
def deliver_package(request, payload: PackageDeliverySchema):
    try:
        sales_order = get_object_or_404(SalesOrder1, id=payload.order_id)
        sales_order.status = "Delivered"
        sales_order.delivery_date = timezone.now()
        sales_order.save()
        return {"message": "Package delivered successfully", "order_id": sales_order.id}
    except Exception as e:
        print(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")
    


@api.get("/customer/order-status", response={200: dict})
@permission_required('sales.view_order_status')
def order_status(request, order_id: int):
    try:
        sales_order = get_object_or_404(SalesOrder1, id=order_id)
        return {
            "order_id": sales_order.id,
            "order_number": sales_order.order_number,
            "customer_name": sales_order.customer.name,
            "order_date": sales_order.order_date,
            "status": sales_order.status,
            "packaging_types": [pt.name for pt in sales_order.packaging_types.all()]
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")


@api.get("/packaging_types/{parent_id}/children_count", response=dict)
@permission_required('inventory.view_packagingtypes')
def count_children_packages(request, parent_id: int):
    try:
        parent = get_object_or_404(PackagingTypes, id=parent_id)
        count = PackagingTypes.objects.filter(parent=parent).count()
        return {"parent_id": parent_id, "children_count": count}
    except PackagingTypes.DoesNotExist:
        logger.error("Parent packaging type does not exist")
        raise HttpError(400, "Parent packaging type does not exist")
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")
    


@api.get("/packaging_types/{parent_id}/children", response=List[PackagingTypesSchema])
@permission_required('inventory.view_packagingtypes')
def get_children_packages(request, parent_id: int):
    try:
        parent = get_object_or_404(PackagingTypes, id=parent_id)
        children = PackagingTypes.objects.filter(parent=parent)
        return [PackagingTypesSchema.from_orm(child) for child in children]
    except PackagingTypes.DoesNotExist:
        logger.error("Parent packaging type does not exist")
        raise HttpError(400, "Parent packaging type does not exist")
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")
    


    



@api.put("/packaging_types/{packaging_type_id}/update_quantity", response=PackagingTypesSchema)
@permission_required('inventory.change_packagingtypes')
def update_quantity(request, packaging_type_id: int, payload: UpdateQuantitySchema):
    try:
        packaging_type = get_object_or_404(PackagingTypes, id=packaging_type_id)
        packaging_type.quantity = payload.quantity
        packaging_type.save()
        return PackagingTypesSchema.from_orm(packaging_type)
    except PackagingTypes.DoesNotExist:
        logger.error("Packaging type does not exist")
        raise HttpError(400, "Packaging type does not exist")
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")






@api.get("/packaging_types/{parent_id}/hierarchy", response=PackagingHierarchyNode)
@permission_required('inventory.view_packagingtypes')
def get_packaging_hierarchy(request, parent_id: int):
    try:
        parent = get_object_or_404(PackagingTypes, id=parent_id)
        def build_hierarchy(node):
            children = PackagingTypes.objects.filter(parent=node)
            return {
                "id": node.id,
                "name": node.name,
                "children": [build_hierarchy(child) for child in children]
            }
        hierarchy = build_hierarchy(parent)
        return hierarchy
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")







@api.get("/orders/fulfillment_dashboard", response=OrderFulfillmentSchema)
@permission_required('sales.view_order_status')
def order_fulfillment_dashboard(request):
    try:
        pending_orders = SalesOrder1.objects.filter(status='pending').count()
        completed_orders = SalesOrder1.objects.filter(status='completed').count()
        delayed_orders = pending_orders

        return {
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "delayed_orders": delayed_orders
        }
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")
    



def calculate_total_cost(packaging_type):
    total_cost = packaging_type.cost
    children = PackagingTypes.objects.filter(parent=packaging_type)
    for child in children:
        total_cost += calculate_total_cost(child)
    return total_cost

@api.get("/packaging_types/{parent_id}/total_cost", response=dict)
@permission_required('inventory.view_packagingtypes')
def get_total_cost(request, parent_id: int):
    try:
        parent = get_object_or_404(PackagingTypes, id=parent_id)
        total_cost = calculate_total_cost(parent)
        return {"parent_id": parent_id, "total_cost": total_cost}
    except PackagingTypes.DoesNotExist:
        logger.error("Parent packaging type does not exist")
        raise HttpError(400, "Parent packaging type does not exist")
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")





def calculate_total_cost_and_details(packaging_type):
    details = []
    total_cost = packaging_type.cost
    
    children = PackagingTypes.objects.filter(parent=packaging_type)
    for child in children:
        child_total_cost, child_details = calculate_total_cost_and_details(child)
        total_cost += child_total_cost
        details.append({
            "id": child.id,
            "name": child.name,
            "cost": child.cost,
            "count": 1
        })
        details.extend(child_details)

    return total_cost, details

@api.get("/packaging_types/{parent_id}/package_details", response=BillSchema)
@permission_required('inventory.view_packagingtypes')
def package_details(request, parent_id: int):
    try:
        parent = get_object_or_404(PackagingTypes, id=parent_id)
        total_cost, details = calculate_total_cost_and_details(parent)
        
        children_count = PackagingTypes.objects.filter(parent=parent).count()
        for detail in details:
            children_count += PackagingTypes.objects.filter(parent_id=detail["id"]).count()

        bill = {
            "parent_id": parent.id,
            "parent_name": parent.name,
            "parent_cost": parent.cost,
            "total_cost": total_cost,
            "children_count": children_count,
            "details": details
        }
        return bill
    except PackagingTypes.DoesNotExist:
        logger.error("Parent packaging type does not exist")
        raise HttpError(400, "Parent packaging type does not exist")
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")




@api.post("/sales/create", response=SalesRecordSchema)
@permission_required('sales.add_salesrecord')
def create_sales_record(request, payload: CreateSalesSchema):
    try:
        package = get_object_or_404(PackagingTypes, id=payload.package_id)
        customer = get_object_or_404(Customer, id=payload.customer_id)
        total_cost = calculate_total_cost(package) * payload.quantity
        sale_date = timezone.now()

        sales_record = SalesRecord.objects.create(
            order_number=payload.order_number,
            package=package,
            quantity=payload.quantity,
            total_cost=total_cost,
            customer=customer,
        )

        # Update the inventory for the package and its children
        def update_inventory(package, quantity):
            package.quantity -= quantity
            package.save()
            children = PackagingTypes.objects.filter(parent=package)
            for child in children:
                update_inventory(child, quantity)

        update_inventory(package, payload.quantity)

        return sales_record
    except PackagingTypes.DoesNotExist:
        logger.error("Package does not exist")
        raise HttpError(400, "Package does not exist")
    except Customer.DoesNotExist:
        logger.error("Customer does not exist")
        raise HttpError(400, "Customer does not exist")
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")






@api.get("/sales_records", response=List[SalesRecordSchema])
@permission_required('sales.view_salesrecord')
@paginate(CustomPagination)
def get_sales_records(request, filters: SalesRecordFilterSchema = Query(...), sorting: SortingSchema = Query(...)):
    try:
        sales_records = SalesRecord.objects.all().annotate(
            customer_name=F('customer__name')
        )
        sales_records = filters.filter(sales_records)

        if sorting.sort_by:
            sort_order = '' if sorting.sort_order == 'asc' else '-'
            sort_by_field = sorting.sort_by
            sales_records = sales_records.order_by(f'{sort_order}{sort_by_field}')

        return sales_records

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HttpError(500, "Internal server error, please try again later.")




@api.get("/customers/{customer_id}/bill", response=BillSchema1)
@permission_required('sales.view_salesrecord')
def generate_bill(request, customer_id: int):
    try:
        customer = get_object_or_404(Customer, id=customer_id)
        sales_records = SalesRecord.objects.filter(customer=customer).annotate(
            package_name=F('package__name')
        ).values(
            'order_number', 'package_name', 'quantity', 'total_cost'
        )

        total_amount = sales_records.aggregate(total=Sum('total_cost'))['total'] or 0

        bill_details = [BillItemSchema(
            order_number=record['order_number'],
            package_name=record['package_name'],
            quantity=record['quantity'],
            total_cost=record['total_cost']
        ) for record in sales_records]

        bill = BillSchema1(
            customer_name=customer.name,
            total_amount=total_amount,
            details=bill_details
        )

        return bill

    except Customer.DoesNotExist:
        logger.error("Customer does not exist")
        raise HttpError(400, "Customer does not exist")
    except Exception as e:
        logger.error(f"Internal server error: {str(e)}")
        raise HttpError(500, "Internal server error, please try again later.")
    


