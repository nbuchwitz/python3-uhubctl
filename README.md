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

## Create hub and enumerate attached ports
```python
import uhubctl

hub = Hub("1-1", enumerate_ports=True)

# Iterate all ports
for port in hub.ports:
    print(f"Found port: {port}")

# Get port by port number
port_2 = hub.find_port(2)
print(f"The status of port 2 is {port_2.status}")
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

## Device details

```python
import uhubctl

hubs = uhubctl.discover_hubs()

for hub in hubs:
    print(f"Found hub: {hub}")

    for port in hub.ports:
        print(f"   Found port: {port}")
        
        # You can use the optional argument `cached_results=False` for each of 
        # these 3 methods in order to invalidate the internal cache,
        # which is used for performance reasons
        print(f"      Description: {port.description()}")
        print(f"      Vendor ID: {port.vendor_id()}")
        print(f"      Product ID: {port.product_id()}")
```

# FAQ

### How can I specify the path to ´uhubctl´

```python
import uhubctl

uhubctl.utils.UHUBCTL_BINARY = "sudo /usr/local/bin/uhubctl"
```
