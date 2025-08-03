/**
 * Network Simulation Components for SKJ Simulator Pro
 * Interactive network topology with device management and packet visualization
 */

class NetworkDevice {
    constructor(id, type, x, y, config = {}) {
        this.id = id;
        this.type = type; // 'router', 'switch', 'firewall', 'server', 'workstation'
        this.x = x;
        this.y = y;
        this.config = {
            name: config.name || `${type}_${id}`,
            ip: config.ip || this.generateIP(),
            ports: config.ports || this.getDefaultPorts(),
            status: config.status || 'active',
            ...config
        };
        this.connections = [];
        this.selected = false;
        this.dragging = false;
    }

    generateIP() {
        const types = {
            'router': '192.168.1.1',
            'switch': '192.168.1.2', 
            'firewall': '192.168.1.3',
            'server': '192.168.1.10',
            'workstation': `192.168.1.${20 + Math.floor(Math.random() * 80)}`
        };
        return types[this.type] || '192.168.1.100';
    }

    getDefaultPorts() {
        const portConfigs = {
            'router': { ethernet: 4, serial: 2 },
            'switch': { ethernet: 24 },
            'firewall': { ethernet: 3, management: 1 },
            'server': { ethernet: 1 },
            'workstation': { ethernet: 1 }
        };
        return portConfigs[this.type] || { ethernet: 1 };
    }

    draw(ctx) {
        const size = 40;
        const halfSize = size / 2;
        
        // Device background
        ctx.fillStyle = this.selected ? '#00e5a8' : '#0f1b2d';
        ctx.strokeStyle = this.selected ? '#00b38f' : '#1e2a40';
        ctx.lineWidth = 2;
        
        // Draw device shape based on type
        ctx.beginPath();
        switch (this.type) {
            case 'router':
                this.drawRouter(ctx, halfSize);
                break;
            case 'switch':
                this.drawSwitch(ctx, halfSize);
                break;
            case 'firewall':
                this.drawFirewall(ctx, halfSize);
                break;
            case 'server':
                this.drawServer(ctx, halfSize);
                break;
            case 'workstation':
                this.drawWorkstation(ctx, halfSize);
                break;
        }
        ctx.fill();
        ctx.stroke();

        // Device label
        ctx.fillStyle = '#e8f0ff';
        ctx.font = '12px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(this.config.name, this.x, this.y + halfSize + 15);
        
        // Status indicator
        ctx.fillStyle = this.config.status === 'active' ? '#23d18b' : '#ff5c7a';
        ctx.beginPath();
        ctx.arc(this.x + halfSize - 5, this.y - halfSize + 5, 4, 0, Math.PI * 2);
        ctx.fill();
    }

    drawRouter(ctx, halfSize) {
        ctx.roundRect(this.x - halfSize, this.y - halfSize, halfSize * 2, halfSize * 2, 8);
        // Router icon - antenna lines
        ctx.strokeStyle = '#00e5a8';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(this.x - 10, this.y - 5);
        ctx.lineTo(this.x + 10, this.y - 5);
        ctx.moveTo(this.x - 5, this.y);
        ctx.lineTo(this.x + 5, this.y);
        ctx.stroke();
    }

    drawSwitch(ctx, halfSize) {
        ctx.rect(this.x - halfSize, this.y - halfSize, halfSize * 2, halfSize * 2);
        // Switch icon - grid pattern
        ctx.strokeStyle = '#00e5a8';
        ctx.lineWidth = 1;
        for (let i = -10; i <= 10; i += 10) {
            ctx.beginPath();
            ctx.moveTo(this.x + i, this.y - 10);
            ctx.lineTo(this.x + i, this.y + 10);
            ctx.stroke();
        }
    }

    drawFirewall(ctx, halfSize) {
        ctx.roundRect(this.x - halfSize, this.y - halfSize, halfSize * 2, halfSize * 2, 4);
        // Firewall icon - shield
        ctx.fillStyle = '#ff9800';
        ctx.beginPath();
        ctx.moveTo(this.x, this.y - 10);
        ctx.lineTo(this.x - 8, this.y);
        ctx.lineTo(this.x, this.y + 10);
        ctx.lineTo(this.x + 8, this.y);
        ctx.closePath();
        ctx.fill();
    }

    drawServer(ctx, halfSize) {
        ctx.rect(this.x - halfSize, this.y - halfSize, halfSize * 2, halfSize * 2);
        // Server icon - stacked rectangles
        ctx.fillStyle = '#2196f3';
        for (let i = 0; i < 3; i++) {
            ctx.fillRect(this.x - 12, this.y - 8 + i * 6, 24, 4);
        }
    }

    drawWorkstation(ctx, halfSize) {
        ctx.roundRect(this.x - halfSize, this.y - halfSize, halfSize * 2, halfSize * 2, 12);
        // Workstation icon - monitor
        ctx.fillStyle = '#9c27b0';
        ctx.fillRect(this.x - 8, this.y - 6, 16, 10);
        ctx.fillRect(this.x - 2, this.y + 4, 4, 6);
    }

