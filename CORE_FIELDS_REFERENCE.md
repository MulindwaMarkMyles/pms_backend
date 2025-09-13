# Core Property Management - Field Reference Guide

Base URL: `/api/core/`  
All endpoints require `Authorization: Bearer <token>` header.

## 1. Estate Fields

### Required Fields
- `name` (string) - Estate name
- `address` (string) - Full address

### Optional Fields
- `size` (string) - Estate size (e.g., "5 acres", "2 hectares")
- `description` (text) - Detailed description

### Create Estate Request
```json
{
  "name": "Sunset Gardens Estate",           // Required: string, max 255 chars
  "address": "123 Main St, Kampala, Uganda", // Required: string, max 500 chars
  "size": "5 acres",                         // Optional: string, max 100 chars
  "description": "Luxury residential estate" // Optional: text, unlimited
}
```

### Response Fields
```json
{
  "id": 1,                                   // Auto-generated primary key
  "name": "Sunset Gardens Estate",
  "address": "123 Main St, Kampala, Uganda",
  "size": "5 acres",
  "description": "Luxury residential estate",
  "created_at": "2024-01-15T10:00:00Z"      // Auto-generated timestamp
}
```

---

## 2. Block Fields

### Required Fields
- `estate` (integer) - Estate ID (foreign key)
- `name` (string) - Block name

### Optional Fields
- `description` (text) - Block description

### Create Block Request
```json
{
  "estate": 1,                               // Required: integer, must exist
  "name": "Block A",                         // Required: string, max 100 chars
  "description": "First residential block"   // Optional: text, unlimited
}
```

### Response Fields
```json
{
  "id": 1,                                   // Auto-generated primary key
  "estate": 1,                               // Foreign key to Estate
  "estate_details": {                        // Nested estate info (read-only)
    "id": 1,
    "name": "Sunset Gardens Estate"
  },
  "name": "Block A",
  "description": "First residential block",
  "created_at": "2024-01-15T11:00:00Z"      // Auto-generated timestamp
}
```

---

## 3. Apartment Fields

### Required Fields
- `block` (integer) - Block ID (foreign key)
- `number` (string) - Apartment number
- `rent_amount` (decimal) - Monthly rent amount

### Optional Fields
- `size` (decimal) - Apartment size in square meters
- `amenities` (array) - List of amenity IDs
- `furnishings` (array) - List of furnishing IDs
- `number_of_rooms` (integer) - Number of rooms
- `color` (string) - Apartment color/theme
- `description` (text) - Apartment description

### Create Apartment Request
```json
{
  "block": 1,                                // Required: integer, must exist
  "number": "A101",                          // Required: string, max 20 chars, unique per block
  "size": 120.50,                           // Optional: decimal, max 8 digits, 2 decimal places
  "amenities": [1, 2, 3],                   // Optional: array of integers (amenity IDs)
  "furnishings": [1, 2],                    // Optional: array of integers (furnishing IDs)
  "rent_amount": 500000.00,                 // Required: decimal, max 12 digits, 2 decimal places
  "number_of_rooms": 3,                     // Optional: positive integer
  "color": "White",                         // Optional: string, max 50 chars
  "description": "3-bedroom apartment"       // Optional: text, unlimited
}
```

### Response Fields
```json
{
  "id": 1,                                   // Auto-generated primary key
  "block": 1,                                // Foreign key to Block
  "block_details": {                         // Nested block info (read-only)
    "id": 1,
    "name": "Block A",
    "estate": {
      "id": 1,
      "name": "Sunset Gardens Estate"
    }
  },
  "number": "A101",
  "size": "120.50",
  "amenities": [                             // Many-to-many relationship
    {"id": 1, "name": "Water"},
    {"id": 2, "name": "Electricity"},
    {"id": 3, "name": "Internet"}
  ],
  "furnishings": [                           // Many-to-many relationship
    {"id": 1, "name": "Air Conditioning"},
    {"id": 2, "name": "Kitchen Appliances"}
  ],
  "rent_amount": "500000.00",
  "number_of_rooms": 3,
  "color": "White",
  "description": "3-bedroom apartment",
  "is_occupied": false,                      // Computed field (read-only)
  "created_at": "2024-01-15T12:00:00Z"      // Auto-generated timestamp
}
```

---

## 4. Amenity Fields

### Required Fields
- `name` (string) - Amenity name

### Create Amenity Request
```json
{
  "name": "Swimming Pool"                    // Required: string, max 100 chars, unique
}
```

