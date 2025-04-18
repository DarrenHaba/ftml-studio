# src/ftml_studio/tests/test_json_converter.py
import pytest
import json
from src.ftml_studio.converters.json_converter import JSONConverter

def test_simple_object_conversion():
    """Test conversion of a simple JSON object to FTML"""
    json_data = '{"name": "John", "age": 30}'
    expected_ftml = 'name = "John"\nage = 30'

    converter = JSONConverter(reverse=True)
    result = converter.convert(json_data)

    assert result.strip() == expected_ftml.strip()

def test_special_character_conversion():
    """Test conversion of strings with special characters to FTML"""
    json_data = '{"message": "Hello \\"world\\"!\\nNew line"}'
    # Note the escaped \n in the expected output
    expected_ftml = 'message = "Hello \\"world\\"!\\nNew line"'

    converter = JSONConverter(reverse=True)
    result = converter.convert(json_data)

    assert result.strip() == expected_ftml.strip()
    
def test_nested_object_conversion():
    """Test conversion of a nested JSON object to FTML"""
    json_data = '{"person": {"name": "John", "age": 30}}'
    expected_ftml = 'person = {\n    name = "John",\n    age = 30\n}'

    converter = JSONConverter(reverse=True)
    result = converter.convert(json_data)

    assert result.strip() == expected_ftml.strip()

def test_array_conversion():
    """Test conversion of a JSON array to FTML"""
    json_data = '{"tags": ["red", "green", "blue"]}'
    expected_ftml = 'tags = ["red", "green", "blue"]'

    converter = JSONConverter(reverse=True)
    result = converter.convert(json_data)

    assert result.strip() == expected_ftml.strip()

def test_nested_array_conversion():
    """Test conversion of nested JSON arrays to FTML"""
    json_data = '{"matrix": [[1, 2], [3, 4]]}'
    expected_ftml = 'matrix = [\n    [1, 2],\n    [3, 4]\n]'

    converter = JSONConverter(reverse=True)
    result = converter.convert(json_data)

    assert result.strip() == expected_ftml.strip()

def test_boolean_value_conversion():
    """Test conversion of boolean values to FTML"""
    json_data = '{"active": true, "verified": false}'
    expected_ftml = 'active = true\nverified = false'

    converter = JSONConverter(reverse=True)
    result = converter.convert(json_data)

    assert result.strip() == expected_ftml.strip()

def test_null_value_conversion():
    """Test conversion of null values to FTML"""
    json_data = '{"data": null}'
    expected_ftml = 'data = null'

    converter = JSONConverter(reverse=True)
    result = converter.convert(json_data)

    assert result.strip() == expected_ftml.strip()

def test_special_character_conversion():
    """Test conversion of strings with special characters to FTML"""
    json_data = '{"message": "Hello \\"world\\"!\\nNew line"}'
    expected_ftml = 'message = "Hello \\"world\\"!\\nNew line"'

    converter = JSONConverter(reverse=True)
    result = converter.convert(json_data)

    assert result.strip() == expected_ftml.strip()

def test_empty_object_conversion():
    """Test conversion of empty objects to FTML"""
    json_data = '{"empty": {}}'
    expected_ftml = 'empty = {}'

    converter = JSONConverter(reverse=True)
    result = converter.convert(json_data)

    assert result.strip() == expected_ftml.strip()

def test_empty_array_conversion():
    """Test conversion of empty arrays to FTML"""
    json_data = '{"empty": []}'
    expected_ftml = 'empty = []'

    converter = JSONConverter(reverse=True)
    result = converter.convert(json_data)

    assert result.strip() == expected_ftml.strip()

def test_invalid_json_conversion():
    """Test that invalid JSON raises the appropriate error"""
    json_data = '{"invalid": true'  # Missing closing brace

    converter = JSONConverter(reverse=True)
    with pytest.raises(ValueError):
        converter.convert(json_data)

def test_complete_complex_structure():
    """Test conversion of a complex JSON structure with mixed types"""
    json_data = {
        "name": "John",
        "age": 30,
        "height": 5.9,
        "active": True,
        "lastLogin": None,
        "address": {
            "street": "123 Main St",
            "city": "Anytown"
        },
        "hobbies": ["reading", "coding"]
    }

    converter = JSONConverter(reverse=True)
    result = converter.convert(json.dumps(json_data))

    # Verify the result contains all expected values
    assert '"John"' in result
    assert '30' in result
    assert '5.9' in result
    assert 'true' in result
    assert 'null' in result
    assert '"123 Main St"' in result
    assert '"Anytown"' in result
    assert '"reading"' in result
    assert '"coding"' in result
