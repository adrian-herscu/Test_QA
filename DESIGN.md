# Design Decisions - Ammeter Testing Framework

## Architecture Overview

The framework follows a modular architecture separating concerns into distinct components:

### Module Structure
```
src/
├── testing/          # Core testing functionality
│   ├── test_framework.py    # Orchestration layer
│   ├── data_collector.py    # Socket communication & sampling
│   ├── result_analyzer.py   # Statistical analysis
│   └── visualizer.py         # Plot generation
└── utils/           # Cross-cutting concerns
    ├── config.py            # YAML configuration loader
    └── logger.py            # Structured logging
```

**Rationale**: This separation allows each component to be tested, modified, and reused independently. The testing modules can work with any socket-based measurement device, not just ammeters.

## Key Design Decisions

### 1. Socket-Based Communication
**Decision**: Use raw TCP sockets instead of higher-level protocols.

**Rationale**: 
- Matches the existing ammeter emulator infrastructure
- Minimal overhead for embedded systems context
- Direct control over timing and connection lifecycle
- No external dependencies required

**Trade-off**: Manual connection management and error handling required.

### 2. Threading for Data Collection
**Decision**: Use threading (not asyncio) for concurrent measurement collection.

**Rationale**:
- Socket I/O is blocking - threading provides natural isolation
- Simple mental model: one thread per test run
- Queue-based communication between threads is straightforward
- Compatible with existing synchronous codebase

**Trade-off**: Threading has higher overhead than async, but irrelevant for our scale (10 Hz sampling).

### 3. Configuration-Driven Testing
**Decision**: YAML configuration file instead of command-line arguments.

**Rationale**:
- Repeatable test configurations
- Version-controllable test scenarios
- Easy to document and share
- Supports complex nested parameters

**Trade-off**: Requires YAML parsing library (PyYAML).

### 4. Statistical Analysis with SciPy
**Decision**: Use SciPy for confidence intervals and normality tests.

**Rationale**:
- Industry-standard statistical library
- Provides robust implementations (t-distribution, Shapiro-Wilk)
- Better than reimplementing statistical formulas
- Well-documented and maintained

**Trade-off**: External dependency, but justified by correctness guarantees.

### 5. Result Archiving with UUID
**Decision**: Use UUID4 for unique test identification.

**Rationale**:
- Guaranteed uniqueness without coordination
- Works in distributed/concurrent scenarios
- Timestamp alone insufficient (multiple tests per second)
- Enables easy cross-referencing between JSON and plots

**Trade-off**: Less human-readable than sequential IDs, but provides stronger guarantees.

### 6. JSON Result Format
**Decision**: Store results as JSON (not CSV or binary).

**Rationale**:
- Human-readable for debugging
- Supports nested structures (metadata + measurements + statistics)
- Easy to parse in any language
- No schema migration needed for adding fields

**Trade-off**: Larger file size than binary, but negligible for our data volumes.

## Error Handling Strategy

### Validation Before Execution
**Decision**: Validate ammeter type and configuration synchronously before spawning threads.

**Rationale**: Prevents cryptic thread errors and provides immediate feedback on configuration issues.

### Timeout-Based Socket Operations
**Decision**: Set socket timeout to 2 seconds for all operations.

**Rationale**: Prevents indefinite blocking on unresponsive devices while allowing sufficient time for response.

### SO_REUSEADDR Socket Option
**Decision**: Enable SO_REUSEADDR on all server sockets.

**Rationale**: Allows rapid restart during development without waiting for TIME_WAIT state to clear.

## Limitations and Future Improvements

### Current Limitations
1. **Single Measurement Type**: Framework assumes current measurements only
2. **No Retry Logic**: Single failed measurement causes data loss
3. **Memory-Based Storage**: All measurements held in memory before archiving
4. **No Real-Time Monitoring**: Results only available after test completion

### Potential Improvements
1. Support multiple measurement types (voltage, power, etc.)
2. Implement exponential backoff retry for failed measurements
3. Streaming results to disk for long-duration tests
4. WebSocket interface for real-time monitoring
5. Database backend for historical trend analysis

## Testing Approach

### Unit Tests
Tests validate individual components in isolation:
- Configuration loading and validation
- Statistical calculations
- Data collection timing accuracy
- Result archiving and retrieval

### Integration Testing
The `examples/run_tests.py` script serves as both example and integration test, validating the complete workflow from emulator start to result archiving.

## Dependencies Rationale

All dependencies pinned to exact versions for reproducibility:

- **numpy 2.4.1**: Required for Python 3.13 compatibility (older versions depend on removed distutils)
- **scipy 1.17.0**: Latest version compatible with numpy 2.4.1
- **matplotlib 3.10.8**: Stable release with Python 3.13 support
- **seaborn 0.13.2**: Statistical visualization wrapper around matplotlib
- **pyyaml 6.0.3**: YAML parsing for configuration
- **pandas 3.0.0**: Data manipulation for statistical operations

## Conclusion

The framework prioritizes **simplicity**, **modularity**, and **correctness** over performance optimization. Design choices favor maintainability and clarity appropriate for a testing framework where reliability matters more than throughput.
