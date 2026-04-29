import pytest
from agent.calculator_tool import calculator


def test_addition():
    assert calculator("2 + 3") == "5"

def test_subtraction():
    assert calculator("10 - 4") == "6"

def test_multiplication():
    assert calculator("3 * 7") == "21"

def test_division():
    assert calculator("10 / 4") == "2.5"
    

def test_power():
    assert calculator("2 ** 8") == "256"

def test_modulo():
    assert calculator("17 % 5") == "2"

def test_floor_division():
    assert calculator("17 // 5") == "3"

def test_negative():
    assert calculator("-5 + 3") == "-2"

def test_complex_expression():
    assert calculator("(2 + 3) * 4") == "20"

def test_division_by_zero():
    result = calculator("1 / 0")
    assert "zero" in result.lower()

def test_code_injection_blocked():
    result = calculator("__import__('os').system('echo hacked')")
    assert "Error" in result

def test_string_injection_blocked():
    result = calculator("'hello'")
    assert "Error" in result

def test_empty_expression():
    result = calculator("")
    assert "Error" in result
