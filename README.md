# Exercise Monitoring Vest

A wearable real-time monitoring system for cardiovascular and respiratory metrics during exercise. Built with Arduino Mega 2560, featuring ECG heart rate monitoring, respiratory rate tracking, and galvanic skin response (sweat) detection.

## 🎯 Project Overview

**Course:** BEng/MEng Biomedical Engineering - Mechatronics Module  
**Team:** Sebastian, Fawziyah Sheikhomar, Shuo Tao, Zhiyang Ma  

### Key Features

✅ **Multi-Sensor Integration**
- 3-lead ECG (AD8232) for heart rate monitoring
- Conductive rubber respiratory band for breathing rate
- GSR sensor for sweat level detection

✅ **Real-Time Monitoring**
- 20x4 LCD display on vest
- Web-based dashboard with live graphs
- 24+ hour continuous operation

✅ **Data Logging**
- SD card storage (CSV format)
- Excel-compatible output
- Timestamp precision to millisecond

✅ **Professional Visualization**
- Real-time web dashboard
- Historical trend analysis
- Statistical summaries
- Export capabilities

## 📁 Repository Structure

```
exercise-monitoring-vest/
├── arduino/                    # Arduino firmware
│   ├── main/                  # Main integrated system
│   ├── libraries/             # Custom sensor libraries
│   │   ├── ECGProcessor/
│   │   ├── RespiratoryProcessor/
│   │   ├── GSRProcessor/
│   │   └── DataLogger/
│   └── examples/              # Individual sensor tests
├── web-dashboard/             # Real-time visualization
│   ├── dashboard.html
│   ├── serial_bridge.py
│   ├── test_data_generator.py
│   └── README.md
├── docs/                      # Documentation
│   ├── circuit-diagrams/
│   ├── datasheets/
│   └── user-manual.md
├── hardware/                  # Hardware specifications
│   ├── bill-of-materials.md
│   └── wiring-diagrams/
├── data/                      # Example datasets
│   └── sample-session.csv
├── .gitignore
├── LICENSE
└── README.md                  # This file
```

### Software Setup

1. **Arduino IDE**
   ```bash
   # Install Arduino IDE 2.0+
   # Add required libraries:
   # - LiquidCrystal (built-in)
   # - SD (built-in)
   # - SPI (built-in)
   ```

2. **Web Dashboard** (optional)
   ```bash
   cd web-dashboard
   pip install -r requirements.txt
   ```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/[your-username]/exercise-monitoring-vest.git
   cd exercise-monitoring-vest
   ```

2. **Upload Arduino code**
   ```bash
   # Open arduino/main/main.ino in Arduino IDE
   # Select: Tools > Board > Arduino Mega 2560
   # Select: Tools > Port > [Your Port]
   # Click Upload
   ```

3. **Test sensors individually** (recommended)
   ```bash
   # Upload and test each sensor separately:
   # - arduino/examples/ecg_test/
   # - arduino/examples/respiratory_test/
   # - arduino/examples/gsr_test/
   ```

4. **Run web dashboard** (optional)
   ```bash
   cd web-dashboard
   python serial_bridge.py
   # Open dashboard.html in browser
   ```

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Arduino Mega 2560                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │   ECG    │  │   RESP   │  │   GSR    │                │
│  │ 333 Hz   │  │  20 Hz   │  │   5 Hz   │                │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                │
│       │             │             │                        │
│       └─────────────┴─────────────┘                        │
│                     │                                      │
│           ┌─────────┴─────────┐                           │
│           │   Data Logger     │                           │
│           │   (SD Card 1Hz)   │                           │
│           └─────────┬─────────┘                           │
│                     │                                      │
│           ┌─────────┴─────────┐                           │
│           │   LCD Display     │                           │
│           │   (Update 1Hz)    │                           │
│           └───────────────────┘                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                                    │
         │ USB Serial                         │ Direct View
         ▼                                    ▼
┌──────────────────┐              ┌──────────────────┐
│   Web Dashboard  │              │   LCD on Vest    │
│   (Real-time)    │              │   (3 modes)      │
└──────────────────┘              └──────────────────┘
```

## 🔧 Pin Configuration

### Arduino Mega 2560 Connections

