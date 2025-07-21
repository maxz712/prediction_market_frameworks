# Unified Pagination System

This document describes the unified pagination system implemented in the Polymarket client framework.

## Overview

The pagination system provides a consistent interface for handling paginated API responses across different Polymarket APIs (Gamma, CLOB, etc.). It supports:

- **Offset-based pagination** (limit + offset)
- **Automatic pagination** through multiple pages
- **Streaming iteration** for memory-efficient processing
- **Pagination metadata** tracking

## Core Components

### 1. Pagination Strategy (`PaginationStrategy`)

Abstract base class that defines the interface for different pagination strategies:

```python
from src.polymarket_client.pagination import PaginationStrategy

class OffsetPaginationStrategy(PaginationStrategy[T]):
    """Implements offset-based pagination (limit + offset)"""
```

### 2. Paginator (`Paginator`)

The main class that handles pagination logic:

```python
from src.polymarket_client.pagination import Paginator

paginator = Paginator(
    strategy=strategy,
    default_page_size=100,
    max_total_results=1000,
    auto_paginate=True
)
```

### 3. Pagination Models

- `PaginationInfo`: Metadata about the current page
- `PaginatedResponse[T]`: Generic wrapper for paginated data with metadata

## Usage Examples

### Basic Pagination with Polymarket Client

```python
from src.polymarket_client import PolymarketClient

client = PolymarketClient.from_env()

# Get events with auto-pagination (fetches all pages)
events = client.get_events(limit=500, auto_paginate=True)

# Get single page
first_page = client.get_events(limit=50, auto_paginate=False)

# Get specific page using offset
third_page = client.get_events(limit=50, offset=100, auto_paginate=False)
```

### Streaming Large Datasets

For memory-efficient processing of large datasets:

```python
# Process events one at a time
for event in client.iter_events(page_size=100):
    # Process each event
    print(f"Processing: {event.title}")
    
    # Can break early if needed
    if some_condition:
        break
```

### Getting Pagination Metadata

```python
# Get response with pagination info
response = client.get_events_paginated(limit=50)

print(f"Current page: {response.pagination.page}")
print(f"Has next page: {response.pagination.has_next}")
print(f"Total items: {len(response.data)}")

# Access the data
for event in response.data:
    print(event.title)
```

### Custom Pagination Implementation

You can create custom paginators for any API endpoint:

```python
from src.polymarket_client.pagination import create_offset_paginator
from pydantic import BaseModel

# Define your model
class MyModel(BaseModel):
    id: str
    name: str
    value: float

# Define fetch function
def fetch_data(**kwargs) -> list[dict]:
    # Make API call with kwargs (limit, offset, etc.)
    response = make_api_call("/my-endpoint", params=kwargs)
    return response.json()

# Create paginator
paginator = create_offset_paginator(
    fetch_func=fetch_data,
    model_class=MyModel,
    config=config  # PolymarketConfig instance
)

# Use paginator
all_data = paginator.fetch_all(limit=1000)
paginated = paginator.fetch_paginated(limit=50)

for item in paginator.iter_pages(page_size=25):
    process(item)
```

## Configuration

Pagination behavior is controlled by `PolymarketConfig`:

```python
from src.polymarket_client.configs import PolymarketConfig

config = PolymarketConfig(
    # Pagination settings
    default_page_size=100,        # Default items per page
    max_page_size=1000,          # Maximum allowed page size
    max_total_results=10000,     # Maximum total results to fetch
    enable_auto_pagination=True,  # Auto-paginate by default
    warn_large_requests=True     # Warn about large requests
)
```

## Best Practices

1. **Use streaming for large datasets**: Use `iter_events()` instead of `get_events()` when processing many items to avoid memory issues.

2. **Set reasonable limits**: Always specify a `limit` to avoid accidentally fetching too much data.

3. **Disable auto-pagination for single pages**: Set `auto_paginate=False` when you only need one page.

4. **Handle pagination metadata**: Use `get_events_paginated()` when you need to know about pagination state.

5. **Batch processing**: Process data in reasonable batch sizes:
   ```python
   for event in client.iter_events(page_size=100):
       # Process in batches of 100
   ```

## Migration Guide

If you're updating existing code to use the unified pagination system:

### Before (Direct API calls):
```python
# Manual pagination
all_events = []
offset = 0
while True:
    response = gamma_client._session.get("/events", params={"limit": 100, "offset": offset})
    events = response.json()
    if not events:
        break
    all_events.extend(events)
    offset += 100
```

### After (Unified pagination):
```python
# Automatic pagination
events = client.get_events(limit=1000, auto_paginate=True)

# Or streaming
for event in client.iter_events(page_size=100):
    process(event)
```

## Performance Considerations

1. **Memory usage**: Auto-pagination loads all results into memory. For large datasets (>10,000 items), use streaming iteration.

2. **API rate limits**: The pagination system respects rate limits through the retry mechanism, but be mindful of making too many requests.

3. **Network efficiency**: Larger page sizes mean fewer API calls but more memory usage. Find the right balance for your use case.

## Extending the System

To add pagination support to new endpoints:

1. Create a fetch function that accepts `limit` and `offset` parameters
2. Use `create_offset_paginator()` to create a paginator
3. Optionally, create convenience methods that use the paginator

Example:
```python
class MyClient:
    def get_items(self, limit=None, offset=0, auto_paginate=None):
        paginator = create_offset_paginator(
            fetch_func=self._fetch_items_raw,
            model_class=Item,
            config=self.config,
            initial_offset=offset
        )
        
        if auto_paginate is None:
            auto_paginate = self.config.enable_auto_pagination
            
        paginator.auto_paginate = auto_paginate
        return paginator.fetch_all(limit=limit)
```