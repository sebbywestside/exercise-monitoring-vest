#!/usr/bin/env python3
"""
Serial to WebSocket Bridge for Exercise Monitoring Vest
Reads JSON data from Arduino serial port and broadcasts to WebSocket clients
"""

import serial
import json
import asyncio
import websockets
import sys
from datetime import datetime

# Configuration
SERIAL_PORT = '/dev/cu.usbserial-14310'  # Mac/Linux - Change to your port
# SERIAL_PORT = 'COM3'  # Windows - Change to your port
BAUD_RATE = 115200
WS_HOST = 'localhost'
WS_PORT = 8765

# Global set of connected WebSocket clients
clients = set()


async def handle_client(websocket, path):
    """Handle new WebSocket client connection"""
    clients.add(websocket)
    print(f"New client connected. Total clients: {len(clients)}")
    
    try:
        # Keep connection open and wait for messages (we don't expect any)
        async for message in websocket:
            # Echo back if needed for debugging
            pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)
        print(f"Client disconnected. Total clients: {len(clients)}")


async def broadcast_data():
    """Read from serial port and broadcast to all WebSocket clients"""
    try:
        # Open serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✅ Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud")
        print(f"Waiting for data...")
        
        line_count = 0
        
        while True:
            try:
                # Read line from serial
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if not line:
                        await asyncio.sleep(0.01)
                        continue
                    
                    line_count += 1
                    
                    # Try to parse as JSON
                    if line.startswith('{'):
                        try:
                            data = json.loads(line)
                            
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
                                
                                # Log every 10th message to avoid spam
                                if line_count % 10 == 0:
                                    print(f"📊 Broadcast #{line_count}: HR={data.get('hr', 'N/A')} "
                                          f"RR={data.get('rr', 'N/A')} Sweat={data.get('sweat', 'N/A')} "
                                          f"({len(clients)} clients)")
                            
                        except json.JSONDecodeError as e:
                            if line_count % 20 == 0:  # Only show occasional errors
                                print(f"⚠️  Invalid JSON: {line[:50]}... Error: {e}")
                    
                    else:
                        # Non-JSON line (probably debug output)
                        if line_count % 20 == 0:
                            print(f"📝 Debug: {line[:80]}")
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.01)
                
            except serial.SerialException as e:
                print(f"❌ Serial error: {e}")
                print("Attempting to reconnect in 5 seconds...")
                await asyncio.sleep(5)
                try:
                    ser.close()
                    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                    print("✅ Reconnected to serial port")
                except Exception as reconnect_error:
                    print(f"❌ Reconnection failed: {reconnect_error}")
            
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                await asyncio.sleep(1)
    
    except serial.SerialException as e:
        print(f"\n❌ Could not open serial port {SERIAL_PORT}")
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check that Arduino is connected via USB")
        print("2. Verify the correct port in the script:")
        print("   - Mac/Linux: /dev/cu.usbserial-XXXX or /dev/ttyUSB0")
        print("   - Windows: COM3, COM4, etc.")
        print("3. Ensure no other programs (Arduino IDE, Serial Monitor) are using the port")
        print("\nTo list available ports, run:")
        print("   python -m serial.tools.list_ports")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        ser.close()
        sys.exit(0)


async def main():
    """Main entry point - start WebSocket server and data broadcaster"""
    print("=" * 60)
    print("Exercise Monitoring Vest - Serial to WebSocket Bridge")
    print("=" * 60)
    print(f"WebSocket Server: ws://{WS_HOST}:{WS_PORT}")
    print(f"Serial Port: {SERIAL_PORT} @ {BAUD_RATE} baud")
    print("=" * 60)
    print()
    
    # Start WebSocket server
    server = await websockets.serve(handle_client, WS_HOST, WS_PORT)
    print(f"✅ WebSocket server started on ws://{WS_HOST}:{WS_PORT}")
    print("✅ Waiting for web dashboard connections...")
    print()
    
    # Start broadcasting serial data
    await broadcast_data()


if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import serial
        import websockets
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("\nPlease install required packages:")
        print("   pip install pyserial websockets")
        print("\nOr install all requirements:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
