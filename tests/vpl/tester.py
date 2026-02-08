"""
print as json back
+-----------------------+--------+
| Test                  | Result |
+-----------------------+--------+
| Parameters Validation | False  |
| Insert                |  True  |
| Leave Data            |  True  |
| Free data            |  True  |
| Remove                |  True  |
| Remove Non-Owned Node | False  |
| Forward Transitions  |  True  |
| Failure Transitions  |  True  |
| Pattern Matching      |  True  |
| Valgrind              | False  |
+-----------------------+--------+
+-----------------------+--------+
"""
import os

def test_vpl_tester():
    results = {
        "Parameters Validation": False,
        "Insert": True,
        "Leave Data": True,
        "Free data": True,
        "Remove": True,
        "Remove Non-Owned Node": False,
        "Forward Transitions": True,    
        "Failure Transitions": True,
        "Pattern Matching": True,
        "Valgrind": False
    }
    import json
    print(json.dumps(results))  

if __name__ == "__main__":
    test_vpl_tester()