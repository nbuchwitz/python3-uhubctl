# Python wrapper for uhubctl

This is a simple Python wrapper for [uhubctl](https://github.com/mvp/uhubctl)

# Examples

## Discover all usable USB hubs

```python
import uhubctl

hubs = uhubctl.discover_hubs()

for hub in hubs:
    print(f"Found hub: {hub}")

    for port in hub.ports:
        print(f"   Found port: {port}")
```

## Manually specify hub and port

```python
from uhubctl import Hub, Port

hub = Hub("1-1")
hub.add_port(1)
```

## Control ports

```python
from uhubctl import Hub, Port

hub = Hub("1-1")
port = hub.add_port(1)

print("Switch port 1-1.1 off")
port.status = False

print("Switch port 1-1.1 on")
port.status = True

print("Get port 1-1.1 status")
print(port.status)
```