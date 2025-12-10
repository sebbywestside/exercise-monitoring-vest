#!/usr/bin/env python3
"""
Mock Data Server for Exercise Monitoring Vest Dashboard
Generates realistic test data without Arduino hardware
Compatible with websockets 15.x
"""

import asyncio
import websockets
import json
import random
import math
from datetime import datetime

# Server configuration
WS_HOST = 'localhost'
WS_PORT = 8765

# Global set of connected clients
clients = set()

# Simulation state
simulation_time = 0
session_start = datetime.now()


def generate_realistic_vitals(elapsed_seconds):
    """
    Generate realistic vital signs based on simulated activity level
    
    Activity phases:
    - 0-60s: Rest (baseline)
    - 60-180s: Warm-up (gradual increase)
    - 180-300s: Exercise (high intensity)
    - 300-420s: Cool-down (gradual decrease)
    - 420s+: Recovery (return to baseline)
    """
    
    # Calculate activity level (0.0 to 1.0)
    if elapsed_seconds < 60:
        # Rest phase
        activity = 0.0
        phase = "REST"
    elif elapsed_seconds < 180:
        # Warm-up: gradual increase over 2 minutes
        activity = (elapsed_seconds - 60) / 120
        phase = "WARM-UP"
    elif elapsed_seconds < 300:
        # Exercise: maintain high intensity with variation
        activity = 0.9 + (random.random() * 0.2)
        phase = "EXERCISE"
    elif elapsed_seconds < 420:
        # Cool-down: gradual decrease over 2 minutes
        activity = 1.0 - ((elapsed_seconds - 300) / 120)
        phase = "COOL-DOWN"
    else:
        # Recovery: low activity with small variation
        activity = 0.1 + (random.random() * 0.1)
        phase = "RECOVERY"
    
    # Generate Heart Rate (50-180 BPM)
    base_hr = 70
    hr_range = 110
    hr = int(base_hr + (hr_range * activity))
    
    # Add realistic variation
    hr += random.randint(-3, 3)
    
    # Add breathing-synchronized variation
    breath_sync = math.sin(elapsed_seconds * 0.1) * 2
    hr += int(breath_sync)
    
    # Clamp to realistic range
    hr = max(50, min(180, hr))
    
    # Generate Breathing Rate (10-35 BPM)
    base_rr = 14
    rr_range = 21
    rr = int(base_rr + (rr_range * activity))
    
    # Add variation
    rr += random.randint(-2, 2)
    
    # Clamp to realistic range
    rr = max(10, min(35, rr))
    
    # Generate Sweat Level (0-3)
    # Sweat lags behind heart rate increase
    if elapsed_seconds < 90:
        sweat = 0
    elif elapsed_seconds < 200:
        sweat = 1
    elif elapsed_seconds < 280:
        sweat = 2
    elif elapsed_seconds < 400:
        sweat = 3
    elif elapsed_seconds < 500:
        sweat = 2
    else:
        sweat = 1
    
    # Occasional lead-off events (1% chance)
    lead_off = random.random() < 0.01
    
    return {
        'hr': hr,
        'rr': rr,
        'sweat': sweat,
        'leadOff': lead_off,
        'timestamp': elapsed_seconds,
        'phase': phase
    }


async def handle_client(websocket):
    """Handle new WebSocket client connection (websockets 15.x compatible)"""
    clients.add(websocket)
    client_id = id(websocket)
    print(f"✅ Client {client_id} connected (Total: {len(clients)})")
    
    try:
        # Send initial connection confirmation
        welcome_msg = {
            'type': 'connection',
            'message': 'Connected to Mock Data Server',
            'serverTime': datetime.now().isoformat()
        }
        await websocket.send(json.dumps(welcome_msg))
        
        # Keep connection open
        async for message in websocket:
            # Handle any messages from client (optional)
            try:
                data = json.loads(message)
                if data.get('type') == 'command':
                    print(f"📨 Received command from client: {data.get('command')}")
            except json.JSONDecodeError:
                pass
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)
        print(f"❌ Client {client_id} disconnected (Total: {len(clients)})")


async def broadcast_data():
    """Generate and broadcast mock data to all clients"""
    global simulation_time
    
    print("🎬 Starting data generation...")
    print("📊 Simulating realistic exercise session...")
    print()
    
    update_count = 0
    
    while True:
        try:
            # Generate vital signs data
            data = generate_realistic_vitals(simulation_time)
            
            # Add server timestamp
            data['serverTime'] = datetime.now().isoformat()
            
            # Broadcast to all connected clients
            if clients:
                message = json.dumps(data)
                
                # Send to all clients concurrently
                await asyncio.gather(
                    *[client.send(message) for client in clients],
                    return_exceptions=True
                )
                
                update_count += 1
                
                # Log every 10 updates
                if update_count % 10 == 0:
                    print(f"📡 Update #{update_count}: "
                          f"Phase={data['phase']:<10} "
                          f"HR={data['hr']:3}bpm "
                          f"RR={data['rr']:2}bpm "
                          f"Sweat={data['sweat']} "
                          f"({len(clients)} clients)")
            
            # Increment simulation time
            simulation_time += 1
            
            # Reset after 10 minutes (600 seconds) to loop
            if simulation_time >= 600:
                simulation_time = 0
                print("\n🔄 Restarting simulation cycle...\n")
            
            # Wait 1 second between updates
            await asyncio.sleep(1.0)
            
        except Exception as e:
            print(f"⚠️  Error in broadcast: {e}")
            await asyncio.sleep(1.0)


async def main():
    """Main entry point - start WebSocket server and data generation"""
    print("=" * 70)
    print("🏃 Exercise Monitoring Vest - Mock Data Server")
    print("=" * 70)
    print(f"WebSocket Server: ws://{WS_HOST}:{WS_PORT}")
    print(f"Status: Generating realistic test data")
    print(f"Mode: Continuous simulation (10-minute loop)")
    print(f"Websockets Version: {websockets.__version__}")
    print("=" * 70)
    print()
    print("💡 How to use:")
    print("   1. Keep this server running")
    print("   2. Open dashboard.html in your browser")
    print("   3. Dashboard will connect automatically")
    print()
    print("🎬 Activity Simulation:")
    print("   0:00-1:00   → REST (baseline)")
    print("   1:00-3:00   → WARM-UP (increasing)")
    print("   3:00-5:00   → EXERCISE (high intensity)")
    print("   5:00-7:00   → COOL-DOWN (decreasing)")
    print("   7:00-10:00  → RECOVERY (baseline)")
    print("   [Loop repeats]")
    print()
    print("=" * 70)
    print("✅ Server starting...")
    print()
    
    # Start WebSocket server (websockets 15.x style)
    async with websockets.serve(handle_client, WS_HOST, WS_PORT):
        print(f"✅ WebSocket server ready on ws://{WS_HOST}:{WS_PORT}")
        print(f"⏳ Waiting for dashboard connections...")
        print()
        
        # Start data generation
        await broadcast_data()


if __name__ == "__main__":
    try:
        # Check if websockets is installed
        import websockets
        print(f"\n✅ Using websockets version {websockets.__version__}")
    except ImportError:
        print("❌ Missing required package: websockets")
        print("\nInstall it with:")
        print("   pip install websockets")
        print("\nOr install all requirements:")
        print("   pip install -r requirements.txt")
        exit(1)
    
    # Run the server
    try:
        print("\n🚀 Starting Mock Data Server...\n")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        exit(1)