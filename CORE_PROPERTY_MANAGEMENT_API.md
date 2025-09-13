# Core Property Management API Documentation

Base URL: `/api/core/`  
All endpoints require `Authorization: Bearer <token>` header.

## 1. Estates Management

### List All Estates
GET `/estates/`

Response:
```json
[
  {
    "id":1,
    "name":"Sunset Gardens Estate",
    "address":"123 Main Street, Kampala, Uganda",
    "size":"5 acres",
    "description":"Luxury residential estate with modern amenities",
    "created_at":"2024-01-15T10:00:00Z"
  }
]
```

### Get Single Estate
GET `/estates/{id}/`

Response: Single estate object (same structure as above)

### Create Estate
POST `/estates/`

Request:
```json
{
  "name":"Sunset Gardens Estate",
  "address":"123 Main Street, Kampala, Uganda",
  "size":"5 acres",
  "description":"Luxury residential estate with modern amenities"
}
```

Response (201):
```json
{
  "id":1,
  "name":"Sunset Gardens Estate",
  "address":"123 Main Street, Kampala, Uganda",
  "size":"5 acres",
  "description":"Luxury residential estate with modern amenities",
  "created_at":"2024-01-15T10:00:00Z"
}
```

### Update Estate
PUT `/estates/{id}/` or PATCH `/estates/{id}/`

Request (PATCH - partial update):
```json
{
  "description":"Updated description with new amenities"
}
```

Response (200):
```json
{
  "id":1,
  "name":"Sunset Gardens Estate",
  "address":"123 Main Street, Kampala, Uganda",
  "size":"5 acres",
  "description":"Updated description with new amenities",
  "created_at":"2024-01-15T10:00:00Z"
}
```

### Delete Estate
DELETE `/estates/{id}/`

Response (204): No content

---

## 2. Blocks Management

### List All Blocks
GET `/blocks/`

Optional query params:
- `?estate_id=1` (filter by estate)

Response:
```json
[
  {
    "id":1,
    "estate":1,
    "estate_details":{
      "id":1,
      "name":"Sunset Gardens Estate"
    },
    "name":"Block A",
    "description":"First residential block with 20 units",
    "created_at":"2024-01-15T11:00:00Z"
  }
]
```

### Get Single Block
GET `/blocks/{id}/`

Response: Single block object (same structure as above)

### Create Block
POST `/blocks/`

Request:
```json
{
  "estate":1,
  "name":"Block A",
  "description":"First residential block with 20 units"
}
```

Response (201):
```json
{
  "id":1,
  "estate":1,
  "estate_details":{
    "id":1,
    "name":"Sunset Gardens Estate"
  },
  "name":"Block A",
  "description":"First residential block with 20 units",
  "created_at":"2024-01-15T11:00:00Z"
}
```

### Update Block
PUT `/blocks/{id}/` or PATCH `/blocks/{id}/`

Request (PATCH):
```json
{
  "description":"Updated block description"
}
```

Response (200): Updated block object

### Delete Block
DELETE `/blocks/{id}/`

Response (204): No content

---

## 3. Apartments Management

### List All Apartments
GET `/apartments/`

Optional query params:
- `?block_id=1` (filter by block)
- `?estate_id=1` (filter by estate)
- `?available=true` (only available apartments)

Response:
```json
[
  {
    "id":1,
    "block":1,
    "block_details":{
      "id":1,
      "name":"Block A",
      "estate":{
        "id":1,
        "name":"Sunset Gardens Estate"
      }
    },
    "number":"A101",
    "size":"120.50",
    "amenities":[
      {"id":1,"name":"Water"},
      {"id":2,"name":"Electricity"}
    ],
    "furnishings":[
      {"id":1,"name":"Air Conditioning"}
    ],
    "rent_amount":"500000.00",
    "number_of_rooms":3,
    "color":"White",
    "description":"3-bedroom apartment with modern furnishings",
    "is_occupied":false,
    "created_at":"2024-01-15T12:00:00Z"
  }
]
```

### Get Available Apartments
GET `/apartments/available/`

Response: Same as list, but only unoccupied apartments

### Get Single Apartment
GET `/apartments/{id}/`

Response: Single apartment object (same structure as above)

### Create Apartment
POST `/apartments/`

Request:
```json
{
  "block":1,
  "number":"A101",
  "size":120.50,
  "amenities":[1,2,3],
  "furnishings":[1,2],
  "rent_amount":500000,
  "number_of_rooms":3,
  "color":"White",
  "description":"3-bedroom apartment with modern furnishings"
}
```

Response (201):
```json
{
  "id":1,
  "block":1,
  "block_details":{
    "id":1,
    "name":"Block A",
    "estate":{
      "id":1,
      "name":"Sunset Gardens Estate"
    }
  },
  "number":"A101",
  "size":"120.50",
  "amenities":[
    {"id":1,"name":"Water"},
    {"id":2,"name":"Electricity"},
    {"id":3,"name":"Internet"}
  ],
  "furnishings":[
    {"id":1,"name":"Air Conditioning"},
    {"id":2,"name":"Kitchen Appliances"}
  ],
  "rent_amount":"500000.00",
  "number_of_rooms":3,
  "color":"White",
  "description":"3-bedroom apartment with modern furnishings",
  "is_occupied":false,
  "created_at":"2024-01-15T12:00:00Z"
}
```

### Update Apartment
PUT `/apartments/{id}/` or PATCH `/apartments/{id}/`

Request (PATCH):
```json
{
  "rent_amount":550000,
  "description":"Updated apartment with premium features"
}
```

Response (200): Updated apartment object

### Delete Apartment
DELETE `/apartments/{id}/`

Response (204): No content

---

## 4. Amenities Management

### List All Amenities
GET `/amenities/`

Response:
```json
[
  {"id":1,"name":"Water"},
  {"id":2,"name":"Electricity"},
  {"id":3,"name":"Internet"},
  {"id":4,"name":"Parking"},
  {"id":5,"name":"Security"}
]
```

### Create Amenity
POST `/amenities/`

Request:
```json
{
  "name":"Swimming Pool"
}
```

Response (201):
```json
{
  "id":6,
  "name":"Swimming Pool"
}
```

### Update Amenity
PUT `/amenities/{id}/` or PATCH `/amenities/{id}/`

### Delete Amenity
DELETE `/amenities/{id}/`

---

## 5. Furnishings Management

### List All Furnishings
GET `/furnishings/`

Response:
```json
[
  {"id":1,"name":"Air Conditioning"},
  {"id":2,"name":"Kitchen Appliances"},
  {"id":3,"name":"Bedroom Furniture"},
  {"id":4,"name":"Living Room Furniture"}
]
```

### Create Furnishing
POST `/furnishings/`

Request:
```json
{
  "name":"Washing Machine"
}
```

Response (201):
```json
{
  "id":5,
  "name":"Washing Machine"
}
```

### Update Furnishing
PUT `/furnishings/{id}/` or PATCH `/furnishings/{id}/`

### Delete Furnishing
DELETE `/furnishings/{id}/`

---

## Error Responses

### 400 Bad Request
```json
{
  "error":"name is required"
}
```

### 404 Not Found
```json
{
  "detail":"Not found."
}
```

### 401 Unauthorized
```json
{
  "detail":"Authentication credentials were not provided."
}
```

---

**Notes:**
- All endpoints support standard REST operations (GET, POST, PUT, PATCH, DELETE)
- Use query parameters to filter results
- Amenities and furnishings are many-to-many relationships with apartments
- Estate → Block → Apartment hierarchy must be maintained
- Deleting estates/blocks will cascade to related objects