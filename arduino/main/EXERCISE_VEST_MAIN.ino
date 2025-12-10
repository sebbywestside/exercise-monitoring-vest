// ========================================
// EXERCISE_VEST_MAIN.ino
// Complete integration of ECG, Respiratory, GSR
// ========================================

#include <LiquidCrystal.h>
#include <SD.h>
#include <SPI.h>

// ============ PIN DEFINITIONS ============
// ECG (AD8232)
const int ECG_OUTPUT = A0;
const int ECG_LO_PLUS = A1;
const int ECG_LO_MINUS = A2;

// Respiratory Band
const int RESP_SENSOR = A4;

// GSR Sensor
const int GSR_SENSOR = A3;

// SD Card
const int SD_CS = 10;

// LCD (4-bit mode)
LiquidCrystal lcd(2, 3, 4, 5, 6, 7);

// User Interface
const int BUTTON_MODE = 8;
const int BUTTON_ADJUST = 9;

// ============ TIMING CONFIGURATION ============
unsigned long lastECGSample = 0;
unsigned long lastRespSample = 0;
unsigned long lastGSRSample = 0;
unsigned long lastLCDUpdate = 0;
unsigned long lastDataLog = 0;
unsigned long sessionStartTime = 0;

const int ECG_SAMPLE_INTERVAL = 3;      // 333 Hz (1000/3)
const int RESP_SAMPLE_INTERVAL = 50;    // 20 Hz
const int GSR_SAMPLE_INTERVAL = 200;    // 5 Hz
const int LCD_UPDATE_INTERVAL = 1000;   // 1 Hz
const int DATA_LOG_INTERVAL = 1000;     // 1 Hz summary

// ============ ECG PROCESSING ============
struct ECGProcessor {
  // R-peak detection
  const int BUFFER_SIZE = 100;
  int ecgBuffer[100];
  int bufferIndex = 0;
  
  // Heart rate calculation
  unsigned long lastPeakTime = 0;
  int rrIntervals[10];
  int rrIndex = 0;
  int currentHeartRate = 0;
  
  // Thresholds
  int peakThreshold = 600;  // Adjust based on calibration
  int signalMin = 1023;
  int signalMax = 0;
  bool leadOff = false;
  
  // Peak detection state
  bool inPeak = false;
  int peakValue = 0;
  
  void processECGSample(int rawValue) {
    // Check lead-off
    if (digitalRead(ECG_LO_PLUS) == 1 || digitalRead(ECG_LO_MINUS) == 1) {
      leadOff = true;
      currentHeartRate = 0;
      return;
    }
    leadOff = false;
    
    // Update buffer
    ecgBuffer[bufferIndex] = rawValue;
    bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;
    
    // Adaptive baseline tracking
    if (rawValue < signalMin) signalMin = rawValue;
    if (rawValue > signalMax) signalMax = rawValue;
    
    // Recalculate threshold every 100 samples
    if (bufferIndex == 0) {
      int range = signalMax - signalMin;
      peakThreshold = signalMin + (range * 0.6);
      
      // Reset min/max with some hysteresis
      signalMin = signalMax - (range * 0.8);
      signalMax = signalMin + (range * 0.8);
    }
    
    // R-peak detection
    if (rawValue > peakThreshold && !inPeak) {
      // Rising edge - start of peak
      inPeak = true;
      peakValue = rawValue;
    } else if (inPeak) {
      if (rawValue > peakValue) {
        // Still rising
        peakValue = rawValue;
      } else if (rawValue < peakThreshold) {
        // Falling edge - peak complete
        inPeak = false;
        
        // Calculate RR interval
        unsigned long now = millis();
        if (lastPeakTime > 0) {
          int rrInterval = now - lastPeakTime;
          
          // Physiologically valid (30-200 bpm)
          if (rrInterval > 300 && rrInterval < 2000) {
            rrIntervals[rrIndex] = rrInterval;
            rrIndex = (rrIndex + 1) % 10;
            
            // Calculate average heart rate
            int sum = 0;
            int count = 0;
            for (int i = 0; i < 10; i++) {
              if (rrIntervals[i] > 0) {
                sum += rrIntervals[i];
                count++;
              }
            }
            if (count > 0) {
              int avgRR = sum / count;
              currentHeartRate = 60000 / avgRR;
            }
          }
        }
        lastPeakTime = now;
      }
    }
  }
  
  int getHeartRate() { return leadOff ? 0 : currentHeartRate; }
  bool isLeadOff() { return leadOff; }
  int getRawValue() { return ecgBuffer[(bufferIndex + BUFFER_SIZE - 1) % BUFFER_SIZE]; }
};

