# Property Management System - Property Owner APIs

## Table of Contents
- [Authentication](#authentication)
- [Dashboard Module](#dashboard-module)
- [Payment Alerts & Reports](#payment-alerts--reports)
- [Occupancy Status](#occupancy-status)
- [Complaint Analytics](#complaint-analytics)
- [Tenancy Expiry Status](#tenancy-expiry-status)
- [Error Handling](#error-handling)

## Base URL
```
http://127.0.0.1:8000
```

## Authentication

### Login (Get Token)
**POST** `/api/token/`

**Request Body:**
```json
{
    "username": "property_owner",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## Dashboard Module

### 1. Occupancy Status

#### Get Overall Occupancy Summary
**GET** `/api/core/dashboard/occupancy/`

**Response (200 OK):**
```json
{
    "total_estates": 3,
    "total_apartments": 150,
    "occupied_apartments": 120,
    "vacant_apartments": 30,
    "occupancy_rate": 80.0,
    "estates": [
        {
            "estate_id": 1,
            "estate_name": "Sunset Gardens Estate",
            "total_apartments": 50,
            "occupied_apartments": 45,
            "vacant_apartments": 5,
            "occupancy_rate": 90.0,
            "blocks": [
                {
                    "block_id": 1,
                    "block_name": "Block A",
                    "total_apartments": 25,
                    "occupied_apartments": 22,
                    "vacant_apartments": 3,
                    "occupancy_rate": 88.0
                }
            ]
        }
    ]
}
```

#### Get Estate-Specific Occupancy
**GET** `/api/core/dashboard/occupancy/?estate_id=1`

#### Get Block-Specific Occupancy
**GET** `/api/core/dashboard/occupancy/?block_id=1`

### 2. Payment Status Dashboard

#### Get Payment Dashboard Summary
**GET** `/api/payments/payments/dashboard_summary/`

**Response (200 OK):**
```json
{
    "total_payments": 450,
    "paid_payments": 380,
    "pending_payments": 50,
    "overdue_payments": 20,
    "monthly_revenue": 180000000,
    "payment_rate": 84.4
}
```

#### Get Payment Status by Estate
**GET** `/api/payments/payments/estate_payment_status/`

**Response (200 OK):**
```json
[
    {
        "estate_id": 1,
        "estate_name": "Sunset Gardens Estate",
        "total_apartments": 50,
        "occupied_apartments": 45,
        "total_rent_expected": 22500000,
        "rent_collected": 20250000,
        "collection_rate": 90.0,
        "overdue_tenants": [
            {
                "tenant_id": 5,
                "tenant_name": "John Doe",
                "apartment": "A101",
                "overdue_months": 2
            }
        ],
        "overdue_count": 3
    }
]
```

### 3. Complaint Status Dashboard

#### Get Complaint Analytics
**GET** `/api/complaints/complaints/dashboard_analytics/`

**Response (200 OK):**
```json
{
    "total_complaints": 85,
    "open_complaints": 12,
    "in_progress_complaints": 8,
    "resolved_complaints": 60,
    "closed_complaints": 5,
    "avg_resolution_time": 3.2,
    "estates": [
        {
            "estate_id": 1,
            "estate_name": "Sunset Gardens Estate",
            "total_complaints": 35,
            "open_complaints": 5,
            "resolution_rate": 85.7,
            "avg_resolution_days": 2.8,
            "blocks": [
                {
                    "block_id": 1,
                    "block_name": "Block A",
                    "complaints": 15,
                    "open": 3,
                    "resolved": 12
                }
            ]
        }
    ]
}
```

#### Get Complaint Trends (Last 30 Days)
**GET** `/api/complaints/complaints/trends/?days=30`

**Response (200 OK):**
```json
{
    "period": "Last 30 days",
    "new_complaints": 25,
    "resolved_complaints": 22,
    "trends": [
        {
            "date": "2024-01-15",
            "new": 3,
            "resolved": 2
        },
        {
            "date": "2024-01-16",
            "new": 1,
            "resolved": 4
        }
    ]
}
```

### 4. Tenancy Expiry Status

#### Get Tenancy Expiry Dashboard
**GET** `/api/tenants/tenants/expiry_dashboard/`

**Response (200 OK):**
```json
{
    "expiring_soon": [
        {
            "tenant_id": 1,
            "tenant_name": "John Doe",
            "apartment": "A101",
            "lease_end": "2024-02-15",
            "days_until_expiry": 15,
            "estate": "Sunset Gardens Estate",
            "block": "Block A"
        }
    ],
    "expired_leases": [
        {
            "tenant_id": 2,
            "tenant_name": "Jane Smith",
            "apartment": "B205",
            "lease_end": "2024-01-10",
            "days_overdue": 5,
            "estate": "Riverside Apartments",
            "block": "Block B"
        }
    ],
    "expiring_this_month": 8,
    "expiring_next_month": 12,
    "expired_total": 3,
    "renewal_rate": 75.0
}
```

#### Get Tenants Expiring in Date Range
**GET** `/api/tenants/tenants/expiring/?start_date=2024-01-01&end_date=2024-01-31`

---

## Payment Alerts & Reports

### 1. Payment Alerts

#### Get All Payment Alerts
**GET** `/api/payments/payments/payment_alerts/`

**Response (200 OK):**
```json
{
    "overdue_alerts": [
        {
            "payment_id": 15,
            "tenant_name": "John Doe",
            "apartment": "A101",
            "amount": "500000.00",
            "due_date": "2024-01-01",
            "days_overdue": 14,
            "estate": "Sunset Gardens Estate"
        }
    ],
    "upcoming_alerts": [
        {
            "payment_id": 20,
            "tenant_name": "Jane Smith",
            "apartment": "B205",
            "amount": "450000.00",
            "due_date": "2024-01-20",
            "days_until_due": 5,
            "estate": "Riverside Apartments"
        }
    ],
    "recent_payments": [
        {
            "payment_id": 18,
            "tenant_name": "Bob Johnson",
            "apartment": "C301",
            "amount": "550000.00",
            "paid_at": "2024-01-14T10:30:00Z",
            "estate": "Green Valley Estate"
        }
    ]
}
```

### 2. Detailed Reports

#### Get Payment Report by Date Range
**GET** `/api/payments/payments/report/?start_date=2024-01-01&end_date=2024-01-31`

**Response (200 OK):**
```json
{
    "period": "2024-01-01 to 2024-01-31",
    "total_payments": 150,
    "total_amount": 75000000,
    "paid_amount": 67500000,
    "pending_amount": 5250000,
    "overdue_amount": 2250000,
    "estates": [
        {
            "estate_name": "Sunset Gardens Estate",
            "payments": 50,
            "total_amount": 25000000,
            "paid_amount": 22500000,
            "collection_rate": 90.0
        }
    ]
}
```

#### Get Occupancy Report
**GET** `/api/core/dashboard/occupancy/report/?start_date=2024-01-01&end_date=2024-01-31`

**Response (200 OK):**
```json
{
    "period": "2024-01-01 to 2024-01-31",
    "occupancy_trends": [
        {
            "date": "2024-01-01",
            "total_apartments": 150,
            "occupied": 120,
            "occupancy_rate": 80.0
        }
    ],
    "estate_breakdown": [
        {
            "estate_name": "Sunset Gardens Estate",
            "avg_occupancy": 88.5,
            "peak_occupancy": 95.0,
            "lowest_occupancy": 82.0
        }
    ]
}
```

#### Get Complaint Report
**GET** `/api/complaints/complaints/report/?start_date=2024-01-01&end_date=2024-01-31`

**Response (200 OK):**
```json
{
    "period": "2024-01-01 to 2024-01-31",
    "total_complaints": 85,
    "resolved_complaints": 75,
    "avg_resolution_time": 3.2,
    "complaint_categories": [
        {
            "category": "Maintenance",
            "count": 35,
            "resolution_rate": 88.6
        },
        {
            "category": "Facilities",
            "count": 25,
            "resolution_rate": 92.0
        }
    ],
    "estate_breakdown": [
        {
            "estate_name": "Sunset Gardens Estate",
            "complaints": 35,
            "resolution_rate": 85.7
        }
    ]
}
```

---

## Additional API Endpoints

### Get All Estates
**GET** `/api/core/estates/`

### Get All Tenants
**GET** `/api/tenants/tenants/`

### Get All Payments
**GET** `/api/payments/payments/`

### Get All Complaints
**GET** `/api/complaints/complaints/`

### Get Pending Payments
**GET** `/api/payments/payments/pending_payments/`

### Get Overdue Payments
**GET** `/api/payments/payments/overdue_payments/`

---

## Frontend Implementation Guide

### 1. Dashboard Page Structure

```javascript
// Dashboard Component Structure
const Dashboard = () => {
    const [occupancyData, setOccupancyData] = useState(null);
    const [paymentData, setPaymentData] = useState(null);
    const [complaintData, setComplaintData] = useState(null);
    const [tenancyData, setTenancyData] = useState(null);

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            const [occupancy, payments, complaints, tenancy] = await Promise.all([
                fetch('/api/core/dashboard/occupancy/', { headers: authHeaders }),
                fetch('/api/payments/payments/dashboard_summary/', { headers: authHeaders }),
                fetch('/api/complaints/complaints/dashboard_analytics/', { headers: authHeaders }),
                fetch('/api/tenants/tenants/expiry_dashboard/', { headers: authHeaders })
            ]);

            setOccupancyData(await occupancy.json());
            setPaymentData(await payments.json());
            setComplaintData(await complaints.json());
            setTenancyData(await tenancy.json());
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    };

    return (
        <div className="dashboard">
            <OccupancyWidget data={occupancyData} />
            <PaymentWidget data={paymentData} />
            <ComplaintWidget data={complaintData} />
            <TenancyWidget data={tenancyData} />
        </div>
    );
};
```

### 2. Real-time Alerts

```javascript
// Alerts Component
const Alerts = () => {
    const [alerts, setAlerts] = useState(null);

    useEffect(() => {
        const loadAlerts = async () => {
            const response = await fetch('/api/payments/payments/payment_alerts/', {
                headers: authHeaders
            });
            const data = await response.json();
            setAlerts(data);
        };

        loadAlerts();
        // Refresh every 5 minutes
        const interval = setInterval(loadAlerts, 300000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="alerts">
            <OverdueAlerts alerts={alerts?.overdue_alerts || []} />
            <UpcomingAlerts alerts={alerts?.upcoming_alerts || []} />
            <RecentPayments payments={alerts?.recent_payments || []} />
        </div>
    );
};
```

### 3. Reports Page

```javascript
// Reports Component
const Reports = () => {
    const [reportType, setReportType] = useState('payments');
    const [dateRange, setDateRange] = useState({
        start_date: '2024-01-01',
        end_date: '2024-01-31'
    });
    const [reportData, setReportData] = useState(null);

    const generateReport = async () => {
        let endpoint = '';
        switch(reportType) {
            case 'payments':
                endpoint = '/api/payments/payments/report/';
                break;
            case 'occupancy':
                endpoint = '/api/core/dashboard/occupancy/report/';
                break;
            case 'complaints':
                endpoint = '/api/complaints/complaints/report/';
                break;
        }

        const params = new URLSearchParams(dateRange);
        const response = await fetch(`${endpoint}?${params}`, {
            headers: authHeaders
        });
        const data = await response.json();
        setReportData(data);
    };

    return (
        <div className="reports">
            <ReportFilters 
                reportType={reportType}
                setReportType={setReportType}
                dateRange={dateRange}
                setDateRange={setDateRange}
                onGenerate={generateReport}
            />
            <ReportDisplay data={reportData} type={reportType} />
        </div>
    );
};
```

---

## Error Handling

### Common HTTP Status Codes

- **200 OK** - Request successful
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

### Error Response Format
```json
{
    "error": "Error message description",
    "details": "Additional error details (if available)"
}
```

### Example Error Responses

**401 Unauthorized:**
```json
{
    "detail": "Given token not valid for any token type"
}
```

**404 Not Found:**
```json
{
    "detail": "Not found."
}
```

---

## Authentication Headers

```javascript
const authHeaders = {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
};
```

---

## Quick Start Guide for Property Owner Frontend

### 1. Authentication
1. Login to get JWT tokens
2. Store tokens in localStorage/sessionStorage
3. Include tokens in all API requests

### 2. Dashboard Implementation
1. Create dashboard component
2. Load all dashboard data on component mount
3. Display data in charts/widgets
4. Implement auto-refresh for real-time updates

### 3. Alerts System
1. Create alerts component
2. Poll alerts endpoint every 5 minutes
3. Show notifications for overdue payments
4. Highlight upcoming due dates

### 4. Reports System
1. Create reports component with filters
2. Allow date range selection
3. Generate different report types
4. Export functionality (optional)

### 5. Real-time Updates
1. Implement WebSocket or polling for real-time data
2. Update dashboard when new data arrives
3. Show toast notifications for important events

---

## API Response Data Structure

### Occupancy Data Structure
```javascript
{
    total_estates: number,
    total_apartments: number,
    occupied_apartments: number,
    vacant_apartments: number,
    occupancy_rate: number,
    estates: [
        {
            estate_id: number,
            estate_name: string,
            total_apartments: number,
            occupied_apartments: number,
            vacant_apartments: number,
            occupancy_rate: number,
            blocks: [
                {
                    block_id: number,
                    block_name: string,
                    total_apartments: number,
                    occupied_apartments: number,
                    vacant_apartments: number,
                    occupancy_rate: number
                }
            ]
        }
    ]
}
```

### Payment Data Structure
```javascript
{
    total_payments: number,
    paid_payments: number,
    pending_payments: number,
    overdue_payments: number,
    monthly_revenue: number,
    payment_rate: number
}
```

### Complaint Data Structure
```javascript
{
    total_complaints: number,
    open_complaints: number,
    in_progress_complaints: number,
    resolved_complaints: number,
    closed_complaints: number,
    avg_resolution_time: number,
    estates: [...]
}
```

This README provides everything needed to build a comprehensive Property Owner dashboard with real-time alerts and detailed reporting capabilities! 🎉