# Database Schema Summary

## assets

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| home_majorlocation_UID | VARCHAR(100) |  |
| parent_asset_UID | VARCHAR(100) |  |
| current_majorlocation_UID | VARCHAR(100) | NOT NULL |
| current_minorlocation_UID | VARCHAR(100) |  |
| hours_operated | FLOAT |  |
| meter_1 | FLOAT |  |
| meter_1_type | VARCHAR(100) |  |
| meter_2 | FLOAT |  |
| meter_2_type | VARCHAR(100) |  |
| UID | VARCHAR(50) | NOT NULL |
| asset_type | VARCHAR(50) |  |
| common_name | VARCHAR(100) |  |
| description | TEXT | NOT NULL |
| status | VARCHAR(50) |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |
| status | types_statuses.value |
| asset_type | types_assets.value |
| meter_2_type | generic_types.value |
| meter_1_type | generic_types.value |
| current_minorlocation_UID | minor_locations.UID |
| current_majorlocation_UID | major_locations.UID |
| parent_asset_UID | assets.UID |
| home_majorlocation_UID | major_locations.UID |

---

## attachments

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| event_id | INT | NOT NULL |
| file_path | VARCHAR(100) | NOT NULL |
| file_name | VARCHAR(100) | NOT NULL |
| file_type | VARCHAR(100) | NOT NULL |
| file_size | INT |  |
| file_hash | VARCHAR(100) | NOT NULL |
| tags | VARCHAR(100) |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |
| event_id | events.row_id |

---

## dropdowns

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| UID | VARCHAR(100) |  |
| group | VARCHAR(100) | NOT NULL |
| value | VARCHAR(64) | NOT NULL |
| description | TEXT |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |

---

## events

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| title | VARCHAR(255) | NOT NULL |
| description | TEXT |  |
| event_type | VARCHAR(64) | NOT NULL |
| status | VARCHAR(50) | NOT NULL |
| location_UID | VARCHAR(50) |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |
| asset_UID | VARCHAR(100) |  |
| asset_type | VARCHAR(100) | NOT NULL |

### Foreign Keys
| Column | References |
|--------|------------|
| asset_type | assets.asset_type |
| asset_UID | assets.UID |
| updated_by | users.row_id |
| created_by | users.row_id |
| location_UID | major_locations.UID |

---

## generic_types

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| UID | VARCHAR(100) |  |
| group | VARCHAR(100) | NOT NULL |
| value | VARCHAR(64) | NOT NULL |
| description | TEXT |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |

---

## log_entry

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| id | INT | PK, NOT NULL |
| level | VARCHAR(10) | NOT NULL |
| message | TEXT | NOT NULL |
| timestamp | DATETIME | NOT NULL |
| module | VARCHAR(100) |  |
| function | VARCHAR(100) |  |
| line | INT |  |
| log_data | TEXT |  |

---

## major_locations

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| Country | VARCHAR(100) |  |
| State | VARCHAR(100) |  |
| City | VARCHAR(100) |  |
| Address | VARCHAR(100) |  |
| ZipCode | INT |  |
| Misc | VARCHAR(100) |  |
| UID | VARCHAR(50) | NOT NULL |
| asset_type | VARCHAR(50) |  |
| common_name | VARCHAR(100) |  |
| description | TEXT | NOT NULL |
| status | VARCHAR(50) |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |
| status | types_statuses.value |
| asset_type | types_assets.value |

---

## minor_locations

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| major_location_uid | VARCHAR(50) | NOT NULL |
| Building | VARCHAR(100) |  |
| Room | VARCHAR(100) |  |
| xyz_orgin_type | VARCHAR(100) |  |
| x | FLOAT |  |
| y | FLOAT |  |
| z | FLOAT |  |
| ml_bin | VARCHAR(100) |  |
| ml_bin_type | VARCHAR(100) |  |
| UID | VARCHAR(50) | NOT NULL |
| asset_type | VARCHAR(50) |  |
| common_name | VARCHAR(100) |  |
| description | TEXT | NOT NULL |
| status | VARCHAR(50) |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |
| status | types_statuses.value |
| asset_type | types_assets.value |
| major_location_uid | major_locations.UID |

