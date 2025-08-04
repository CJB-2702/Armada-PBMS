# Phase 2: Asset Detail Tables - Detailed Implementation Plan

## Overview
Phase 2 implements the detail table system for extended asset information. This phase creates a flexible, extensible system for storing detailed specifications and configurations for both assets and models. The detail table system uses a virtual template approach to allow dynamic addition of detail information without schema changes.

## Objectives
- Implement detail table infrastructure with virtual templates
- Create specific detail table models for common asset information
- Establish relationships between assets, models, and their detail tables
- Provide a flexible system for future detail table additions
- Ensure proper data integrity and relationships

## Architecture Overview

### Detail Table System Design
The detail table system consists of three main components:

1. **Detail Table Sets**: Container models that group related detail tables
2. **Virtual Templates**: Base classes that provide common functionality
3. **Specific Detail Tables**: Concrete implementations for specific data types

### File Structure
```
app/models/assets/
├── __init__.py
├── build.py                          # Asset models builder
├── detail_virtual_template.py        # Base virtual template classes
├── asset_details/                    # Asset-specific detail tables
│   ├── __init__.py
│   ├── asset_detail_virtual.py       # Asset detail base class
│   ├── purchase_info.py              # Purchase information
│   ├── vehicle_registration.py       # Vehicle registration details
│   └── toyota_warranty_receipt.py    # Toyota-specific warranty info
├── model_details/                    # Model-specific detail tables
│   ├── __init__.py
│   ├── model_detail_virtual.py       # Model detail base class
│   ├── emissions_info.py             # Emissions specifications
│   └── model_info.py                 # General model information
└── detail_table_sets/                # Detail table set containers
    ├── __init__.py
    ├── asset_type_detail_table_set.py   # Asset detail table set
    └── model_detail_table_set.py        # Model detail table set
```

## Implementation Steps

### Step 2.0: Detail Table Infrastructure

#### 2.0.0 Create Virtual Template Base Classes
**File**: `app/models/assets/detail_virtual_template.py`

**Purpose**: Provide base classes for all detail table functionality

**Implementation**:
- Create `DetailTableVirtualTemplate` abstract base class
- Implement common fields: `id`, `created_at`, `created_by_id`, `updated_at`, `updated_by_id`
- Add relationship to `User` for audit trail
- Include abstract methods for detail table operations

**Key Features**:
- Inherits from `UserCreatedBase`
- Provides common CRUD operations
- Supports audit trail functionality
- Enables polymorphic relationships



### Step 2.2: Asset Detail Tables

#### 2.2.1 Asset Detail Virtual Base Class
**File**: `app/models/assets/asset_details/asset_detail_virtual.py`

**Purpose**: Base class for all asset-specific detail tables

**Implementation**:
- Inherit from `DetailTableVirtualTemplate`
- Add relationship to `Asset` via foreign key (not to detail table set)
- Implement asset-specific validation logic
- Provide common asset detail operations
- Support dynamic creation during asset creation process

#### 2.2.2 Purchase Information Detail Table
**File**: `app/models/assets/asset_details/purchase_info.py`

**Purpose**: Store purchase-related information for assets

**Fields**:
- `purchase_date`: Date of purchase
- `purchase_price`: Purchase price
- `purchase_vendor`: Vendor/seller information
- `purchase_order_number`: PO number if applicable
- `warranty_start_date`: Warranty start date
- `warranty_end_date`: Warranty end date
- `purchase_notes`: Additional purchase notes
- `event_id` : link to an event so comments and attachments can be added

**Implementation**:
- Inherit from `AssetDetailVirtual`
- Add purchase-specific validation
- Implement warranty date calculations
- Support vendor information tracking
- Create an Event on insert and link to it

#### 2.2.3 Vehicle Registration Detail Table
**File**: `app/models/assets/asset_details/vehicle_registration.py`

**Purpose**: Store vehicle registration and licensing information

**Fields**:
- `license_plate`: Vehicle license plate number
- `registration_number`: Registration number
- `registration_expiry`: Registration expiry date
- `vin_number`: Vehicle Identification Number
- `state_registered`: State of registration
- `registration_status`: Current registration status
- `insurance_provider`: Insurance company
- `insurance_policy_number`: Insurance policy number
- `insurance_expiry`: Insurance expiry date

**Implementation**:
- Inherit from `AssetDetailVirtual`
- Add vehicle-specific validation
- Implement expiry date tracking
- Support multiple state registrations

#### 2.2.4 Toyota Warranty Receipt Detail Table
**File**: `app/models/assets/asset_details/toyota_warranty_receipt.py`

**Purpose**: Store Toyota-specific warranty and service information