// ============ RESPIRATORY PROCESSING ============
struct RespiratoryProcessor {
  // Breathing detection
  const int BUFFER_SIZE = 60;
  int respBuffer[60];
  int bufferIndex = 0;
  
  // Breath detection
  enum BreathState { INHALE, EXHALE, HOLD };
  BreathState currentState = HOLD;
  BreathState lastState = HOLD;
  
  unsigned long lastBreathTime = 0;
  int breathIntervals[10];
  int breathIndex = 0;
  int currentBreathRate = 0;
  
  // Adaptive thresholds
  int baseline = 512;
  int inhaleThreshold = 530;
  int exhaleThreshold = 494;
  
  void processRespSample(int rawValue) {
    // Update buffer
    respBuffer[bufferIndex] = rawValue;
    bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;
    
    // Update baseline every 60 samples (3 seconds at 20Hz)
    if (bufferIndex == 0) {
      long sum = 0;
      for (int i = 0; i < BUFFER_SIZE; i++) {
        sum += respBuffer[i];
      }
      baseline = sum / BUFFER_SIZE;
      
      // Calculate standard deviation for threshold
      long variance = 0;
      for (int i = 0; i < BUFFER_SIZE; i++) {
        int diff = respBuffer[i] - baseline;
        variance += diff * diff;
      }
      int stdDev = sqrt(variance / BUFFER_SIZE);
      
      inhaleThreshold = baseline + (stdDev * 0.5);
      exhaleThreshold = baseline - (stdDev * 0.5);
    }
    
    // State machine for breath detection
    lastState = currentState;
    
    if (rawValue > inhaleThreshold) {
      currentState = INHALE;
    } else if (rawValue < exhaleThreshold) {
      currentState = EXHALE;
    } else {
      currentState = HOLD;
    }
    
    // Detect breath cycle completion (exhale to inhale transition)
    if (currentState == INHALE && lastState == EXHALE) {
      unsigned long now = millis();
      if (lastBreathTime > 0) {
        int breathInterval = now - lastBreathTime;
        
        // Physiologically valid (6-40 breaths per minute)
        if (breathInterval > 1500 && breathInterval < 10000) {
          breathIntervals[breathIndex] = breathInterval;
          breathIndex = (breathIndex + 1) % 10;
          
          // Calculate average breath rate
          int sum = 0;
          int count = 0;
          for (int i = 0; i < 10; i++) {
            if (breathIntervals[i] > 0) {
              sum += breathIntervals[i];
              count++;
            }
          }
          if (count > 0) {
            int avgBreath = sum / count;
            currentBreathRate = 60000 / avgBreath;
          }
        }
      }
      lastBreathTime = now;
    }
  }
  
  int getBreathRate() { return currentBreathRate; }
  int getRawValue() { return respBuffer[(bufferIndex + BUFFER_SIZE - 1) % BUFFER_SIZE]; }
  String getStateString() {
    switch(currentState) {
      case INHALE: return "INH";
      case EXHALE: return "EXH";
      default: return "HLD";
    }
  }
};

// ============ GSR PROCESSING ============
struct GSRProcessor {
  // Smoothing and trend detection
  const int BUFFER_SIZE = 30;
  int gsrBuffer[30];
  int bufferIndex = 0;
  
  int baseline = 0;
  int smoothedValue = 0;
  int sweatLevel = 0;  // 0=dry, 1=low, 2=medium, 3=high
  
  // Calibration
  bool calibrated = false;
  int calibrationSamples = 0;
  const int CALIBRATION_TIME = 50;  // 10 seconds at 5Hz
  
  void processGSRSample(int rawValue) {
    // Update buffer
    gsrBuffer[bufferIndex] = rawValue;
    bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;
    
    // Calculate moving average
    long sum = 0;
    for (int i = 0; i < BUFFER_SIZE; i++) {
      sum += gsrBuffer[i];
    }
    smoothedValue = sum / BUFFER_SIZE;
    
    // Calibration phase
    if (!calibrated) {
      calibrationSamples++;
      if (calibrationSamples >= CALIBRATION_TIME) {
        baseline = smoothedValue;
        calibrated = true;
      }
      return;
    }
    
    // Calculate sweat level relative to baseline
    int delta = smoothedValue - baseline;
    
    if (delta < 10) {
      sweatLevel = 0;  // Dry
    } else if (delta < 30) {
      sweatLevel = 1;  // Low
    } else if (delta < 60) {
      sweatLevel = 2;  // Medium
    } else {
      sweatLevel = 3;  // High
    }
    
    // Slowly adapt baseline (very slow drift correction)
    if (millis() % 60000 == 0) {  // Every minute
      baseline = (baseline * 99 + smoothedValue) / 100;
    }
  }
  
