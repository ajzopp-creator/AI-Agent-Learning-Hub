import json
from pathlib import Path
from datetime import datetime

result = {
    "test": "works",
    "timestamp": datetime.now().isoformat()
}

out_file = Path(__file__).parent.parent / "outputs" / "test_simple.json"
with open(out_file, 'w') as f:
    json.dump(result, f)

print("Created test file")