**Fields**:
- `warranty_receipt_number`: Toyota warranty receipt number
- `warranty_type`: Type of warranty (basic, powertrain, etc.)
- `warranty_mileage_limit`: Mileage limit for warranty
- `warranty_time_limit`: Time limit for warranty
- `dealer_name`: Toyota dealer information
- `dealer_contact`: Dealer contact information
- `service_history`: Service history notes
- `warranty_claims`: Warranty claim information

**Implementation**:
- Inherit from `AssetDetailVirtual`
- Add Toyota-specific validation
- Implement warranty tracking
- Support service history

### Step 2.3: Model Detail Tables

#### 2.3.1 Model Detail Virtual Base Class
**File**: `app/models/assets/model_details/model_detail_virtual.py`

**Purpose**: Base class for all model-specific detail tables

**Implementation**:
- Inherit from `DetailTableVirtualTemplate`
- Add relationship to `MakeModel` via foreign key (not to detail table set)
- Implement model-specific validation logic
- Provide common model detail operations
- Support dynamic creation during asset creation process
- Prevent duplicate model detail rows

#### 2.3.2 Emissions Information Detail Table
**File**: `app/models/assets/model_details/emissions_info.py`

**Purpose**: Store emissions specifications for vehicle models

**Fields**:
- `emissions_standard`: Emissions standard (EPA, CARB, etc.)
- `emissions_rating`: Emissions rating/classification
- `fuel_type`: Fuel type (gasoline, diesel, electric, hybrid)
- `mpg_city`: City fuel economy
- `mpg_highway`: Highway fuel economy
- `mpg_combined`: Combined fuel economy
- `co2_emissions`: CO2 emissions rating
- `emissions_test_date`: Date of emissions testing
- `emissions_certification`: Certification number

**Implementation**:
- Inherit from `ModelDetailVirtual`
- Add emissions-specific validation
- Implement fuel economy calculations
- Support multiple emissions standards

#### 2.3.3 Model Information Detail Table
**File**: `app/models/assets/model_details/model_info.py`

**Purpose**: Store general model specifications and information

**Fields**:
- `model_year`: Model year
- `body_style`: Body style (sedan, SUV, truck, etc.)
- `engine_type`: Engine type and specifications
- `transmission_type`: Transmission type
- `drivetrain`: Drivetrain configuration
- `seating_capacity`: Number of seats
- `cargo_capacity`: Cargo capacity
- `towing_capacity`: Towing capacity
- `manufacturer_website`: Manufacturer website
- `technical_specifications`: Technical specifications

**Implementation**:
- Inherit from `ModelDetailVirtual`
- Add model-specific validation
- Support multiple body styles
- Include comprehensive specifications

### 2.1: Create Detail Sets

#### 2.1.1 Create Asset Type Detail Set
**File**: `app/models/assets/detail_table_sets/asset_type_detail_table_set.py`

**Purpose**: Configuration container that defines which detail table types are available for a specific asset type

**Implementation**:
- Create `AssetTypeDetailTableSet` model
- Link to `AssetType` via foreign key
- Include configuration fields for detail table type assignments
- Store list of detail table types (purchase_info, vehicle_registration, etc.) that apply to this asset type
- Mark each detail table type as asset_detail or model_detail


#### 2.1.2 Create Model Specific Detail Set
**File**: `app/models/assets/detail_table_sets/model_detail_table_set.py`

**Purpose**: Configuration container that defines additional detail table types for a specific model beyond what the asset type provides

**Implementation**:
- Create `ModelDetailTableSet` model
- Link to `MakeModel` via foreign key
- Include configuration fields for additional detail table type assignments
- Store list of additional detail table types that apply to this model
- Mark each detail table type as asset_detail or model_detail

### Step 2.4: Detail Table Relationships

#### 2.4.1 Dynamic Detail Table Assignment System
**Implementation**:
- **No direct relationships**: Assets and models do NOT have relationships to detail table sets
- **Asset Type Detail Table Sets**: Define which detail tables are available for each asset type
- **Model Detail Table Sets**: Define additional detail tables available for specific models
- **Dynamic row creation**: On asset creation, system automatically creates detail table rows

#### 2.4.2 Asset Creation Detail Table Process
**Implementation**:
When a new asset is created, the system automatically processes detail table assignments through the following steps:

1. **Asset Type Lookup**: Retrieve the AssetTypeDetailTableSet configuration for the asset's type
2. **Model Lookup**: Retrieve the ModelDetailTableSet configuration for the asset's model  
3. **Asset Type Processing**: For each detail table type in the asset type configuration:
   - If asset_detail: Create a new detail table row linked to this specific asset
   - If model_detail: Check if a detail table row exists for this model, create if missing