  int getSweatLevel() { return sweatLevel; }
  int getRawValue() { return gsrBuffer[(bufferIndex + BUFFER_SIZE - 1) % BUFFER_SIZE]; }
  int getSmoothedValue() { return smoothedValue; }
  String getSweatString() {
    switch(sweatLevel) {
      case 0: return "DRY ";
      case 1: return "LOW ";
      case 2: return "MED ";
      case 3: return "HIGH";
      default: return "ERR ";
    }
  }
};

// ============ GLOBAL INSTANCES ============
ECGProcessor ecgProc;
RespiratoryProcessor respProc;
GSRProcessor gsrProc;

File dataFile;
String sessionID;
int displayMode = 0;  // 0=vitals, 1=raw, 2=status

// ============ SETUP ============
void setup() {
  Serial.begin(115200);
  
  // Initialize LCD
  lcd.begin(20, 4);  // Assuming 20x4 LCD
  lcd.clear();
  lcd.print("Exercise Vest v1.0");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  
  // Configure pins
  pinMode(ECG_LO_PLUS, INPUT);
  pinMode(ECG_LO_MINUS, INPUT);
  pinMode(BUTTON_MODE, INPUT_PULLUP);
  pinMode(BUTTON_ADJUST, INPUT_PULLUP);
  
  // Initialize SD card
  lcd.setCursor(0, 2);
  lcd.print("SD Card...");
  
  if (!SD.begin(SD_CS)) {
    lcd.print("FAILED!");
    while(1);  // Stop if SD fails
  }
  lcd.print("OK!");
  
  // Create session ID
  sessionID = "SESSION_" + String(millis());
  
  // Create directory
  if (!SD.exists(sessionID)) {
    SD.mkdir(sessionID);
  }
  
  // Create initial files
  dataFile = SD.open(sessionID + "/VITALS.CSV", FILE_WRITE);
  if (dataFile) {
    dataFile.println("Timestamp_ms,HR_bpm,RR_bpm,Sweat_Level,ECG_Raw,Resp_Raw,GSR_Raw");
    dataFile.close();
  }
  
  delay(2000);
  lcd.clear();
  lcd.print("Ready!");
  lcd.setCursor(0, 1);
  lcd.print("Press button...");
  
  // Wait for button press to start
  while(digitalRead(BUTTON_MODE) == HIGH);
  delay(200);  // Debounce
  
  sessionStartTime = millis();
  lcd.clear();
  lcd.print("Recording...");
}

// ============ MAIN LOOP ============
void loop() {
  unsigned long now = millis();
  
  // ECG sampling (333 Hz)
  if (now - lastECGSample >= ECG_SAMPLE_INTERVAL) {
    int ecgValue = analogRead(ECG_OUTPUT);
    ecgProc.processECGSample(ecgValue);
    lastECGSample = now;
  }
  
  // Respiratory sampling (20 Hz)
  if (now - lastRespSample >= RESP_SAMPLE_INTERVAL) {
    int respValue = analogRead(RESP_SENSOR);
    respProc.processRespSample(respValue);
    lastRespSample = now;
  }
  
  // GSR sampling (5 Hz)
  if (now - lastGSRSample >= GSR_SAMPLE_INTERVAL) {
    int gsrValue = analogRead(GSR_SENSOR);
    gsrProc.processGSRSample(gsrValue);
    lastGSRSample = now;
  }
  
  // LCD update (1 Hz)
  if (now - lastLCDUpdate >= LCD_UPDATE_INTERVAL) {
    updateLCD();
    lastLCDUpdate = now;
  }
  
  // Data logging (1 Hz)
  if (now - lastDataLog >= DATA_LOG_INTERVAL) {
    logData();
    lastDataLog = now;
  }
  
  // Check mode button
  if (digitalRead(BUTTON_MODE) == LOW) {
    displayMode = (displayMode + 1) % 3;
    delay(200);  // Debounce
  }
}

