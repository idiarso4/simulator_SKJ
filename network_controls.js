/**
 * Network Simulation Controls and Device Configuration
 */

class NetworkControls {
    constructor(topology, containerId) {
        this.topology = topology;
        this.container = document.getElementById(containerId);
        this.selectedDevice = null;
        this.init();
    }

    init() {
        this.createControlPanel();
        this.createDevicePanel();
        this.createMonitoringPanel();
        this.setupEventListeners();
    }

    createControlPanel() {
        const controlPanel = document.createElement('div');
        controlPanel.className = 'network-control-panel';
        controlPanel.innerHTML = `
            <div class="control-section">
                <h3>Network Tools</h3>
                <div class="tool-buttons">
                    <button id="selectMode" class="tool-btn active">Select</button>
                    <button id="connectionMode" class="tool-btn">Connect</button>
                    <button id="clearAll" class="tool-btn danger">Clear</button>
                </div>
            </div>
            
            <div class="control-section">
                <h3>Add Devices</h3>
                <div class="device-buttons">
                    <button class="device-btn" data-device="router">
                        <span class="device-icon">🔀</span>
                        Router
                    </button>
                    <button class="device-btn" data-device="switch">
                        <span class="device-icon">🔗</span>
                        Switch
                    </button>
                    <button class="device-btn" data-device="firewall">
                        <span class="device-icon">🛡️</span>
                        Firewall
                    </button>
                    <button class="device-btn" data-device="server">
                        <span class="device-icon">🖥️</span>
                        Server
                    </button>
                    <button class="device-btn" data-device="workstation">
                        <span class="device-icon">💻</span>
                        PC
                    </button>
                </div>
            </div>

            <div class="control-section">
                <h3>Simulation</h3>
                <div class="simulation-controls">
                    <button id="startSim" class="sim-btn">Start Simulation</button>
                    <button id="stopSim" class="sim-btn">Stop Simulation</button>
                    <button id="sendPacket" class="sim-btn">Send Packet</button>
                </div>
                <div class="packet-controls">
                    <select id="packetProtocol">
                        <option value="TCP">TCP</option>
                        <option value="UDP">UDP</option>
                        <option value="ICMP">ICMP</option>
                        <option value="HTTP">HTTP</option>
                    </select>
                    <input type="text" id="packetSource" placeholder="Source Device ID">
                    <input type="text" id="packetDest" placeholder="Dest Device ID">
                </div>
            </div>

            <div class="control-section">
                <h3>Import/Export</h3>
                <div class="file-controls">
                    <button id="exportTopology" class="file-btn">Export</button>
                    <button id="importTopology" class="file-btn">Import</button>
                    <input type="file" id="fileInput" accept=".json" style="display: none;">
                </div>
            </div>
        `;

        this.container.appendChild(controlPanel);
    }

    createDevicePanel() {
        const devicePanel = document.createElement('div');
        devicePanel.className = 'device-config-panel';
        devicePanel.innerHTML = `
            <div class="panel-header">
                <h3>Device Configuration</h3>
                <button id="closeDevicePanel" class="close-btn">×</button>
            </div>
            <div id="deviceConfigContent" class="panel-content">
                <p>Select a device to configure</p>
            </div>
        `;

        this.container.appendChild(devicePanel);
        this.devicePanel = devicePanel;
        this.hideDevicePanel();
    }

    createMonitoringPanel() {
        const monitorPanel = document.createElement('div');
        monitorPanel.className = 'network-monitor-panel';
        monitorPanel.innerHTML = `
            <div class="panel-header">
                <h3>Network Monitor</h3>
                <button id="toggleMonitor" class="toggle-btn">Hide</button>
            </div>
            <div class="monitor-content">
                <div class="monitor-section">
                    <h4>Traffic Statistics</h4>
                    <div id="trafficStats" class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">Packets Sent:</span>
                            <span id="packetsSent" class="stat-value">0</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Active Connections:</span>
                            <span id="activeConnections" class="stat-value">0</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Devices Online:</span>
                            <span id="devicesOnline" class="stat-value">0</span>
                        </div>
                    </div>
                </div>
                
                <div class="monitor-section">
                    <h4>Network Events</h4>
                    <div id="networkEvents" class="events-log"></div>
                </div>
            </div>
        `;

        this.container.appendChild(monitorPanel);
        this.monitorPanel = monitorPanel;
    }

