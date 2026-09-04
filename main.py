import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, StreamingResponse
import socket as sckt
import json

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
        async def err_gen():
            yield f"data: {json.dumps({'error': 'Could not determine local IP'})}\n\n"
        return StreamingResponse(err_gen(), media_type="text/event-stream")
    
    parts = local_ip.split('.')
    subnet = f"{parts[0]}.{parts[1]}.{parts[2]}"
    
    ips_to_scan = [f"{subnet}.{i}" for i in range(1, 255)]
    
    async def event_generator():
        found_devices = []
        chunk_size = 50
        total_ips = len(ips_to_scan)
        
        for i in range(0, total_ips, chunk_size):
            chunk = ips_to_scan[i:i + chunk_size]
            tasks = [check_port(ip, 502, timeout=2.5) for ip in chunk]
            results = await asyncio.gather(*tasks)
            found_devices.extend([ip for ip, is_open in results if is_open])
            
            # Calcula progresso e envia para o frontend
            progress = min(100, int(((i + chunk_size) / total_ips) * 100))
            yield f"data: {json.dumps({'progress': progress, 'devices_so_far': found_devices})}\n\n"
            
        # Evento final
        yield f"data: {json.dumps({'done': True, 'devices': found_devices, 'local_ip': local_ip, 'subnet': f'{subnet}.0/24'})}\n\n"
        
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")
