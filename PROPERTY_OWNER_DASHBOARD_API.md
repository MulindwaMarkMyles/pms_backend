# Property Owner Dashboard API Documentation

Base URL: `/api/`  
All endpoints require `Authorization: Bearer <token>` header.

## 1. Occupancy Status

### Get Occupancy Dashboard
GET `/core/apartments/dashboard_occupancy/`

Response:
```json
{
  "total_estates":3,
  "total_apartments":150,
  "occupied_apartments":120,
  "vacant_apartments":30,
  "occupancy_rate":80.0,
  "estates":[
    {
      "estate_id":1,
      "estate_name":"Sunset Gardens",
      "total_apartments":50,
      "occupied_apartments":45,
      "vacant_apartments":5,
      "occupancy_rate":90.0,
      "blocks":[
        {
          "block_id":1,
          "block_name":"Block A",
          "total_apartments":25,
          "occupied_apartments":22,
          "vacant_apartments":3,
          "occupancy_rate":88.0
        }
      ]
    }
  ]
}
```

### Get Occupancy Report
GET `/core/apartments/report/?start_date=2024-01-01&end_date=2024-01-31`

Response:
```json
{
  "period":"2024-01-01 to 2024-01-31",
  "occupancy_trends":[
    {
      "date":"2024-01-01",
      "total_apartments":150,
      "occupied":120,
      "occupancy_rate":80.0
    }
  ],
  "estate_breakdown":[
    {
      "estate_name":"Sunset Gardens",
      "avg_occupancy":88.5,
      "peak_occupancy":95.0,
      "lowest_occupancy":82.0
    }
  ]
}
```

Optional filters:
- `?estate_id=1`
- `?block_id=2`

---

## 2. Payment Status

### Summary (All Estates)
GET `/payments/payments/dashboard_summary/`

Response:
```json
{
  "total_payments":450,
  "paid_payments":380,
  "pending_payments":50,
  "overdue_payments":20,
  "monthly_revenue":180000000,
  "payment_rate":84.4
}
```

### Status by Estate
GET `/payments/payments/estate_payment_status/`

Response:
```json
[
  {
    "estate_id":1,
    "estate_name":"Sunset Gardens",
    "total_apartments":50,
    "occupied_apartments":45,
    "total_rent_expected":22500000,
    "rent_collected":20250000,
    "collection_rate":90.0,
    "overdue_tenants":[
      {
        "tenant_id":1,
        "tenant_name":"John Doe",
        "apartment":"A101",
        "overdue_months":2
      }
    ],
    "overdue_count":3
  }
]
```

### Payment Alerts
GET `/payments/payments/payment_alerts/`

Response:
```json
{
  "overdue_alerts":[
    {
      "payment_id":1,
      "tenant_name":"John Doe",
      "apartment":"A101",
      "amount":"500000.00",
      "due_date":"2024-01-15",
      "days_overdue":15,
      "estate":"Sunset Gardens"
    }
  ],
  "upcoming_alerts":[
    {
      "payment_id":2,
      "tenant_name":"Jane Smith",
      "apartment":"B202",
      "amount":"600000.00", 
      "due_date":"2024-02-01",
      "days_until_due":5,
      "estate":"City Heights"
    }
  ],
  "recent_payments":[
    {
      "payment_id":3,
      "tenant_name":"Bob Johnson",
      "apartment":"C101",
      "amount":"550000.00",
      "paid_at":"2024-01-28T10:30:00Z",
      "estate":"Green Valley"
    }
  ]
}
```

### Payment Report
GET `/payments/payments/report/?start_date=2024-01-01&end_date=2024-01-31`

Response:
```json
{
  "period":"2024-01-01 to 2024-01-31",
  "total_payments":125,
  "total_amount":"62500000.00",
  "paid_amount":"56250000.00",
  "pending_amount":"6250000.00",
  "overdue_amount":"2500000.00",
  "estates":[
    {
      "estate_name":"Sunset Gardens",
      "payments":45,
      "total_amount":"22500000.00",
      "paid_amount":"20250000.00",
      "collection_rate":90.0
    }
  ]
}
```

---

## 3. Complaint Status

### Analytics
GET `/complaints/complaints/dashboard_analytics/`

Response:
```json
{
  "total_complaints":85,
  "open_complaints":12,
  "in_progress_complaints":8,
  "resolved_complaints":60,
  "closed_complaints":5,
  "avg_resolution_time":3.2,
  "estates":[
    {
      "estate_id":1,
      "estate_name":"Sunset Gardens",
      "total_complaints":25,
      "open_complaints":3,
      "resolution_rate":88.0,
      "avg_resolution_days":2.8,
      "blocks":[
        {
          "block_id":1,
          "block_name":"Block A",
          "complaints":10,
          "open":1,
          "resolved":9
        }
      ]
    }
  ]
}
```

### Trends
GET `/complaints/complaints/trends/?days=30`

Response:
```json
{
  "period":"Last 30 days",
  "new_complaints":25,
  "resolved_complaints":22,
  "trends":[
    {"date":"2024-01-15","new":3,"resolved":2},
    {"date":"2024-01-16","new":1,"resolved":4}
  ]
}
```

### Complaint Report
GET `/complaints/complaints/report/?start_date=2024-01-01&end_date=2024-01-31`

Response:
```json
{
  "period":"2024-01-01 to 2024-01-31",
  "total_complaints":45,
  "resolved_complaints":38,
  "avg_resolution_time":3.5,
  "complaint_categories":[
    {
      "category":"Amenities",
      "count":18,
      "resolution_rate":85.0
    }
  ],
  "estate_breakdown":[
    {
      "estate_name":"Sunset Gardens",
      "complaints":15,
      "resolution_rate":90.0
    }
  ]
}
```

---

## 4. Tenancy Expiry Status

### Expiry Dashboard
GET `/tenants/tenants/expiry_dashboard/`

Response:
```json
{
  "expiring_soon":[
    {
      "tenant_id":1,
      "tenant_name":"John Doe",
      "apartment":"A101",
      "lease_end":"2024-02-15",
      "days_until_expiry":15,
      "estate":"Sunset Gardens",
      "block":"Block A"
    }
  ],
  "expired_leases":[
    {
      "tenant_id":2,
      "tenant_name":"Jane Smith",
      "apartment":"B202",
      "lease_end":"2024-01-10",
      "days_overdue":20,
      "estate":"City Heights",
      "block":"Block B"
    }
  ],
  "expiring_this_month":8,
  "expiring_next_month":12,
  "expired_total":3,
  "renewal_rate":75.0
}
```

### Expiring in Range
GET `/tenants/tenants/expiring/?start_date=2024-01-01&end_date=2024-01-31`

Response:
```json
{
  "period":"2024-01-01 to 2024-01-31",
  "expiring_tenants":[
    {
      "tenant_id":1,
      "tenant_name":"John Doe",
      "apartment":"A101",
      "lease_end":"2024-01-31",
      "estate":"Sunset Gardens",
      "block":"Block A"
    }
  ],
  "count":8
}
```

---

### Error Responses

- **401 Unauthorized**: missing or invalid token
- **404 Not Found**: resource not found
- **400 Bad Request**: invalid parameters

Include error JSON: `{"error":"message"}` or standard DRF `{"detail":"message"}`.

---

This completes the Property Owner (ED) dashboard API reference for occupancy, payments, complaints, and tenancy expiry functionalities.