    setupEventListeners() {
        // Tool mode buttons
        document.getElementById('selectMode').addEventListener('click', () => {
            this.setActiveMode('select');
            this.topology.setMode('select');
        });

        document.getElementById('connectionMode').addEventListener('click', () => {
            this.setActiveMode('connection');
            this.topology.setMode('add_connection');
        });

        document.getElementById('clearAll').addEventListener('click', () => {
            if (confirm('Clear all devices and connections?')) {
                this.topology.clear();
                this.hideDevicePanel();
                this.logEvent('Topology cleared');
            }
        });

        // Device buttons
        document.querySelectorAll('.device-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const deviceType = btn.dataset.device;
                this.setActiveDevice(btn);
                this.topology.setMode('add_device', deviceType);
            });
        });

        // Simulation controls
        document.getElementById('startSim').addEventListener('click', () => {
            this.startSimulation();
        });

        document.getElementById('stopSim').addEventListener('click', () => {
            this.stopSimulation();
        });

        document.getElementById('sendPacket').addEventListener('click', () => {
            this.sendTestPacket();
        });

        // File operations
        document.getElementById('exportTopology').addEventListener('click', () => {
            this.exportTopology();
        });

        document.getElementById('importTopology').addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });

        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.importTopology(e.target.files[0]);
        });

        // Device panel
        document.getElementById('closeDevicePanel').addEventListener('click', () => {
            this.hideDevicePanel();
        });

        // Monitor panel
        document.getElementById('toggleMonitor').addEventListener('click', () => {
            this.toggleMonitorPanel();
        });

        // Listen for device selection changes
        this.topology.canvas.addEventListener('click', () => {
            setTimeout(() => {
                if (this.topology.selectedDevice) {
                    this.showDeviceConfig(this.topology.selectedDevice);
                } else {
                    this.hideDevicePanel();
                }
            }, 100);
        });
    }

    setActiveMode(mode) {
        document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(mode + 'Mode').classList.add('active');

        document.querySelectorAll('.device-btn').forEach(btn => btn.classList.remove('active'));
    }

    setActiveDevice(deviceBtn) {
        document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.device-btn').forEach(btn => btn.classList.remove('active'));
        deviceBtn.classList.add('active');
    }

    showDeviceConfig(device) {
        this.selectedDevice = device;
        const content = document.getElementById('deviceConfigContent');

        content.innerHTML = `
            <div class="config-form">
                <div class="form-group">
                    <label>Device Name:</label>
                    <input type="text" id="deviceName" value="${device.config.name}">
                </div>
                
                <div class="form-group">
                    <label>IP Address:</label>
                    <input type="text" id="deviceIP" value="${device.config.ip}">
                </div>
                
                <div class="form-group">
                    <label>Status:</label>
                    <select id="deviceStatus">
                        <option value="active" ${device.config.status === 'active' ? 'selected' : ''}>Active</option>
                        <option value="inactive" ${device.config.status === 'inactive' ? 'selected' : ''}>Inactive</option>
                        <option value="error" ${device.config.status === 'error' ? 'selected' : ''}>Error</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Ports:</label>
                    <div id="portConfig"></div>
                </div>
                
                <div class="form-actions">
                    <button id="saveDeviceConfig" class="save-btn">Save</button>
                    <button id="deleteDevice" class="delete-btn">Delete</button>
                </div>
            </div>
        `;

        this.renderPortConfig(device);
        this.showDevicePanel();
        this.setupDeviceConfigListeners();
    }

    renderPortConfig(device) {
        const portContainer = document.getElementById('portConfig');
        let portHTML = '';

        Object.entries(device.config.ports).forEach(([portType, count]) => {
            portHTML += `
                <div class="port-config">
                    <span>${portType}:</span>
                    <input type="number" min="1" max="48" value="${count}" data-port="${portType}">
                </div>
            `;
        });

        portContainer.innerHTML = portHTML;
    }

    setupDeviceConfigListeners() {
        document.getElementById('saveDeviceConfig').addEventListener('click', () => {
            this.saveDeviceConfig();
        });

        document.getElementById('deleteDevice').addEventListener('click', () => {
            if (confirm('Delete this device and all its connections?')) {
                this.topology.removeDevice(this.selectedDevice.id);
                this.hideDevicePanel();
                this.logEvent(`Device ${this.selectedDevice.config.name} deleted`);
            }
        });
    }

    saveDeviceConfig() {
        if (!this.selectedDevice) return;

        const name = document.getElementById('deviceName').value;
        const ip = document.getElementById('deviceIP').value;
        const status = document.getElementById('deviceStatus').value;

        // Update device config
        this.selectedDevice.config.name = name;
        this.selectedDevice.config.ip = ip;
        this.selectedDevice.config.status = status;

        // Update ports
        document.querySelectorAll('#portConfig input').forEach(input => {
            const portType = input.dataset.port;
            const count = parseInt(input.value);
            this.selectedDevice.config.ports[portType] = count;
        });

        this.logEvent(`Device ${name} configuration updated`);
        this.hideDevicePanel();
    }

    showDevicePanel() {
        this.devicePanel.style.display = 'block';
    }

    hideDevicePanel() {
        this.devicePanel.style.display = 'none';
        this.selectedDevice = null;
    }

    toggleMonitorPanel() {
        const btn = document.getElementById('toggleMonitor');
        const content = this.monitorPanel.querySelector('.monitor-content');

        if (content.style.display === 'none') {
            content.style.display = 'block';
            btn.textContent = 'Hide';
        } else {
            content.style.display = 'none';
            btn.textContent = 'Show';
        }
    }

    startSimulation() {
        this.simulationRunning = true;
        this.logEvent('Network simulation started');

        // Start periodic packet sending for demonstration
        this.simulationInterval = setInterval(() => {
            this.sendRandomPackets();
            this.updateStatistics();
        }, 2000);
    }

    stopSimulation() {
        this.simulationRunning = false;
        if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
        }
        this.logEvent('Network simulation stopped');
    }

    sendTestPacket() {
        const protocol = document.getElementById('packetProtocol').value;
        const source = document.getElementById('packetSource').value;
        const dest = document.getElementById('packetDest').value;

        if (source && dest) {
            this.topology.sendPacket(source, dest, protocol);
            this.logEvent(`${protocol} packet sent from ${source} to ${dest}`);
            this.packetsSent = (this.packetsSent || 0) + 1;
        } else {
            alert('Please specify source and destination device IDs');
        }
    }

    sendRandomPackets() {
        const devices = Array.from(this.topology.devices.values());
        if (devices.length < 2) return;

        // Send a few random packets
        for (let i = 0; i < Math.random() * 3 + 1; i++) {
            const source = devices[Math.floor(Math.random() * devices.length)];
            const dest = devices[Math.floor(Math.random() * devices.length)];

            if (source !== dest) {
                const protocols = ['TCP', 'UDP', 'ICMP', 'HTTP'];
                const protocol = protocols[Math.floor(Math.random() * protocols.length)];
                this.topology.sendPacket(source.id, dest.id, protocol);
                this.packetsSent = (this.packetsSent || 0) + 1;
            }
        }
    }

    updateStatistics() {
        const devices = Array.from(this.topology.devices.values());
        const activeDevices = devices.filter(d => d.config.status === 'active').length;
        const connections = this.topology.connections.length;

        document.getElementById('packetsSent').textContent = this.packetsSent || 0;
        document.getElementById('activeConnections').textContent = connections;
        document.getElementById('devicesOnline').textContent = activeDevices;
    }

    logEvent(message) {
        const eventsLog = document.getElementById('networkEvents');
        const timestamp = new Date().toLocaleTimeString();
        const eventElement = document.createElement('div');
        eventElement.className = 'event-item';
        eventElement.innerHTML = `<span class="event-time">${timestamp}</span> ${message}`;

        eventsLog.insertBefore(eventElement, eventsLog.firstChild);

        // Keep only last 10 events
        while (eventsLog.children.length > 10) {
            eventsLog.removeChild(eventsLog.lastChild);
        }
    }

    exportTopology() {
        const topology = this.topology.exportTopology();
        const dataStr = JSON.stringify(topology, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });

        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'network_topology.json';
        link.click();

        this.logEvent('Topology exported');
    }

    importTopology(file) {
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const topology = JSON.parse(e.target.result);
                this.topology.importTopology(topology);
                this.logEvent('Topology imported');
                this.hideDevicePanel();
            } catch (error) {
                alert('Error importing topology: ' + error.message);
            }
        };
        reader.readAsText(file);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NetworkControls };
}