    containsPoint(x, y) {
        const size = 40;
        return x >= this.x - size/2 && x <= this.x + size/2 && 
               y >= this.y - size/2 && y <= this.y + size/2;
    }

    moveTo(x, y) {
        this.x = x;
        this.y = y;
    }
}

class NetworkConnection {
    constructor(device1, device2, type = 'ethernet') {
        this.device1 = device1;
        this.device2 = device2;
        this.type = type; // 'ethernet', 'serial', 'wireless'
        this.status = 'active';
        this.packets = [];
        this.selected = false;
    }

    draw(ctx) {
        ctx.strokeStyle = this.selected ? '#00e5a8' : 
                         this.status === 'active' ? '#1e2a40' : '#ff5c7a';
        ctx.lineWidth = this.selected ? 3 : 2;
        
        // Draw connection line
        ctx.beginPath();
        ctx.moveTo(this.device1.x, this.device1.y);
        ctx.lineTo(this.device2.x, this.device2.y);
        ctx.stroke();

        // Draw connection type indicator
        const midX = (this.device1.x + this.device2.x) / 2;
        const midY = (this.device1.y + this.device2.y) / 2;
        
        ctx.fillStyle = '#ffb020';
        ctx.font = '10px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(this.type, midX, midY - 5);

        // Draw packets
        this.packets.forEach(packet => packet.draw(ctx));
    }

    addPacket(packet) {
        this.packets.push(packet);
    }

    updatePackets() {
        this.packets = this.packets.filter(packet => {
            packet.update();
            return !packet.isComplete();
        });
    }
}

class NetworkPacket {
    constructor(connection, direction = 1) {
        this.connection = connection;
        this.direction = direction; // 1 for device1->device2, -1 for reverse
        this.progress = 0;
        this.speed = 0.02;
        this.size = 6;
        this.color = '#23d18b';
        this.protocol = 'TCP';
    }

    update() {
        this.progress += this.speed;
    }

    isComplete() {
        return this.progress >= 1;
    }

    draw(ctx) {
        const startDevice = this.direction > 0 ? this.connection.device1 : this.connection.device2;
        const endDevice = this.direction > 0 ? this.connection.device2 : this.connection.device1;
        
        const x = startDevice.x + (endDevice.x - startDevice.x) * this.progress;
        const y = startDevice.y + (endDevice.y - startDevice.y) * this.progress;

        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(x, y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

class NetworkTopology {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.devices = new Map();
        this.connections = [];
        this.selectedDevice = null;
        this.selectedConnection = null;
        this.dragging = false;
        this.dragOffset = { x: 0, y: 0 };
        this.mode = 'select'; // 'select', 'add_device', 'add_connection'
        this.deviceToAdd = 'router';
        
        this.setupEventListeners();
        this.animationId = null;
        this.startAnimation();
    }

    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    }

    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    handleMouseDown(e) {
        const pos = this.getMousePos(e);
        
        if (this.mode === 'add_device') {
            this.addDevice(this.deviceToAdd, pos.x, pos.y);
            return;
        }

        // Check if clicking on a device
        for (const device of this.devices.values()) {
            if (device.containsPoint(pos.x, pos.y)) {
                if (this.mode === 'add_connection' && this.selectedDevice) {
                    // Create connection between selected device and clicked device
                    if (this.selectedDevice !== device) {
                        this.addConnection(this.selectedDevice, device);
                        this.selectedDevice.selected = false;
                        this.selectedDevice = null;
                        this.mode = 'select';
                    }
                } else {
                    // Select device for dragging
                    this.selectDevice(device);
                    this.dragging = true;
                    this.dragOffset = {
                        x: pos.x - device.x,
                        y: pos.y - device.y
                    };
                }
                return;
            }
        }

        // Deselect if clicking on empty space
        this.deselectAll();
    }

    handleMouseMove(e) {
        const pos = this.getMousePos(e);
        
        if (this.dragging && this.selectedDevice) {
            this.selectedDevice.moveTo(
                pos.x - this.dragOffset.x,
                pos.y - this.dragOffset.y
            );
        }
    }

    handleMouseUp(e) {
        this.dragging = false;
    }

    selectDevice(device) {
        this.deselectAll();
        device.selected = true;
        this.selectedDevice = device;
    }

    deselectAll() {
        this.devices.forEach(device => device.selected = false);
        this.connections.forEach(conn => conn.selected = false);
        this.selectedDevice = null;
        this.selectedConnection = null;
    }

    addDevice(type, x, y, config = {}) {
        const id = `${type}_${Date.now()}`;
        const device = new NetworkDevice(id, type, x, y, config);
        this.devices.set(id, device);
        return device;
    }

    removeDevice(deviceId) {
        // Remove all connections to this device
        this.connections = this.connections.filter(conn => 
            conn.device1.id !== deviceId && conn.device2.id !== deviceId
        );
        this.devices.delete(deviceId);
    }

    addConnection(device1, device2, type = 'ethernet') {
        // Check if connection already exists
        const exists = this.connections.some(conn => 
            (conn.device1 === device1 && conn.device2 === device2) ||
            (conn.device1 === device2 && conn.device2 === device1)
        );
        
        if (!exists) {
            const connection = new NetworkConnection(device1, device2, type);
            this.connections.push(connection);
            return connection;
        }
        return null;
    }

    removeConnection(connection) {
        const index = this.connections.indexOf(connection);
        if (index > -1) {
            this.connections.splice(index, 1);
        }
    }

    sendPacket(fromDeviceId, toDeviceId, protocol = 'TCP') {
        const fromDevice = this.devices.get(fromDeviceId);
        const toDevice = this.devices.get(toDeviceId);
        
        if (!fromDevice || !toDevice) return;

        // Find connection between devices
        const connection = this.connections.find(conn => 
            (conn.device1 === fromDevice && conn.device2 === toDevice) ||
            (conn.device1 === toDevice && conn.device2 === fromDevice)
        );

        if (connection) {
            const direction = connection.device1 === fromDevice ? 1 : -1;
            const packet = new NetworkPacket(connection, direction);
            packet.protocol = protocol;
            connection.addPacket(packet);
        }
    }

    setMode(mode, deviceType = 'router') {
        this.mode = mode;
        this.deviceToAdd = deviceType;
        this.deselectAll();
    }

    clear() {
        this.devices.clear();
        this.connections = [];
        this.deselectAll();
    }

    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#07111f';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid
        this.drawGrid();

        // Draw connections first (behind devices)
        this.connections.forEach(connection => {
            connection.draw(this.ctx);
            connection.updatePackets();
        });

        // Draw devices
        this.devices.forEach(device => device.draw(this.ctx));

        // Draw mode indicator
        this.drawModeIndicator();
    }

