# MCC Condition Monitoring System

Industrial motor condition monitoring system for real-time equipment health tracking.

## 📋 Overview

This application provides real-time monitoring, predictive maintenance alerts, and analytics for industrial motors in MCC (Motor Control Centre) environments.

## ✨ Features

- **Real-time Monitoring**: Live current, temperature, vibration, and power readings
- **Predictive Analytics**: Trend detection and FFT vibration analysis
- **Health Scoring**: Automated health scores (0-100) for each motor
- **Alert System**: Critical, warning, and info alerts with notifications
- **Data Export**: Export reports to CSV/Excel
- **Historical Data**: SQLite database storage with trend analysis
- **Modern UI**: Dark theme with glass effects and animations
- **Standalone EXE**: Windows executable available

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcc-monitoring-system.git
cd mcc-monitoring-system

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