// ============ LCD DISPLAY ============
void updateLCD() {
  lcd.clear();
  
  switch(displayMode) {
    case 0:  // Vital signs
      lcd.setCursor(0, 0);
      lcd.print("HR: ");
      if (ecgProc.isLeadOff()) {
        lcd.print("--");
      } else {
        lcd.print(ecgProc.getHeartRate());
      }
      lcd.print(" bpm");
      
      lcd.setCursor(0, 1);
      lcd.print("RR: ");
      lcd.print(respProc.getBreathRate());
      lcd.print(" bpm");
      
      lcd.setCursor(0, 2);
      lcd.print("Sweat: ");
      lcd.print(gsrProc.getSweatString());
      
      lcd.setCursor(0, 3);
      unsigned long elapsed = (millis() - sessionStartTime) / 1000;
      int hours = elapsed / 3600;
      int minutes = (elapsed % 3600) / 60;
      int seconds = elapsed % 60;
      char timeStr[20];
      sprintf(timeStr, "Time: %02d:%02d:%02d", hours, minutes, seconds);
      lcd.print(timeStr);
      break;
      
    case 1:  // Raw values
      lcd.setCursor(0, 0);
      lcd.print("ECG: ");
      lcd.print(ecgProc.getRawValue());
      
      lcd.setCursor(0, 1);
      lcd.print("RESP: ");
      lcd.print(respProc.getRawValue());
      lcd.print(" ");
      lcd.print(respProc.getStateString());
      
      lcd.setCursor(0, 2);
      lcd.print("GSR: ");
      lcd.print(gsrProc.getSmoothedValue());
      
      lcd.setCursor(0, 3);
      lcd.print("Mode: RAW DATA");
      break;
      
    case 2:  // Status
      lcd.setCursor(0, 0);
      lcd.print("Status: Recording");
      
      lcd.setCursor(0, 1);
      lcd.print("Leads: ");
      lcd.print(ecgProc.isLeadOff() ? "OFF" : "OK");
      
      lcd.setCursor(0, 2);
      lcd.print("Storage: ");
      // Could add SD card space check
      lcd.print("OK");
      
      lcd.setCursor(0, 3);
      lcd.print("Mode: STATUS");
      break;
  }
}

// ============ DATA LOGGING ============
void logData() {
  dataFile = SD.open(sessionID + "/VITALS.CSV", FILE_WRITE);
  
  if (dataFile) {
    // Timestamp,HR,RR,Sweat,ECG_Raw,Resp_Raw,GSR_Raw
    dataFile.print(millis());
    dataFile.print(",");
    dataFile.print(ecgProc.getHeartRate());
    dataFile.print(",");
    dataFile.print(respProc.getBreathRate());
    dataFile.print(",");
    dataFile.print(gsrProc.getSweatLevel());
    dataFile.print(",");
    dataFile.print(ecgProc.getRawValue());
    dataFile.print(",");
    dataFile.print(respProc.getRawValue());
    dataFile.print(",");
    dataFile.println(gsrProc.getSmoothedValue());
    
    dataFile.close();
    
    // Also log to serial for debugging
    Serial.print("HR:");
    Serial.print(ecgProc.getHeartRate());
    Serial.print(" RR:");
    Serial.print(respProc.getBreathRate());
    Serial.print(" Sweat:");
    Serial.println(gsrProc.getSweatLevel());
  } else {
    Serial.println("ERROR: Could not open data file!");
  }
}
```

---

## 4. Implementation Timeline

**Week 1: Individual Sensors**
- Day 1-2: ECG integration and testing
- Day 3-4: GSR integration and testing
- Day 5: Respiratory band refinement
- Day 6-7: Data logging validation

**Week 2: System Integration**
- Day 1-2: Combine all sensors
- Day 3-4: LCD interface implementation
- Day 5: 24-hour test run
- Day 6-7: Bug fixes and calibration

**Week 3: Enhancement & Documentation**
- Day 1-2: Web dashboard (if implementing)
- Day 3-4: Data analysis scripts in Python
- Day 5-6: Documentation writing
- Day 7: Video preparation

**Week 4: Final Testing**
- Day 1-2: Extended testing
- Day 3-4: Final adjustments
- Day 5: Video recording
- Day 6: Submission preparation

---

## 5. Testing & Validation Protocol
```
Test 1: Static Baseline (Person at rest)
- Duration: 30 minutes
- Expected: HR 60-80, RR 12-16, GSR stable
- Validates: Baseline detection, lead stability

Test 2: Light Activity (Walking)
- Duration: 15 minutes
- Expected: HR 80-100, RR 16-20, GSR slight increase
- Validates: Response to activity

Test 3: Moderate Exercise (Jogging/Stairs)
- Duration: 10 minutes
- Expected: HR 100-140, RR 20-30, GSR significant increase
- Validates: Dynamic range, peak detection

Test 4: Recovery
- Duration: 20 minutes
- Expected: Gradual return to baseline
- Validates: Trend tracking

Test 5: 24-Hour Endurance
- Duration: 24+ hours
- Include: Sleep, daily activities, meals
- Validates: Battery life, data integrity, long-term stability