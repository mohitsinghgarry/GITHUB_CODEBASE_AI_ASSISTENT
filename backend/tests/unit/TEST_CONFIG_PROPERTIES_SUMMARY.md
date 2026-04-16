# Configuration Property-Based Tests Summary

## Overview

This document summarizes the property-based tests implemented for configuration validation in `test_config_properties.py`.

## Test Framework

- **Framework**: Hypothesis 6.98.3
- **Test Runner**: pytest
- **Configuration**: 100 examples per property test, 60-second deadline
- **Total Tests**: 21 tests covering all aspects of Property 27

## Property 27: Configuration Validation

**Validates Requirements**: 13.1, 13.2, 13.3, 13.6, 13.8

### Property 27a: Valid Configurations Load Successfully

**Test**: `test_property_27a_valid_configurations_load_successfully`

**Description**: For any configuration with all required fields present and valid values within acceptable ranges, the Settings object SHALL be created successfully without raising ValidationError.

**Strategy**: Generates valid configurations with:
- Valid database URLs (postgresql+asyncpg://)
- Valid Redis URLs (redis://)
- Valid Ollama URLs (http:// or https://)
- Valid ranges for all numeric fields
- Valid enum values for log_level, environment, embedding_device
- Enforces invariants: chunk_overlap < chunk_size, chunk_size <= max_chunk_size, default_top_k <= max_top_k, max_response_tokens <= max_context_tokens

**Examples**: 100

### Property 27b: Invalid Field Types Rejected

**Test**: `test_property_27b_invalid_types_rejected`

**Description**: For any configuration field that expects an integer, providing a non-integer type SHALL raise ValidationError with a descriptive message.

**Strategy**: Tests fields (database_pool_size, redis_max_connections, ollama_timeout, chunk_size, embedding_dimension) with invalid types (None, lists, dicts, strings).

**Examples**: 50

### Property 27c: Out-of-Range Values Rejected

**Tests**:
- `test_property_27c_chunk_size_out_of_range_rejected`
- `test_property_27c_embedding_dimension_out_of_range_rejected`
- `test_property_27c_ollama_timeout_out_of_range_rejected`

**Description**: For any value outside the valid range, the configuration SHALL be rejected with ValidationError.

**Ranges Tested**:
- chunk_size: [128, 2048]
- embedding_dimension: [128, 1536]
- ollama_timeout: [10, 600]

**Examples**: 50 per test

### Property 27d: Missing Required Fields Rejected

**Test**: `test_property_27d_missing_required_fields_rejected`

**Description**: For any configuration missing a required field, the configuration SHALL be rejected with ValidationError indicating the missing field.

**Required Fields Tested**:
- database_url
- redis_url
- celery_broker_url
- celery_result_backend
- secret_key

**Examples**: 50

### Property 27e: Chunk Overlap < Chunk Size Invariant Enforced

**Test**: `test_property_27e_chunk_overlap_less_than_chunk_size_enforced`

**Description**: For any configuration where chunk_overlap >= chunk_size, the configuration SHALL be rejected with ValidationError.

**Strategy**: Generates chunk_size values and creates chunk_overlap = chunk_size + offset to violate the invariant.

**Examples**: 100

### Property 27f: Token Limit Invariants Enforced

**Test**: `test_property_27f_response_tokens_not_exceed_context_tokens`

**Description**: For any configuration where max_response_tokens > max_context_tokens, the configuration SHALL be rejected with ValidationError.

**Strategy**: Generates max_context_tokens and creates max_response_tokens = max_context_tokens + offset to violate the invariant.

**Examples**: 100

### Property 27g: Top-K Limit Invariants Enforced

**Test**: `test_property_27g_default_top_k_not_exceed_max_top_k`

**Description**: For any configuration where default_top_k > max_top_k, the configuration SHALL be rejected with ValidationError.

**Strategy**: Generates max_top_k and creates default_top_k = max_top_k + offset to violate the invariant.

**Examples**: 100

### Property 27h: URL Format Validation

**Tests**:
- `test_property_27h_database_url_format_validation`
- `test_property_27h_redis_url_format_validation`
- `test_property_27h_ollama_url_format_validation`

**Description**: For any URL that doesn't match the expected format, the configuration SHALL be rejected with ValidationError.

**Formats Validated**:
- database_url: Must start with "postgresql+asyncpg://"
- redis_url: Must start with "redis://"
- ollama_base_url: Must start with "http://" or "https://"

**Examples**: 50 per test

### Property 27i: Storage Paths Created If Not Exist

**Test**: `test_property_27i_storage_paths_created_if_not_exist`

**Description**: For any valid storage path configuration, if the path doesn't exist, it SHALL be created automatically during Settings initialization.

**Strategy**: Creates temporary directories with non-existent paths and verifies they are created during Settings initialization.

**Examples**: 50

## Additional Edge Case Tests

### Secret Key Validation
- `test_secret_key_minimum_length_enforced`: Verifies secret_key must be at least 32 characters

### Case-Insensitive Validation
- `test_log_level_case_insensitive`: Verifies log_level accepts any case and normalizes to uppercase
- `test_environment_case_insensitive`: Verifies environment accepts any case and normalizes to lowercase
- `test_embedding_device_case_insensitive`: Verifies embedding_device accepts any case and normalizes to lowercase

### Invalid Enum Values
- `test_invalid_log_level_rejected`: Verifies invalid log levels are rejected
- `test_invalid_environment_rejected`: Verifies invalid environments are rejected
- `test_invalid_embedding_device_rejected`: Verifies invalid embedding devices are rejected

### URL Normalization
- `test_ollama_url_trailing_slash_removed`: Verifies trailing slashes are removed from ollama_base_url

## Test Results

All 21 tests pass successfully:
- ✅ Property 27a: Valid configurations load successfully (100 examples)
- ✅ Property 27b: Invalid types rejected (50 examples)
- ✅ Property 27c: Out-of-range values rejected (150 examples across 3 tests)
- ✅ Property 27d: Missing required fields rejected (50 examples)
- ✅ Property 27e: Chunk overlap invariant enforced (100 examples)
- ✅ Property 27f: Token limit invariants enforced (100 examples)
- ✅ Property 27g: Top-K limit invariants enforced (100 examples)
- ✅ Property 27h: URL format validation (150 examples across 3 tests)
- ✅ Property 27i: Storage paths created (50 examples)
- ✅ 8 additional edge case tests

## Coverage

The property-based tests achieve 81% coverage of the `app/core/config.py` module, testing:
- All field validators
- All model validators
- URL format validation
- Range validation
- Type validation
- Invariant enforcement
- Path creation logic

## Requirements Validated

- ✅ **13.1**: Load configuration from environment variables and configuration files
- ✅ **13.2**: Support configuration for embedding model selection, chunk size, and overlap
- ✅ **13.3**: Support configuration for Ollama endpoint, model name, and timeout settings
- ✅ **13.6**: WHEN configuration is invalid or missing, THE RAG_System SHALL fail to start with descriptive error messages
- ✅ **13.8**: Validate configuration values against expected types and ranges