    drawGrid() {
        const gridSize = 20;
        this.ctx.strokeStyle = '#0e1420';
        this.ctx.lineWidth = 1;

        for (let x = 0; x < this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        for (let y = 0; y < this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    drawModeIndicator() {
        this.ctx.fillStyle = '#0f1b2d';
        this.ctx.fillRect(10, 10, 200, 30);
        this.ctx.strokeStyle = '#1e2a40';
        this.ctx.strokeRect(10, 10, 200, 30);

        this.ctx.fillStyle = '#e8f0ff';
        this.ctx.font = '12px Inter';
        this.ctx.textAlign = 'left';
        
        let modeText = '';
        switch (this.mode) {
            case 'select':
                modeText = 'Mode: Select/Move';
                break;
            case 'add_device':
                modeText = `Mode: Add ${this.deviceToAdd}`;
                break;
            case 'add_connection':
                modeText = 'Mode: Add Connection';
                break;
        }
        
        this.ctx.fillText(modeText, 15, 28);
    }

    startAnimation() {
        const animate = () => {
            this.draw();
            this.animationId = requestAnimationFrame(animate);
        };
        animate();
    }

    stopAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    exportTopology() {
        const topology = {
            devices: Array.from(this.devices.values()).map(device => ({
                id: device.id,
                type: device.type,
                x: device.x,
                y: device.y,
                config: device.config
            })),
            connections: this.connections.map(conn => ({
                device1: conn.device1.id,
                device2: conn.device2.id,
                type: conn.type,
                status: conn.status
            }))
        };
        return topology;
    }

    importTopology(topology) {
        this.clear();
        
        // Import devices
        topology.devices.forEach(deviceData => {
            const device = this.addDevice(
                deviceData.type, 
                deviceData.x, 
                deviceData.y, 
                deviceData.config
            );
            device.id = deviceData.id;
            this.devices.set(deviceData.id, device);
        });

        // Import connections
        topology.connections.forEach(connData => {
            const device1 = this.devices.get(connData.device1);
            const device2 = this.devices.get(connData.device2);
            if (device1 && device2) {
                const connection = this.addConnection(device1, device2, connData.type);
                if (connection) {
                    connection.status = connData.status;
                }
            }
        });
    }
}

// Add roundRect method to CanvasRenderingContext2D if not available
if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function(x, y, width, height, radius) {
        this.beginPath();
        this.moveTo(x + radius, y);
        this.lineTo(x + width - radius, y);
        this.quadraticCurveTo(x + width, y, x + width, y + radius);
        this.lineTo(x + width, y + height - radius);
        this.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
        this.lineTo(x + radius, y + height);
        this.quadraticCurveTo(x, y + height, x, y + height - radius);
        this.lineTo(x, y + radius);
        this.quadraticCurveTo(x, y, x + radius, y);
        this.closePath();
    };
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NetworkTopology, NetworkDevice, NetworkConnection, NetworkPacket };
}