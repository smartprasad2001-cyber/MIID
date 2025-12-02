"""
Test timing for processing a full synapse with 15 names × 15 addresses = 225 addresses.
Check if it can complete in reasonable time.
"""

import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MIID', 'validator'))

from unified_generator import process_full_synapse

# Simulate a synapse with 15 identities
# Format: [name, dob, address]
test_identities = [
    ["John Smith", "1990-01-15", "United States"],
    ["Maria Garcia", "1985-03-22", "United States"],
    ["David Johnson", "1992-07-10", "United Kingdom"],
    ["Sarah Williams", "1988-11-05", "United Kingdom"],
    ["Michael Brown", "1991-04-18", "France"],
    ["Emily Davis", "1987-09-30", "France"],
    ["James Wilson", "1993-12-25", "Germany"],
    ["Jessica Martinez", "1989-06-14", "Germany"],
    ["Robert Taylor", "1990-08-20", "Canada"],
    ["Amanda Anderson", "1986-02-11", "Canada"],
    ["William Thomas", "1992-10-03", "Australia"],
    ["Olivia Jackson", "1988-05-28", "Australia"],
    ["Christopher White", "1991-01-09", "Italy"],
    ["Sophia Harris", "1987-07-16", "Italy"],
    ["Daniel Martin", "1993-03-04", "Spain"],
]

print("="*100)
print("TESTING SYNAPSE PROCESSING TIME")
print("="*100)
print()
print(f"Testing with {len(test_identities)} identities")
print(f"Each identity needs 15 variations")
print(f"Total addresses to generate: {len(test_identities)} × 15 = {len(test_identities) * 15}")
print()
print("⚠️  WARNING: With 1 request/second rate limit, this could take:")
print(f"   - Minimum: {len(test_identities) * 15} seconds = {len(test_identities) * 15 / 60:.1f} minutes")
print(f"   - Realistic: {len(test_identities) * 15 * 3} seconds = {len(test_identities) * 15 * 3 / 60:.1f} minutes")
print(f"   - Worst case: {len(test_identities) * 15 * 10} seconds = {len(test_identities) * 15 * 10 / 60:.1f} minutes")
print()
print("Starting test (this may take a while)...")
print()

start_time = time.time()

try:
    # Process with smaller variation count for testing
    variations = process_full_synapse(
        identity_list=test_identities[:3],  # Test with just 3 identities first
        variation_count=3,  # Just 3 variations per identity for testing
        use_perfect_addresses=True,
        verbose=True
    )
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print()
    print("="*100)
    print("TIMING RESULTS")
    print("="*100)
    print()
    print(f"Processed {len(test_identities[:3])} identities with {3} variations each")
    print(f"Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print(f"Time per identity: {elapsed/len(test_identities[:3]):.1f} seconds")
    print(f"Time per address: {elapsed/(len(test_identities[:3]) * 3):.1f} seconds")
    print()
    
    # Estimate for full synapse
    estimated_time = (elapsed / (len(test_identities[:3]) * 3)) * (len(test_identities) * 15)
    print(f"Estimated time for full synapse (15 names × 15 addresses):")
    print(f"  {estimated_time:.1f} seconds = {estimated_time/60:.1f} minutes = {estimated_time/3600:.1f} hours")
    print()
    
    if estimated_time > 300:  # 5 minutes
        print("⚠️  WARNING: This will take too long!")
        print("   Consider:")
        print("   1. Reducing variation count")
        print("   2. Using exploit addresses (faster but requires empty seed bug)")
        print("   3. Caching addresses")
        print("   4. Parallel processing (but Nominatim rate limit is 1 req/sec)")
    else:
        print("✅ Time is acceptable!")
    
    # Show results
    print()
    print("="*100)
    print("GENERATED VARIATIONS")
    print("="*100)
    for name, vars_list in variations.items():
        print(f"\n{name}: {len(vars_list)} variations")
        if vars_list:
            print(f"  Sample: {vars_list[0]}")
    
except KeyboardInterrupt:
    print("\n\n⚠️  Test interrupted by user")
    print("This confirms that address generation takes too long with rate limiting")
except Exception as e:
    print(f"\n\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

