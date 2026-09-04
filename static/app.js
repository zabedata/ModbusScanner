document.addEventListener('DOMContentLoaded', () => {
    const scanBtn = document.getElementById('scanBtn');
    const scannerVisuals = document.getElementById('scannerVisuals');
    const resultsContainer = document.getElementById('resultsContainer');
    const deviceList = document.getElementById('deviceList');
    const infoBar = document.getElementById('infoBar');

    scanBtn.addEventListener('click', async () => {
        // UI State: Scanning
        scanBtn.disabled = true;
        scanBtn.querySelector('.text').textContent = 'Varrendo...';
        scannerVisuals.style.display = 'flex';
        resultsContainer.style.display = 'none';
        deviceList.innerHTML = '';

        try {
            const response = await fetch('/api/scan');
            if (!response.ok) throw new Error('Falha na resposta da rede');
            
            const data = await response.json();
            
            // UI State: Results
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
        } catch (error) {
            console.error('Erro durante o scan:', error);
            alert('Ocorreu um erro ao escanear a rede. Verifique a conexao e o backend.');
            scannerVisuals.style.display = 'none';
        } finally {
            // UI State: Reset Button
            scanBtn.disabled = false;
            scanBtn.querySelector('.text').textContent = 'Buscar Novamente';
        }
    });
});
