# Complaints API Documentation

Base URL: `/api/complaints/`  
All endpoints require `Authorization: Bearer <token>` header.

## 1. Complaint Statuses (`ComplaintStatus`)

### List Statuses
GET `/complaint-statuses/`

Response:
```json
[
  {"id":1, "name":"Open"},
  {"id":2, "name":"In Progress"},
  {"id":3, "name":"Resolved"},
  {"id":4, "name":"Closed"}
]
```

### Create Status
POST `/complaint-statuses/`

Request:
```json
{ "name": "Pending Review" }
```

Response (201):
```json
{ "id":5, "name":"Pending Review" }
```

---

## 2. Complaint Categories (`ComplaintCategory`)

### List Categories
GET `/complaint-categories/`

Response:
```json
[
  {"id":1, "name":"Amenities", "description":"Water, electricity issues"},
  {"id":2, "name":"Maintenance", "description":"Repair requests"},
  {"id":3, "name":"Security"}
]
```

### Create Category
POST `/complaint-categories/`

Request:
```json
{ "name": "Noise", "description": "Noise complaints" }
```

Response (201):
```json
{ "id":4, "name":"Noise", "description":"Noise complaints" }
```

---

## 3. Complaints (`Complaint`)

### List All Complaints
GET `/complaints/`

Optional query params:
- `status_id` (e.g. `?status_id=2`)
- `tenant_id` (e.g. `?tenant_id=1`)

Response:
```json
[
  {
    "id":1,
    "tenant":2,
    "category":1,
    "title":"Leaking faucet",
    "description":"Sink leaking for 2 days",
    "status":1,
    "feedback":null,
    "attachment":"/media/complaint_attachments/1.jpg",
    "created_at":"2024-01-15T10:00:00Z"
  }
]
```

### Get Single Complaint
GET `/complaints/{id}/`

Response: single object same structure as above.

### Create Complaint
POST `/complaints/`

Request (JSON or form-data):
```json
{
  "tenant":2,
  "category":1,
  "title":"Leaking faucet",
  "description":"Sink leaking in kitchen",
  "attachment":"file_object"
}
```

Response (201):
```json
{
  "id":5,
  "tenant":2,
  "category":1,
  "title":"Leaking faucet",
  "description":"Sink leaking in kitchen",
  "status":1,
  "feedback":"",
  "attachment":"/media/complaint_attachments/5.jpg",
  "created_at":"2024-02-01T14:30:00Z"
}
```

### Update Complaint Status
PATCH `/complaints/{id}/update_status/`

Request:
```json
{
  "status_id":2,
  "feedback":"Maintenance scheduled for tomorrow"
}
```

Response:
```json
{ "message":"Status updated successfully" }
```

### Close Complaint
PATCH `/complaints/{id}/close/`

Request: `{}`

Response:
```json
{ "message":"Complaint closed successfully" }
```

---

## 4. Tenant-Specific Endpoints

### My Complaints
GET `/complaints/my_complaints/`

Response: list of complaints for logged-in tenant (same structure as **List All Complaints**).

### Log Complaint
POST `/complaints/log_complaint/`  
(tenant auto-assigned)

Request:
```json
{
  "category":1,
  "title":"No hot water",
  "description":"No hot water in shower since morning",
  "attachment":null
}
```

Response (201):
```json
{ "message":"Complaint logged successfully","complaint":{...} }
```

---

## Error Responses

- **400 Bad Request**: missing or invalid fields
  ```json
  {"error":"status_id required"}
  ```
- **404 Not Found**: invalid complaint, status, or category ID
  ```json
  {"error":"Complaint not found"}
  ```
- **401 Unauthorized**: no or invalid token
  ```json
  {"detail":"Authentication credentials were not provided."}
  ```

---

**Notes:**
- `/update_status/` and `/close/` are detail routes (use complaint ID).  
- Tenant endpoints are under the same router with custom actions.  
- Attachments return URL for download.  