```cpp
// ECG (AD8232)
#define ECG_OUTPUT    A0    // ECG signal
#define ECG_LO_PLUS   A1    // Lead off detection +
#define ECG_LO_MINUS  A2    // Lead off detection -

// Respiratory Band
#define RESP_SENSOR   A4    // Breathing sensor

// GSR Sensor
#define GSR_SENSOR    A3    // Sweat sensor

// SD Card (SPI)
#define SD_CS         10    // Chip select
#define SD_MOSI       11    // Master out
#define SD_MISO       12    // Master in
#define SD_SCK        13    // Clock

// LCD Display (4-bit mode)
#define LCD_RS        2     // Register select
#define LCD_EN        3     // Enable
#define LCD_D4        4     // Data 4
#define LCD_D5        5     // Data 5
#define LCD_D6        6     // Data 6
#define LCD_D7        7     // Data 7

// User Interface
#define BUTTON_MODE   8     // Mode selection
#define BUTTON_START  9     // Start/stop recording
```

## 📈 Data Format

### CSV Output (SD Card)

```csv
Timestamp_ms,HR_bpm,RR_bpm,Sweat_Level,ECG_Raw,Resp_Raw,GSR_Raw,Battery_V
1000,0,0,0,512,512,720,8.4
2000,68,14,1,545,530,695,8.4
3000,72,16,2,612,522,650,8.3
```

### JSON Output (Serial/Web)

```json
{
  "hr": 72,
  "rr": 16,
  "sweat": 1,
  "leadOff": false
}
```

## 🧪 Testing

### Unit Tests (Individual Sensors)

```bash
# Test ECG sensor
arduino/examples/ecg_test/ecg_test.ino

# Test respiratory band
arduino/examples/respiratory_test/respiratory_test.ino

# Test GSR sensor
arduino/examples/gsr_test/gsr_test.ino
```

### System Integration Test

```bash
# Upload main integrated code
arduino/main/main.ino

# Verify:
# ✓ All sensors respond
# ✓ LCD displays data
# ✓ SD card logging works
# ✓ 24+ hour operation
```

### Web Dashboard Test (No Hardware)

```bash
cd web-dashboard
python test_data_generator.py
# Simulates realistic exercise session
```

## 📖 Documentation

- **[User Manual](docs/user-manual.md)** - Complete usage guide
- **[Hardware Setup](hardware/bill-of-materials.md)** - Component list and assembly
- **[API Reference](docs/api-reference.md)** - Code documentation
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Notion Workspace](https://notion.so/...)** - Detailed technical documentation

## 🎓 Academic Deliverables

This repository contains all materials for the Mechatronics module assessment:

- ✅ **Project Plan** (500 words) - See [docs/project-plan.md](docs/project-plan.md)
- ✅ **Documentation** (1500 words) - See [docs/user-manual.md](docs/user-manual.md)
- ✅ **Code** - Well-commented Arduino code in [arduino/](arduino/)
- ✅ **Example Data** - 24-hour recording in [data/](data/)
- ✅ **Extra Features** - Web dashboard with real-time visualization
- ✅ **Video Demo** - [Link to demonstration video]

## 🤝 Contributing

This is an academic project. Team members:
- Sebastian - Lead Developer, System Integration
- Fawziyah Sheikhomar - [Role]
- Shuo Tao - [Role]
- Zhiyang Ma - [Role]

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

This project is submitted as coursework for [University Name] and follows academic integrity guidelines.

## 🙏 Acknowledgments

- Course Instructor: Kawal Rhode
- AD8232 datasheet and reference designs from Analog Devices
- Arduino community for library support
- Open-source Chart.js for web visualization

## 📞 Contact

- **Project Lead:** Sebastian - [email]
- **Course:** BEng/MEng Biomedical Engineering
- **Module:** Mechatronics
- **GitHub:** [https://github.com/[your-username]/exercise-monitoring-vest](https://github.com/[your-username]/exercise-monitoring-vest)

## 🔗 Links

- [Notion Documentation](https://notion.so/...)
- [Demonstration Video](https://...)
- [Project Presentation](https://...)

---

**Last Updated:** December 2025  
**Version:** 1.0.0  
**Status:** Active Development ✅