4. **Model Processing**: For each additional detail table type in the model configuration:
   - If asset_detail: Create a new detail table row linked to this specific asset
   - If model_detail: Check if a detail table row exists for this model, create if missing
5. **Row Creation**: Generate appropriate detail table rows with proper foreign key relationships
6. **Duplicate Prevention**: Ensure model detail rows are only created once per model

#### 2.4.3 Detail Table Row Creation Logic
**Implementation**:
- **Asset Detail Tables**: Create rows with foreign key to the specific asset
- **Model Detail Tables**: Create rows with foreign key to the model (if not already exists)
- **Duplicate Prevention**: Check for existing model detail rows before creating new ones
- **Cascade Management**: When asset is deleted, remove associated asset detail rows
- **Model Detail Persistence**: Model detail rows persist even when assets are deleted

#### 2.4.4 Detail Table Set Configuration
**Implementation**:
- **Asset Type Detail Table Set**: Contains list of detail table types available for asset type
- **Model Detail Table Set**: Contains list of additional detail table types for specific model
- **Detail Table Type Classification**: Each detail table type marked as asset_detail or model_detail
- **Configuration Management**: Admin interface to configure which detail tables apply to which types/models

### Step 2.5: Build System Integration

#### 2.5.1 Update Asset Models Builder
**File**: `app/models/assets/build.py`

**Implementation**:
- Add detail table set creation to build process
- Implement detail table model registration
- Add validation for detail table relationships
- Include detail table statistics in build output

#### 2.5.2 Update Main Build System
**File**: `app/models/build.py`

**Implementation**:
- Add asset detail tables to model build coordination
- Include detail table set creation in build flow
- Add detail table validation to build process
- Update build statistics to include detail tables

### Step 2.6: Data Testing and Validation

#### 2.6.1 Insert Sample Data
**Implementation**:
- Create sample asset detail table sets
- Insert test data for each detail table type
- Verify relationships work correctly
- Test data integrity constraints

**Sample Data to Insert**:
- Asset: "VTC-001" with purchase info and vehicle registration
- Model: "Toyota Corolla" with emissions info and model info
- Asset: "VTC-002" with Toyota warranty receipt
- Multiple detail table sets for testing relationships

#### 2.6.2 Verify Relationships
**Testing**:
- Test asset-to-detail-table-set relationships
- Test model-to-detail-table-set relationships
- Verify cascade delete behavior
- Test foreign key constraints

#### 2.6.3 Test Querying Detail Information
**Testing**:
- Query assets with their detail information
- Query models with their detail information
- Test filtering by detail table criteria
- Verify join operations work correctly

## Success Criteria

### Functional Requirements
- [ ] All detail table models can be created successfully
- [ ] Detail table sets properly link to assets and models
- [ ] Sample data can be inserted for all detail table types
- [ ] Relationships work correctly for all detail table combinations
- [ ] Query operations return expected results
- [ ] Cascade delete operations work properly

### Technical Requirements
- [ ] All models inherit from appropriate base classes
- [ ] Foreign key relationships are properly defined
- [ ] Audit trail functionality works for all detail tables
- [ ] Build system successfully creates all detail table structures
- [ ] No database constraint violations occur
- [ ] All detail table operations maintain data integrity

### Performance Requirements
- [ ] Detail table queries perform efficiently
- [ ] Join operations don't cause performance issues
- [ ] Database indexes are properly created
- [ ] Memory usage remains reasonable for detail table operations

## Risk Mitigation

### Technical Risks
- **Complex Relationships**: Implement thorough testing of all relationship combinations
- **Data Integrity**: Use database constraints and validation to prevent data corruption
- **Performance Issues**: Monitor query performance and optimize as needed
- **Schema Complexity**: Maintain clear documentation of detail table structure

### Implementation Risks
- **Scope Creep**: Focus on core detail table functionality before adding advanced features
- **Testing Coverage**: Ensure comprehensive testing of all detail table operations
- **Data Migration**: Plan for future detail table additions without breaking existing data

## Dependencies

### Phase 1 Dependencies
- Core models must be fully implemented and tested
- User authentication system must be working
- Database migration system must be functional
- Build system must be operational

### External Dependencies
- SQLAlchemy ORM functionality
- Flask application framework
- Database (SQLite for development)
- Python datetime handling


## Conclusion

Phase 2 establishes a robust, flexible detail table system that will support the asset management system's requirements for storing detailed asset and model information. The virtual template approach ensures the system can be extended with new detail table types without requiring schema changes, while maintaining data integrity and proper relationships.

The implementation follows the established patterns from Phase 1 and provides a solid foundation for the more complex systems in subsequent phases.
