# Getting Started with SMCU

## Option A — With Allpath Runner (recommended)

```bash
# 1. Clone
git clone https://github.com/Tryboy869/smcu-protocol
cd smcu-protocol

# 2. Start daemon
python allpath-runner.py daemon &

# 3. Test: generate an ID
python main.py generate_id "développement logiciel" "erreur"

# 4. Test: validate an example entry
python main.py validate_entry "$(cat examples/software-dev.json)"

# 5. Test: compute a confidence score
python main.py compute_confidence 3 3 100
```

## Option B — Direct Python (no daemon)

```bash
python main.py validate_entry '{"id": "TEST-01", ...}'
python main.py compute_confidence 2 3 50
python main.py generate_id "médecine" "regle"
```

## Option C — From Any Language via Socket

```python
# Python consumer
import socket, json

def call_smcu(function, *args):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect('/tmp/allpath_runner.sock')
    req = json.dumps({"package": "smcu-protocol", "function": function, "args": list(args)})
    s.sendall(req.encode())
    result = json.loads(s.recv(8192).decode())
    s.close()
    return result

# Usage
result = call_smcu("compute_confidence", "3", "3", "100")
print(result)  # { "score": 66.1, ... }
```

```javascript
// JavaScript consumer
const net = require('net');

function callSmcu(fn, ...args) {
  return new Promise((resolve, reject) => {
    const client = net.createConnection('/tmp/allpath_runner.sock', () => {
      client.write(JSON.stringify({ package: 'smcu-protocol', function: fn, args }));
    });
    client.on('data', d => { resolve(JSON.parse(d.toString())); client.end(); });
    client.on('error', reject);
  });
}

// Usage
const result = await callSmcu('compute_confidence', '3', '3', '100');
console.log(result);
```

## Next Steps

- Read [AGENT_GUIDE.md](../AGENT_GUIDE.md) to understand the full workflow
- See [examples/](../examples/) for real entries
- Read [docs/confidence-score.md](confidence-score.md) to understand scoring
- Read [docs/anonymity-system.md](anonymity-system.md) to use anonymous contributions