---

## misc_locations

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| location_type | VARCHAR(100) | NOT NULL |
| contact_person | VARCHAR(100) |  |
| contact_phone | VARCHAR(100) |  |
| contact_email | VARCHAR(100) |  |
| business_hours | VARCHAR(200) |  |
| notes | TEXT |  |
| Country | VARCHAR(100) |  |
| State | VARCHAR(100) |  |
| City | VARCHAR(100) |  |
| Address | VARCHAR(100) |  |
| ZipCode | INT |  |
| Misc | VARCHAR(100) |  |
| UID | VARCHAR(50) | NOT NULL |
| asset_type | VARCHAR(50) |  |
| common_name | VARCHAR(100) |  |
| description | TEXT | NOT NULL |
| status | VARCHAR(50) |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |
| status | types_statuses.value |
| asset_type | types_assets.value |

---

## types_assets

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| value | VARCHAR(64) | NOT NULL |
| description | TEXT |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |

---

## types_events

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| value | VARCHAR(64) | NOT NULL |
| description | TEXT |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |

---

## types_statuses

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| value | VARCHAR(64) | NOT NULL |
| description | TEXT |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |

---

## users

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| row_id | INT | PK, NOT NULL |
| username | VARCHAR(64) | NOT NULL |
| email | VARCHAR(128) | NOT NULL |
| is_admin | BOOL |  |
| display_name | VARCHAR(64) |  |
| role | VARCHAR(64) |  |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |

---

## vehicle_models

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| manufacturer | VARCHAR(100) | NOT NULL |
| model | VARCHAR(100) | NOT NULL |
| model_subtype | VARCHAR(100) | NOT NULL |
| year | INT | NOT NULL |
| vehicle_class | VARCHAR(100) |  |
| NHTSA_classification | VARCHAR(100) |  |
| CARB_classification | VARCHAR(100) |  |
| fuel_type | VARCHAR(100) |  |
| fuel_tank_capacity | FLOAT |  |
| miles_per_fuel_type | FLOAT |  |
| weight | FLOAT |  |
| length | FLOAT |  |
| width | FLOAT |  |
| height | FLOAT |  |
| max_passengers | INT |  |
| max_cargo_capacity | FLOAT |  |
| expected_life_years | INT |  |
| expected_life_miles | INT |  |
| UID | VARCHAR(50) | NOT NULL |
| revision | VARCHAR(100) |  |
| description | TEXT |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |

---

## vehicle_purchase_info

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| row_id | INT | PK, NOT NULL |
| vehicle_id | INT | NOT NULL |
| purchase_date | DATE |  |
| purchase_price | FLOAT |  |
| purchase_location_UID | VARCHAR(100) |  |
| attachments | VARCHAR(100) |  |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |
| purchase_location_UID | misc_locations.UID |
| vehicle_id | vehicles.row_id |

---

## vehicles

### Columns
| Column | Type | Constraints |
|--------|------|-------------|
| asset_UID | VARCHAR(100) | NOT NULL |
| model_UID | VARCHAR(100) | NOT NULL |
| VIN | VARCHAR(100) |  |
| color | VARCHAR(100) |  |
| license_plate | VARCHAR(100) |  |
| license_plate_state | VARCHAR(100) |  |
| license_plate_expiration_date | DATE |  |
| license_plate_renewal_date | DATE |  |
| previous_license_plates | VARCHAR(100) |  |
| purchase_date | DATE |  |
| purchase_price | FLOAT |  |
| row_id | INT | PK, NOT NULL |
| created_at | DATETIME | NOT NULL |
| created_by | INT |  |
| updated_at | DATETIME | NOT NULL |
| updated_by | INT |  |

### Foreign Keys
| Column | References |
|--------|------------|
| updated_by | users.row_id |
| created_by | users.row_id |
| model_UID | vehicle_models.UID |
| asset_UID | assets.UID |

---
