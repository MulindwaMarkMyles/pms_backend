# Tenants API Documentation

Base URL: `/api/tenants/`
All endpoints require JWT `Authorization: Bearer <token>` header.

## 1. Tenant Types (TenantType)

### List Tenant Types
GET `/tenant-types/`

Response:
```json
[
  {"id":1, "name":"Short Stay (≤6 months)", "description":"..."},
  {"id":2, "name":"Long Term (≥1 year)", "description":"..."}
]
```

### Create Tenant Type
POST `/tenant-types/`

Request:
```json
{ "name": "Corporate", "description": "Company tenants" }
```

Response (201):
```json
{ "id":3, "name":"Corporate", "description":"Company tenants" }
```

---

## 2. Tenants (Tenant)

### List All Tenants
GET `/tenants/`

Optional query params:
- `apartment_id` (e.g. `?apartment_id=1`)
- `tenant_type_id` (e.g. `?tenant_type_id=2`)

Response:
```json
[
  {
    "id":1,
    "user_details":{
      "id":5,"username":"jane_doe","email":"jane@example.com",
      "first_name":"Jane","last_name":"Doe"
    },
    "tenant_type":2,
    "apartment":4,
    "lease_start":"2024-01-01",
    "lease_end":"2024-06-30",
    "phone_number":"+256700123456",
    "emergency_contact":"+256700123457",
    "created_at":"2024-01-10T12:00:00Z"
  }
]
```

### Get Single Tenant
GET `/tenants/{id}/`

Response:
```json
{
  "id":1,
  "user_details":{...},
  "tenant_type":2,
  "apartment":4,
  "lease_start":"2024-01-01",
  "lease_end":"2024-06-30",
  "phone_number":"+256700123456",
  "emergency_contact":"+256700123457",
  "created_at":"2024-01-10T12:00:00Z"
}
```

### Get Tenants by Estate
GET `/tenants/by_estate/?estate_id=1`

Response: same as **List All Tenants**, filtered by estate

### Create Tenant
POST `/tenants/`

Request:
```json
{
  "user":{
    "username":"john_doe",
    "email":"john@example.com",
    "first_name":"John",
    "last_name":"Doe",
    "password":"securepass"
  },
  "tenant_type":1,
  "apartment":3,
  "lease_start":"2024-02-01",
  "lease_end":"2024-08-01",
  "phone_number":"+256700123458",
  "emergency_contact":"+256700123459"
}
```

Response (201):
```json
{
  "message":"Tenant created successfully",
  "tenant":{
    "id":2,
    "user":{ "id":7, "username":"john_doe" },
    "tenant_type":1,
    "apartment":3,
    "lease_start":"2024-02-01",
    "lease_end":"2024-08-01",
    "phone_number":"+256700123458",
    "emergency_contact":"+256700123459"
  }
}
```

### Error Responses
- **400 Bad Request**: missing fields or invalid data
  ```json
  {"error":"User username is required"}
  ```
- **404 Not Found**: invalid `apartment` or `tenant_type` ID
  ```json
  {"error":"Apartment not found"}
  ```
- **400 Conflict**: duplicate username/email
  ```json
  {"error":"Username already exists"}
  ```

---

## Notes
- `user_details` nested object returns user info for read operations.
- Use filter params to narrow results by apartment or tenant type.
- Authentication is required for all tenant endpoints.
