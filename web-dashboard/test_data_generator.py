#!/usr/bin/env python3
"""
Test Data Generator for Exercise Monitoring Vest Dashboard
Simulates Arduino serial output for testing without hardware
"""

import json
import time
import random
import math
from datetime import datetime

def generate_realistic_data(elapsed_seconds):
    """
    Generate realistic vital signs data based on simulated exercise activity
    
    Activity phases:
    0-60s: Rest (baseline)
    60-180s: Warm-up (gradual increase)
    180-300s: Exercise (high intensity)
    300-420s: Cool-down (gradual decrease)
    420s+: Rest (return to baseline)
    """
    
    # Base values
    base_hr = 70
    base_rr = 14
    base_sweat = 0
    
    # Calculate activity level (0-1)
    if elapsed_seconds < 60:
        # Rest
        activity = 0.0
    elif elapsed_seconds < 180:
        # Warm-up: gradual increase
        activity = (elapsed_seconds - 60) / 120  # 0 to 1 over 120 seconds
    elif elapsed_seconds < 300:
        # Exercise: maintain high
        activity = 0.9 + (random.random() * 0.2)  # 0.9 to 1.1
    elif elapsed_seconds < 420:
        # Cool-down: gradual decrease
        activity = 1.0 - ((elapsed_seconds - 300) / 120)  # 1 to 0 over 120 seconds
    else:
        # Rest: back to baseline
        activity = 0.1 + (random.random() * 0.1)  # 0.1 to 0.2
    
    # Generate heart rate (50-180 BPM range)
    hr_range = 110  # 180 - 70
    hr = int(base_hr + (hr_range * activity))
    
    # Add realistic variation (±3 BPM)
    hr += random.randint(-3, 3)
    
    # Add breathing pattern (slight sinusoidal variation)
    breath_phase = math.sin(elapsed_seconds * 0.1) * 2
    hr += int(breath_phase)
    
    # Clamp to realistic range
    hr = max(50, min(180, hr))
    
    # Generate breathing rate (10-35 BPM range)
    rr_range = 25  # 35 - 10
    rr = int(base_rr + (rr_range * activity))
    
    # Add realistic variation (±2 BPM)
    rr += random.randint(-2, 2)
    
    # Clamp to realistic range
    rr = max(10, min(35, rr))
    
    # Generate sweat level (0-3)
    # Sweat lags behind HR increase (slower response)
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
    
    # Random lead-off events (1% chance)
    lead_off = random.random() < 0.01
    
    return {
        'hr': hr,
        'rr': rr,
        'sweat': sweat,
        'leadOff': lead_off
    }


def simulate_exercise_session(duration_seconds=600, update_rate=1.0):
    """
    Simulate a complete exercise session
    
    Args:
        duration_seconds: Total duration of simulation (default: 10 minutes)
        update_rate: Updates per second (default: 1.0 = 1 Hz)
    """
    print("=" * 60)
    print("Exercise Monitoring Vest - Test Data Generator")
    print("=" * 60)
    print(f"Duration: {duration_seconds}s ({duration_seconds/60:.1f} minutes)")
    print(f"Update Rate: {update_rate} Hz")
    print("\nActivity Schedule:")
    print("  0-60s:    Rest (baseline)")
    print("  60-180s:  Warm-up (gradual increase)")
    print("  180-300s: Exercise (high intensity)")
    print("  300-420s: Cool-down (gradual decrease)")
    print("  420s+:    Rest (recovery)")
    print("=" * 60)
    print("\nGenerating data... (Press Ctrl+C to stop)\n")
    
    start_time = time.time()
    update_interval = 1.0 / update_rate
    
    try:
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > duration_seconds:
                print(f"\n✅ Session complete ({duration_seconds}s)")
                break
            
            # Generate data
            data = generate_realistic_data(int(elapsed))
            
            # Format as JSON (matching Arduino output)
            json_output = json.dumps(data)
            print(json_output)
            
            # Show progress every 30 seconds
            if int(elapsed) % 30 == 0 and int(elapsed) > 0:
                phase = get_activity_phase(int(elapsed))
                print(f"# Progress: {int(elapsed)}s / {duration_seconds}s - Phase: {phase}")
            
            # Wait for next update
            time.sleep(update_interval)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopped at {int(elapsed)}s")


def get_activity_phase(seconds):
    """Get current activity phase description"""
    if seconds < 60:
        return "REST"
    elif seconds < 180:
        return "WARM-UP"
    elif seconds < 300:
        return "EXERCISE"
    elif seconds < 420:
        return "COOL-DOWN"
    else:
        return "RECOVERY"


def stress_test(duration=60):
    """
    Generate high-frequency test data for stress testing
    
    Args:
        duration: Duration in seconds
    """
    print("🔥 Stress Test Mode - High Frequency Data")
    print(f"Duration: {duration}s")
    print(f"Rate: ~10 Hz")
    print()
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            elapsed = int(time.time() - start_time)
            data = generate_realistic_data(elapsed)
            print(json.dumps(data))
            time.sleep(0.1)  # 10 Hz
    except KeyboardInterrupt:
        print("\n🛑 Stress test stopped")


def demo_mode():
    """
    Demo mode: Show all scenarios in quick succession
    """
    print("🎬 Demo Mode - Quick Activity Transitions")
    print()
    
    scenarios = [
        (0, "REST - Baseline", 10),
        (120, "WARM-UP - Increasing", 10),
        (240, "EXERCISE - High Intensity", 15),
        (360, "COOL-DOWN - Decreasing", 10),
        (480, "RECOVERY - Return to Baseline", 10)
    ]
    
    try:
        for start_time, description, duration in scenarios:
            print(f"\n📍 Scenario: {description} ({duration}s)")
            for i in range(duration):
                elapsed = start_time + (i * 6)  # Accelerate time
                data = generate_realistic_data(elapsed)
                print(json.dumps(data))
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("EXERCISE MONITORING VEST - TEST DATA GENERATOR")
    print("="*60)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "stress":
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            stress_test(duration)
        
        elif mode == "demo":
            demo_mode()
        
        elif mode == "help":
            print("""
Usage:
    python test_data_generator.py [mode] [options]

Modes:
    (none)      Normal mode - 10 minute simulated exercise session
    stress      High-frequency data generation for testing
                  python test_data_generator.py stress [duration]
                  Example: python test_data_generator.py stress 120
    
    demo        Quick demo showing all activity phases
                  python test_data_generator.py demo
    
    help        Show this help message

Normal Mode Output:
    Simulates realistic exercise session with:
    - Rest phase (0-60s)
    - Warm-up (60-180s)
    - Exercise (180-300s)
    - Cool-down (300-420s)
    - Recovery (420s+)

Tip:
    Pipe output to serial_bridge.py for testing:
    python test_data_generator.py | python serial_bridge.py
    
    Or copy output and paste into Arduino Serial Monitor
            """)
            sys.exit(0)
        
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Run with 'help' for usage information")
            sys.exit(1)
    
    else:
        # Normal mode - 10 minute session at 1 Hz
        simulate_exercise_session(duration_seconds=600, update_rate=1.0)
    
    print("\n✅ Test data generation complete")
