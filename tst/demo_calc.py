#!/usr/bin/env python3
"""
Demo Calculator Test
"""

print("Starting calculator demo...")

class Calculator:
    def add(self, a, b):
        result = a + b
        print(f"Adding {a} + {b} = {result}")
        return result
    
    def multiply(self, a, b):
        result = a * b
        print(f"Multiplying {a} * {b} = {result}")
        return result

# Create calculator and run some calculations
calc = Calculator()
print("\nPerforming calculations:")
calc.add(5, 3)
calc.multiply(4, 7)
calc.add(10, 20)
calc.multiply(3, 6)

print("\nDemo completed!")