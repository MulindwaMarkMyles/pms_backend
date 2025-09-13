# Available Apartments API Documentation

## Overview
The Available Apartments API provides smart filtering and comprehensive apartment data for efficient tenant allocation. It includes intelligent scoring, categorization, and detailed property information to help match tenants with suitable apartments.

## Base Endpoint
```
GET /api/core/apartments/available/
```

---

## 🎯 Smart Filtering Parameters

### Room-Based Filtering
```
?min_rooms=2&max_rooms=4
```
- `min_rooms` - Minimum number of rooms required
- `max_rooms` - Maximum number of rooms allowed

### Budget Filtering
```
?min_rent=15000&max_rent=30000
```
- `min_rent` - Minimum rent amount
- `max_rent` - Maximum rent amount

### Size Filtering
```
?min_size=50&max_size=120
```
- `min_size` - Minimum apartment size (square meters)
- `max_size` - Maximum apartment size (square meters)

### Location Filtering
```
?estate_id=1&block_id=3
```
- `estate_id` - Filter by specific estate
- `block_id` - Filter by specific block

### Feature Filtering
```
?amenities=1&amenities=2&furnishings=3&furnishings=4
```
- `amenities` - Multiple amenity IDs (can repeat parameter)
- `furnishings` - Multiple furnishing IDs (can repeat parameter)

---

## 📊 Response Structure

### Main Response
```json
{
  "total_available": 15,
  "apartments": [...],
  "summary": {...},
  "filters_applied": {...}
}
```

### Individual Apartment Object
```json
{
  "id": 1,
  "number": "A101",
  "block": {
    "id": 1,
    "name": "Block A",
    "description": "Modern residential block",
    "estate": {
      "id": 1,
      "name": "Sunrise Estate",
      "address": "123 Main Street, Kampala",
      "description": "Premium residential estate"
    }
  },
  "rent_amount": "25000.00",
  "number_of_rooms": 3,
  "size": "75.50",
  "color": "Blue",
  "description": "Spacious 3-bedroom apartment",
  "amenities": [
    {
      "id": 1,
      "name": "Swimming Pool",
      "description": "Olympic-size swimming pool"
    }
  ],
  "furnishings": [
    {
      "id": 1,
      "name": "Air Conditioning",
      "description": "Central air conditioning system"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  
  // Smart Metrics
  "allocation_score": 85,
  "rent_per_room": 8333.33,
  "rent_per_sqm": 331.13,
  "is_furnished": true,
  "amenities_count": 3,
  "furnishings_count": 2,
  
  // Categories
  "room_category": "2-bedroom",
  "size_category": "large",
  "rent_category": "affordable",
  
  // Location Info
  "full_address": "Sunrise Estate - Block A - A101",
  "location_hierarchy": {
    "estate": "Sunrise Estate",
    "block": "Block A",
    "apartment": "A101"
  }
}
```

### Summary Statistics
```json
{
  "summary": {
    "by_room_category": {
      "studio": 2,
      "1-bedroom": 5,
      "2-bedroom": 8,
      "3-bedroom": 3
    },
    "by_size_category": {
      "small": 3,
      "medium": 7,
      "large": 5,
      "extra-large": 2
    },
    "by_rent_category": {
      "budget": 4,
      "affordable": 8,
      "moderate": 5,
      "premium": 1
    },
    "by_estate": {
      "Sunrise Estate": 10,
      "Garden View": 5,
      "City Center": 3
    },
    "average_rent": 22500.00,
    "average_size": 68.75,
    "furnished_count": 12,
    "unfurnished_count": 6
  }
}
```

---

## 🚀 Usage Examples

### 1. Basic Available Apartments
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/core/apartments/available/"
```

### 2. Family-Sized Apartments
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/core/apartments/available/?min_rooms=3&max_rooms=5"
```

### 3. Budget-Friendly Options
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/core/apartments/available/?max_rent=20000"
```

### 4. Specific Estate with Amenities
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/core/apartments/available/?estate_id=1&amenities=1&amenities=2"
```

### 5. Complex Filtering
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/core/apartments/available/?min_rooms=2&max_rent=30000&min_size=50&estate_id=1&amenities=1"
```

---

## 🧠 Smart Features Explained

### Allocation Score
- **Range**: 0-120+ points
- **Factors**: Room count, size, amenities, furnishings, rent efficiency
- **Usage**: Higher scores indicate better value/features
- **Sorting**: Results automatically sorted by score (highest first)

### Room Categories
- `studio` - 1 room
- `1-bedroom` - 2 rooms
- `2-bedroom` - 3 rooms
- `3-bedroom` - 4 rooms
- `large-family` - 5+ rooms

### Size Categories
- `small` - < 30 sqm
- `medium` - 30-59 sqm
- `large` - 60-99 sqm
- `extra-large` - 100+ sqm

### Rent Categories
- `budget` - < $10,000
- `affordable` - $10,000-$19,999
- `moderate` - $20,000-$34,999
- `premium` - $35,000-$49,999
- `luxury` - $50,000+

---

## 💡 Best Practices

### 1. Use Smart Filtering
```javascript
// Instead of fetching all and filtering client-side
const response = await fetch('/api/core/apartments/available/?min_rooms=2&max_rent=25000');

