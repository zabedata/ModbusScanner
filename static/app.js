document.addEventListener('DOMContentLoaded', () => {
    const scanBtn = document.getElementById('scanBtn');
    const scannerVisuals = document.getElementById('scannerVisuals');
    const resultsContainer = document.getElementById('resultsContainer');
    const deviceList = document.getElementById('deviceList');
    const infoBar = document.getElementById('infoBar');

    scanBtn.addEventListener('click', () => {
        // UI State: Scanning
        scanBtn.disabled = true;
        scanBtn.querySelector('.text').textContent = 'Varrendo...';
        scannerVisuals.style.display = 'flex';
        resultsContainer.style.display = 'none';
        deviceList.innerHTML = '';
        
        const progressBar = document.getElementById('progressBar');
        const statusText = document.getElementById('statusText');
        progressBar.style.width = '0%';
        
        const eventSource = new EventSource('/api/scan');
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.error) {
                alert(data.error);
                eventSource.close();
                resetUI();
                return;
            }
            
            if (data.done) {
                eventSource.close();
                progressBar.style.width = '100%';
                
                // UI State: Results
                setTimeout(() => {
                    scannerVisuals.style.display = 'none';
                    resultsContainer.style.display = 'block';
                    
                    infoBar.textContent = `Escaneado ${data.subnet} a partir de ${data.local_ip}`;
                    
                    if (data.devices.length === 0) {
                        deviceList.innerHTML = '<li class="no-devices">Nenhum dispositivo encontrado na porta 502.</li>';
                    } else {
                        data.devices.forEach(ip => {
                            const li = document.createElement('li');
                            li.className = 'device-item';
                            li.innerHTML = `
                                <span class="device-ip">${ip}</span>
                                <span class="device-status">Modbus TCP Ativo (502)</span>
                            `;
                            deviceList.appendChild(li);
                        });
                    }
                    resetUI();
                }, 500);
            } else {
                progressBar.style.width = `${data.progress}%`;
                statusText.textContent = `Progresso: ${data.progress}% (${data.devices_so_far.length} encontrados...)`;
            }
        };
        
        eventSource.onerror = (error) => {
            console.error('SSE Error:', error);
            eventSource.close();
            alert('Erro de conexão durante o scan.');
            resetUI();
        };
        
        function resetUI() {
            scanBtn.disabled = false;
            scanBtn.querySelector('.text').textContent = 'Buscar Novamente';
        }
    });
});
