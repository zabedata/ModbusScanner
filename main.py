import asyncio
import socket
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import socket as sckt

app = FastAPI(title="Modbus Scanner")

def get_local_ip():
    s = sckt.socket(sckt.AF_INET, sckt.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

async def check_port(ip: str, port: int, timeout: float = 0.5):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return ip, True
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return ip, False

@app.get("/api/scan")
async def scan_network():
    local_ip = get_local_ip()
    if local_ip == '127.0.0.1':
        return {"devices": [], "message": "Could not determine local IP"}
    
    parts = local_ip.split('.')
    subnet = f"{parts[0]}.{parts[1]}.{parts[2]}"
    
    ips_to_scan = [f"{subnet}.{i}" for i in range(1, 255)]
    found_devices = []
    
    # Busca em lotes de 50 para evitar congestionamento de conexões simultâneas no roteador/CLP
    chunk_size = 50
    for i in range(0, len(ips_to_scan), chunk_size):
        chunk = ips_to_scan[i:i + chunk_size]
        tasks = [check_port(ip, 502, timeout=2.5) for ip in chunk]
        results = await asyncio.gather(*tasks)
        found_devices.extend([ip for ip, is_open in results if is_open])
        
    return {"devices": found_devices, "local_ip": local_ip, "subnet": f"{subnet}.0/24"}

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")