// This is more efficient than:
const all = await fetch('/api/core/apartments/available/');
const filtered = all.filter(apt => apt.number_of_rooms >= 2 && apt.rent_amount <= 25000);
```

### 2. Utilize Allocation Scores
```javascript
// Apartments are pre-sorted by allocation_score
const apartments = response.data.apartments;
const topRecommendations = apartments.slice(0, 5); // Get top 5 scored apartments
```

### 3. Check Summary for Quick Overview
```javascript
const summary = response.data.summary;
console.log(`Found ${summary.furnished_count} furnished apartments`);
console.log(`Average rent: $${summary.average_rent}`);
```

### 4. Use Categories for UI Grouping
```javascript
// Group by room category
const byRooms = response.data.apartments.reduce((acc, apt) => {
  const category = apt.room_category;
  if (!acc[category]) acc[category] = [];
  acc[category].push(apt);
  return acc;
}, {});
```

---

## 🔍 Integration Examples

### React Component Example
```jsx
import React, { useState, useEffect } from 'react';

const AvailableApartments = () => {
  const [apartments, setApartments] = useState([]);
  const [filters, setFilters] = useState({
    min_rooms: '',
    max_rent: '',
    estate_id: ''
  });

  const fetchApartments = async () => {
    const params = new URLSearchParams(filters).toString();
    const response = await fetch(`/api/core/apartments/available/?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setApartments(data.apartments);
  };

  return (
    <div>
      <div className="filters">
        <input 
          type="number" 
          placeholder="Min Rooms"
          value={filters.min_rooms}
          onChange={(e) => setFilters({...filters, min_rooms: e.target.value})}
        />
        <input 
          type="number" 
          placeholder="Max Rent"
          value={filters.max_rent}
          onChange={(e) => setFilters({...filters, max_rent: e.target.value})}
        />
        <button onClick={fetchApartments}>Search</button>
      </div>

      <div className="apartments">
        {apartments.map(apt => (
          <div key={apt.id} className="apartment-card">
            <h3>{apt.full_address}</h3>
            <p>Rooms: {apt.number_of_rooms} | Size: {apt.size}sqm</p>
            <p>Rent: ${apt.rent_amount} | Score: {apt.allocation_score}</p>
            <p>Category: {apt.room_category} | {apt.size_category} | {apt.rent_category}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### Python Client Example
```python
import requests

class ApartmentFinder:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def find_apartments(self, **filters):
        """Find apartments with smart filtering"""
        url = f"{self.base_url}/api/core/apartments/available/"
        response = requests.get(url, params=filters, headers=self.headers)
        return response.json()
    
    def find_family_apartments(self, min_rooms=3, max_rent=35000):
        """Find suitable family apartments"""
        return self.find_apartments(
            min_rooms=min_rooms,
            max_rent=max_rent,
            amenities=[1, 2]  # Swimming pool, playground
        )
    
    def find_budget_studios(self, max_rent=15000):
        """Find budget-friendly studio apartments"""
        return self.find_apartments(
            max_rooms=1,
            max_rent=max_rent
        )

# Usage
finder = ApartmentFinder('http://localhost:8000', 'your-token')
family_apts = finder.find_family_apartments()
budget_studios = finder.find_budget_studios()
```

---

## 🔧 Error Handling

### Common HTTP Status Codes
- `200` - Success
- `401` - Unauthorized (invalid/missing token)
- `500` - Server error

### Error Response Format
```json
{
  "error": "Error message",
  "details": "Detailed error information"
}
```

---

## 📈 Performance Tips

1. **Use Specific Filters**: Narrow down results with filters to reduce response size
2. **Cache Results**: Cache apartment data that doesn't change frequently
3. **Pagination**: For large datasets, consider implementing pagination
4. **Index Usage**: Database queries are optimized with proper indexing

---

## 🔄 Related APIs

### Get Specific Apartment Details
```
GET /api/core/apartments/{id}/
```

### Get Apartments by Block
```
GET /api/core/apartments/?block_id=1
```

### Create Tenant Assignment
```
POST /api/tenants/tenants/
{
  "apartment": apartment_id,
  "user": {...},
  ...
}
```

---

## 📞 Support

For API support or feature requests, contact the development team or refer to the main project documentation.

---

## 🆕 Version History

- **v1.0** - Basic available apartments endpoint
- **v2.0** - Added smart filtering and scoring system
- **v2.1** - Enhanced categorization and summary statistics