### Response Fields
```json
{
  "id": 1,                                   // Auto-generated primary key
  "name": "Swimming Pool"
}
```

### Pre-populated Amenities
```json
[
  {"name": "Water"},
  {"name": "Electricity"}, 
  {"name": "Internet"},
  {"name": "Parking"},
  {"name": "Security"},
  {"name": "Swimming Pool"},
  {"name": "Gym"},
  {"name": "Garden"},
  {"name": "Elevator"}
]
```

---

## 5. Furnishing Fields

### Required Fields
- `name` (string) - Furnishing name

### Create Furnishing Request
```json
{
  "name": "Washing Machine"                  // Required: string, max 100 chars, unique
}
```

### Response Fields
```json
{
  "id": 1,                                   // Auto-generated primary key
  "name": "Washing Machine"
}
```

### Pre-populated Furnishings
```json
[
  {"name": "Air Conditioning"},
  {"name": "Kitchen Appliances"},
  {"name": "Bedroom Furniture"},
  {"name": "Living Room Furniture"},
  {"name": "Washing Machine"},
  {"name": "Refrigerator"},
  {"name": "Microwave"},
  {"name": "TV"},
  {"name": "Dining Set"}
]
```

---

## Validation Rules

### Estate Validation
- `name`: Required, unique, max 255 characters
- `address`: Required, max 500 characters
- `size`: Optional, max 100 characters
- `description`: Optional, unlimited text

### Block Validation
- `estate`: Required, must reference existing Estate
- `name`: Required, max 100 characters
- `description`: Optional, unlimited text
- **Unique constraint**: (`estate`, `name`) - Block name must be unique within estate

### Apartment Validation
- `block`: Required, must reference existing Block
- `number`: Required, max 20 characters
- `size`: Optional, positive decimal (max 999999.99)
- `amenities`: Optional, array of existing Amenity IDs
- `furnishings`: Optional, array of existing Furnishing IDs
- `rent_amount`: Required, positive decimal (max 9999999999.99)
- `number_of_rooms`: Optional, positive integer (1-50)
- `color`: Optional, max 50 characters
- `description`: Optional, unlimited text
- **Unique constraint**: (`block`, `number`) - Apartment number must be unique within block

### Amenity/Furnishing Validation
- `name`: Required, unique, max 100 characters

---

## Common Error Responses

### 400 Bad Request - Missing Required Fields
```json
{
  "error": "Validation failed",
  "details": {
    "name": ["This field is required."],
    "rent_amount": ["This field is required."]
  }
}
```

### 400 Bad Request - Invalid Foreign Key
```json
{
  "error": "Validation failed",
  "details": {
    "block": ["Invalid pk \"999\" - object does not exist."]
  }
}
```

### 400 Bad Request - Unique Constraint Violation
```json
{
  "error": "Validation failed",
  "details": {
    "number": ["Apartment with this Number already exists."]
  }
}
```

### 400 Bad Request - Invalid Data Type
```json
{
  "error": "Validation failed",
  "details": {
    "rent_amount": ["A valid number is required."],
    "number_of_rooms": ["A valid integer is required."]
  }
}
```

---

## Example Complete Flow

### 1. Create Estate
```bash
curl -X POST http://127.0.0.1:8000/api/core/estates/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Green Valley Estate",
    "address": "456 Oak Street, Kampala",
    "size": "3 acres",
    "description": "Modern family estate"
  }'
```

### 2. Create Block
```bash
curl -X POST http://127.0.0.1:8000/api/core/blocks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "estate": 1,
    "name": "Block B",
    "description": "Second residential block"
  }'
```

### 3. Create Amenities (if needed)
```bash
curl -X POST http://127.0.0.1:8000/api/core/amenities/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Balcony"}'
```

### 4. Create Apartment
```bash
curl -X POST http://127.0.0.1:8000/api/core/apartments/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "block": 1,
    "number": "B201",
    "size": 95.0,
    "amenities": [1, 2, 3],
    "furnishings": [1, 2],
    "rent_amount": 450000,
    "number_of_rooms": 2,
    "color": "Blue",
    "description": "2-bedroom apartment with balcony"
  }'
```

---

**Notes:**
- All decimal fields accept both string and numeric input
- Arrays can be empty `[]` or contain valid IDs only
- Timestamps are automatically generated and cannot be set manually
- Use PATCH for partial updates, PUT for complete replacement