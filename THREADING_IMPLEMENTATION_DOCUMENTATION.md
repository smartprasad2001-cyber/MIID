# Threading Implementation Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Thread Safety Mechanisms](#thread-safety-mechanisms)
4. [Step-by-Step Example](#step-by-step-example)
5. [Cache File Thread Safety](#cache-file-thread-safety)
6. [Performance Benefits](#performance-benefits)
7. [Configuration](#configuration)

---

## Overview

The address cache generation script uses **parallel threading** to process multiple cities simultaneously within each country. This dramatically speeds up address generation for countries with many cities (e.g., 200+ cities).

### Key Features
- **Parallel City Processing**: Multiple cities processed simultaneously
- **Thread-Safe Operations**: All shared data protected with locks
- **Early Termination**: Stops when 15 addresses are found
- **Safe Cache Writing**: Only one thread writes to cache file at a time

---

## Architecture

### High-Level Flow

```
Main Thread (Sequential)
│
├── Country 1: "United States"
│   ├── Get all cities (e.g., 200 cities)
│   ├── Create ThreadPoolExecutor (8 threads)
│   ├── Submit all cities to thread pool
│   │   ├── Thread 1: Process "New York"
│   │   ├── Thread 2: Process "Los Angeles"
│   │   ├── Thread 3: Process "Chicago"
│   │   ├── ...
│   │   └── Thread 8: Process "Houston"
│   ├── Collect results (thread-safe)
│   └── Save to cache (thread-safe)
│
├── Country 2: "Canada"
│   └── (Same process)
│
└── ...
```

### Component Breakdown

1. **Main Thread**: Processes countries sequentially
2. **ThreadPoolExecutor**: Manages worker threads for city processing
3. **Worker Threads**: Process individual cities in parallel
4. **Shared Data Structures**: Protected with locks
5. **Cache File**: Protected with write lock

---

## Thread Safety Mechanisms

### 1. Shared Data Structures

All shared data structures are protected with a `threading.Lock()`:

```python
# Shared data structures (accessed by all threads)
address_list = []                    # List of valid addresses
seen_addresses = set()                # Exact string duplicates
seen_normalized_addresses = set()     # Normalized duplicates
tried_nodes = set()                   # Processed node IDs
stats = {}                            # Statistics dictionary

# Thread lock for protection
thread_lock = threading.Lock()
```

### 2. Lock Usage Pattern

Every access to shared data follows this pattern:

```python
# Example: Adding an address
with thread_lock:
    # Check if we already have 15 addresses
    if len(address_list) >= 15:
        break
    
    # Check for duplicates
    if normalized_display in seen_normalized_addresses:
        stats["duplicates_skipped"] += 1
        continue
    
    # Add to shared structures
    address_list.append(display)
    seen_addresses.add(display)
    seen_normalized_addresses.add(normalized_display)
    stats["validation_passed"] += 1
```

### 3. Protected Operations

| Operation | Lock Protection | Why? |
|-----------|----------------|------|
| `address_list.append()` | ✅ Yes | Prevents race conditions |
| `seen_addresses.add()` | ✅ Yes | Prevents duplicate checks from failing |
| `seen_normalized_addresses.add()` | ✅ Yes | Prevents duplicate checks from failing |
| `tried_nodes.add()` | ✅ Yes | Prevents processing same node twice |
| `stats["key"] += 1` | ✅ Yes | Prevents lost updates |
| `len(address_list)` | ✅ Yes | Prevents reading while writing |

---

## Step-by-Step Example

### Example: Processing "United States" with 200 Cities

#### Step 1: Initialization

```python
# Main thread
country = "United States"
cities = [200 cities from GeonamesCache]
address_list = []
seen_addresses = set()
seen_normalized_addresses = set()
tried_nodes = set()
stats = {"validation_passed": 0, ...}
thread_lock = threading.Lock()
```

#### Step 2: Create Thread Pool

```python
# Main thread creates ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=8, thread_name_prefix="CityWorker") as executor:
    # 8 worker threads are now available
```

#### Step 3: Submit Cities to Thread Pool

```python
# Main thread submits all 200 cities
future_to_city = {}
for city_idx, city in enumerate(cities, 1):
    future = executor.submit(
        process_single_city,
        city, city_idx, len(cities), country,
        address_list, seen_addresses, seen_normalized_addresses,
        tried_nodes, stats, thread_lock, verbose
    )
    future_to_city[future] = city_idx
```

**Result**: 200 tasks submitted, 8 threads start processing immediately.

#### Step 4: Parallel Processing (Detailed Example)

Let's trace what happens when 8 threads process cities simultaneously:

##### Thread 1: Processing "New York"

```python
def process_single_city(city, ...):
    # Thread 1: "New York"
    city_name = "New York"
    lat, lon = 40.7128, -74.0060
    
    # Step 1: Fetch nodes from Overpass (no lock needed)
    nodes = fetch_nodes_from_overpass_bbox(bbox)  # Returns 500 nodes
    
    # Step 2: Update stats (with lock)
    with thread_lock:
        stats["overpass_queries"] += 1
        stats["nodes_fetched"] += 500
    
    # Step 3: Process nodes
    for node in nodes:
        # Validate address (no lock needed - local operation)
        display = node_tags_to_display_name(node.tags, country)
        is_valid, score = validate_address_with_api(display, country)
        
        if is_valid and score >= 0.9:
            # Add to shared list (with lock)
            with thread_lock:
                if len(address_list) >= 15:
                    break  # Already have 15, stop processing
                
                # Check duplicates
                if display in seen_addresses:
                    continue
                
                # Add address
                address_list.append(display)  # Thread 1 adds: "123 Main St, New York, ..."
                seen_addresses.add(display)
                stats["validation_passed"] += 1
```

##### Thread 2: Processing "Los Angeles" (Simultaneously)

```python
# Thread 2: "Los Angeles" (running at the same time as Thread 1)
def process_single_city(city, ...):
    city_name = "Los Angeles"
    lat, lon = 34.0522, -118.2437
    
    nodes = fetch_nodes_from_overpass_bbox(bbox)  # Returns 300 nodes
    
    with thread_lock:
        stats["overpass_queries"] += 1
        stats["nodes_fetched"] += 300
    
    for node in nodes:
        display = node_tags_to_display_name(node.tags, country)
        is_valid, score = validate_address_with_api(display, country)
        
        if is_valid and score >= 0.9:
            with thread_lock:
                if len(address_list) >= 15:
                    break
                
                if display in seen_addresses:
                    continue
                
                address_list.append(display)  # Thread 2 adds: "456 Sunset Blvd, Los Angeles, ..."
                seen_addresses.add(display)
                stats["validation_passed"] += 1
```

#### Step 5: Concurrent Access Example

**Timeline of events** (simplified):

```
Time  | Thread 1 (NY)              | Thread 2 (LA)              | address_list
------|----------------------------|----------------------------|------------------
T0    | Fetching nodes...          | Fetching nodes...          | []
T1    | Validating address...      | Validating address...      | []
T2    | Acquiring lock...          | Validating address...      | []
T3    | Lock acquired              | Waiting for lock...        | []
T4    | Adding "123 Main St..."    | Waiting...                | []
T5    | Releasing lock             | Waiting...                | ["123 Main St..."]
T6    | Validating next...         | Lock acquired              | ["123 Main St..."]
T7    | Validating...               | Adding "456 Sunset..."     | ["123 Main St..."]
T8    | Validating...               | Releasing lock             | ["123 Main St...", "456 Sunset..."]
T9    | Acquiring lock...          | Validating next...         | ["123 Main St...", "456 Sunset..."]
T10   | Adding "789 Broadway..."   | Validating...              | ["123 Main St...", "456 Sunset..."]
T11   | Releasing lock             | Validating...              | ["123 Main St...", "456 Sunset...", "789 Broadway..."]
```

**Key Points**:
- Threads work on different cities simultaneously
- Lock ensures only one thread modifies shared data at a time
- No data corruption or race conditions

#### Step 6: Early Termination

When 15 addresses are found:

```python
# Thread 3 finds the 15th address
with thread_lock:
    if len(address_list) >= 15:  # Now has 15 addresses
        break  # Thread 3 stops processing

# Main thread detects 15 addresses
for future in as_completed(future_to_city):
    with thread_lock:
        if len(address_list) >= 15:
            # Cancel remaining tasks
            for f in future_to_city:
                if not f.done():
                    f.cancel()  # Stop processing remaining cities
            break
```

**Result**: 
- Threads that already started continue until their current city is done
- Remaining cities are cancelled (not processed)
- Saves time and resources

---

## Cache File Thread Safety

### Problem

The cache file (`validated_address_cache_all_cities.json`) is written after each country is processed. If multiple threads tried to write simultaneously, it could cause:
- File corruption
- Lost data
- Inconsistent state

### Solution: Write Lock

```python
# Global lock for cache file writes
_cache_save_lock = threading.Lock()

def save_cache_safely(address_cache, failed_countries, cache_file, ...):
    lock_acquired = False
    try:
        # Acquire lock (blocking - waits if another save is in progress)
        _cache_save_lock.acquire(blocking=True)
        lock_acquired = True
        
        # Write to temp file
        temp_file = cache_file + ".tmp"
        with open(temp_file, "w") as f:
            json.dump(cache_data, f)
        
        # Atomic rename (prevents partial writes)
        os.replace(temp_file, cache_file)
        
    finally:
        # Always release lock
        if lock_acquired:
            _cache_save_lock.release()
```

### Example: Concurrent Cache Saves

**Scenario**: Two countries finish processing at nearly the same time

```
Time  | Country 1 Thread              | Country 2 Thread              | Cache File
------|-------------------------------|-------------------------------|------------------
T0    | Finished processing           | Finished processing           | {old data}
T1    | Calling save_cache_safely()  | Calling save_cache_safely()  | {old data}
T2    | Acquiring lock...             | Acquiring lock...             | {old data}
T3    | Lock acquired ✅              | Waiting for lock...           | {old data}
T4    | Writing temp file...          | Waiting...                    | {old data}
T5    | Renaming temp → cache         | Waiting...                    | {Country 1 data}
T6    | Releasing lock                | Waiting...                    | {Country 1 data}
T7    | Done                          | Lock acquired ✅              | {Country 1 data}
T8    |                               | Writing temp file...          | {Country 1 data}
T9    |                               | Renaming temp → cache         | {Country 1 + 2 data}
T10   |                               | Releasing lock                | {Country 1 + 2 data}
```

**Result**: 
- Both saves complete successfully
- Latest data is preserved
- No file corruption

---

## Performance Benefits

### Before Threading (Sequential)

```
Country: United States (200 cities)
Time per city: ~30 seconds
Total time: 200 × 30 = 6,000 seconds = 100 minutes
```

### After Threading (8 threads)

```
Country: United States (200 cities)
Time per city: ~30 seconds
Parallel processing: 200 ÷ 8 = 25 batches
Total time: 25 × 30 = 750 seconds = 12.5 minutes
```

**Speedup**: ~8x faster (theoretical maximum)

### Real-World Example

**Country**: India (1,000+ cities)

| Method | Time | Notes |
|--------|------|-------|
| Sequential | ~8.3 hours | 1,000 cities × 30s |
| 8 Threads | ~1 hour | 1,000 ÷ 8 × 30s |
| 10 Threads | ~50 minutes | 1,000 ÷ 10 × 30s |

---

## Configuration

### Default Settings

```python
MAX_WORKER_THREADS = 8  # Default: 8 threads
```

### Custom Configuration

```bash
# Use 10 threads
MAX_WORKER_THREADS=10 python3 generate_address_cache.py

# Use 5 threads (for slower systems)
MAX_WORKER_THREADS=5 python3 generate_address_cache.py

# Use 16 threads (for powerful systems)
MAX_WORKER_THREADS=16 python3 generate_address_cache.py
```

### Choosing the Right Number

| System | Recommended Threads | Reason |
|--------|---------------------|--------|
| Low-end (2-4 cores) | 4-6 | Avoids CPU overload |
| Mid-range (4-8 cores) | 8-10 | Good balance |
| High-end (8+ cores) | 12-16 | Maximum performance |
| API-limited | 4-6 | Respects rate limits |

**Note**: More threads ≠ always faster. Consider:
- API rate limits (Nominatim: 1 req/sec)
- Network bandwidth
- CPU cores
- Memory usage

---

## Thread Safety Checklist

✅ **All shared data protected with locks**
- `address_list` - ✅ Protected
- `seen_addresses` - ✅ Protected
- `seen_normalized_addresses` - ✅ Protected
- `tried_nodes` - ✅ Protected
- `stats` - ✅ Protected

✅ **Cache file writes are serialized**
- Only one thread writes at a time
- Atomic file operations (temp + rename)
- Lock always released

✅ **Early termination is safe**
- Threads check `len(address_list)` with lock
- Cancellation doesn't corrupt data
- Remaining tasks are properly cancelled

✅ **No race conditions**
- All reads/writes to shared data use locks
- Minimal lock time (only when necessary)
- No deadlocks (locks always released)

---

## Troubleshooting

### Issue: "Cache save already in progress, skipping..."

**Cause**: Multiple cache saves attempted simultaneously

**Solution**: Already fixed! The new implementation waits for the lock instead of skipping.

### Issue: Slow performance with many threads

**Possible Causes**:
1. API rate limiting (Nominatim: 1 req/sec)
2. Network bandwidth limits
3. Too many threads competing for resources

**Solution**: Reduce `MAX_WORKER_THREADS` to 4-6

### Issue: High memory usage

**Cause**: Too many threads processing large cities simultaneously

**Solution**: Reduce `MAX_WORKER_THREADS` or process smaller batches

---

## Summary

The threading implementation provides:

1. **Parallel Processing**: Multiple cities processed simultaneously
2. **Thread Safety**: All shared data protected with locks
3. **Early Termination**: Stops when 15 addresses found
4. **Safe Cache Writing**: Only one thread writes at a time
5. **Performance**: ~8x speedup for countries with many cities

The implementation is production-ready and handles edge cases like concurrent cache saves, early termination, and API rate limiting.





