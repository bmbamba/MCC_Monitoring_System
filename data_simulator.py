import random
import datetime
from dataclasses import dataclass, field
from typing import List, Dict
import numpy as np

@dataclass
class MotorData:
    """Data structure for motor parameters"""
    name: str
    status: str  # 'Running', 'Stopped', 'Fault'
    current: float  # Amps
    temperature: float  # Celsius
    vibration: float  # mm/s
    runtime_hours: float
    fault_code: int

    # ── NEW: rolling history buffers for trend & FFT analysis ──
    current_history: List[float] = field(default_factory=list)
    temp_history: List[float] = field(default_factory=list)
    vibe_history: List[float] = field(default_factory=list)
    HISTORY_SIZE: int = field(default=30, init=False, repr=False)

    # ── NEW: computed analytics ──
    health_score: float = field(default=100.0)   # 0–100
    current_trend: str = field(default="stable") # 'rising', 'falling', 'stable'
    temp_trend: str = field(default="stable")
    vibe_trend: str = field(default="stable")
    dominant_freq_hz: float = field(default=0.0) # Hz from FFT
    fft_alarm: bool = field(default=False)        # True when anomalous frequency detected

    def update_history(self, current, temperature, vibration):
        """Push new readings into rolling buffers."""
        for buf, val in [(self.current_history, current),
                         (self.temp_history, temperature),
                         (self.vibe_history, vibration)]:
            buf.append(val)
            if len(buf) > self.HISTORY_SIZE:
                buf.pop(0)

    def compute_trend(self, buf, threshold=0.05):
        """
        Linear regression slope over the buffer.
        Returns 'rising', 'falling', or 'stable'.
        threshold: fraction of mean value that counts as a real trend.
        """
        if len(buf) < 6:
            return "stable"
        x = np.arange(len(buf), dtype=float)
        slope = np.polyfit(x, buf, 1)[0]
        mean = np.mean(buf) if np.mean(buf) != 0 else 1.0
        rel = abs(slope) / abs(mean)
        if rel < threshold:
            return "stable"
        return "rising" if slope > 0 else "falling"

    def compute_health(self, thresholds):
        """
        Score 0–100 combining three parameters.
        Each parameter contributes up to 33 points.
        """
        if self.status != "RUNNING":
            self.health_score = 0.0 if self.status == "FAULT" else 50.0
            return

        def param_score(val, low, high, weight=33.0):
            if val <= low:
                return weight
            if val >= high:
                return 0.0
            return weight * (1.0 - (val - low) / (high - low))

        c_lo, c_hi = self.current_history[0] if self.current_history else self.current, thresholds["current_high"]
        t_lo, t_hi = 60.0, thresholds["temp_high"]
        v_lo, v_hi = 3.0, thresholds["vibration_high"]

        score = (param_score(self.current, c_lo, c_hi) +
                 param_score(self.temperature, t_lo, t_hi) +
                 param_score(self.vibration, v_lo, v_hi, 34.0))
        # Penalty for rising trends on current or vibration
        if self.current_trend == "rising":
            score -= 5
        if self.vibe_trend == "rising":
            score -= 8
        if self.fft_alarm:
            score -= 10
        self.health_score = round(max(0.0, min(100.0, score)), 1)

    def run_fft(self, sample_rate_hz=0.5):
        """
        FFT on vibration history buffer.
        sample_rate_hz: one sample every 2 s by default → 0.5 Hz.
        Sets dominant_freq_hz and fft_alarm.
        """
        if len(self.vibe_history) < 16:
            return
        signal = np.array(self.vibe_history) - np.mean(self.vibe_history)
        fft_vals = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(len(signal), d=1.0 / sample_rate_hz)
        # Ignore DC (index 0)
        peak_idx = np.argmax(fft_vals[1:]) + 1
        self.dominant_freq_hz = round(float(freqs[peak_idx]), 4)
        peak_amplitude = fft_vals[peak_idx]
        mean_amplitude = np.mean(fft_vals[1:])
        # Alarm if peak is more than 3× the mean (harmonic anomaly)
        self.fft_alarm = bool(peak_amplitude > 3.0 * mean_amplitude)

class MotorSimulator:
    """Simulates motor data for mining equipment"""
    
    def __init__(self):
        self.motors: List[Dict] = [
            {
                "name": "Conveyor Belt - CV01",
                "type": "Conveyor",
                "normal_current": (45, 65),
                "normal_temp": (55, 75),
                "normal_vibration": (2.5, 4.5),
                "critical": True
            },
            {
                "name": "Slurry Pump - PM01", 
                "type": "Pump",
                "normal_current": (35, 55),
                "normal_temp": (50, 70),
                "normal_vibration": (2.0, 4.0),
                "critical": True
            },
            {
                "name": "Crusher - CR01",
                "type": "Crusher",
                "normal_current": (80, 110),
                "normal_temp": (60, 85),
                "normal_vibration": (3.0, 5.5),
                "critical": True
            },
            {
                "name": "Ventilation Fan - VF01",
                "type": "Fan",
                "normal_current": (25, 40),
                "normal_temp": (45, 65),
                "normal_vibration": (1.5, 3.5),
                "critical": False
            },
            {
                "name": "Thickener Drive - TH01",
                "type": "Drive",
                "normal_current": (30, 50),
                "normal_temp": (50, 70),
                "normal_vibration": (2.0, 4.0),
                "critical": True
            },
            {
                "name": "Compressor - AC01",
                "type": "Compressor",
                "normal_current": (55, 75),
                "normal_temp": (55, 75),
                "normal_vibration": (2.5, 4.5),
                "critical": False
            }
        ]
        
        self.motor_states = {}
        self._initialize_states()
        
    def _initialize_states(self):
        """Initialize random states for motors"""
        for motor in self.motors:
            # 90% chance of running, 5% stopped, 5% fault
            rand = random.random()
            if rand < 0.9:
                status = "Running"
                fault_code = 0
            elif rand < 0.95:
                status = "Stopped"
                fault_code = 0
            else:
                status = "Fault"
                fault_code = random.choice([1, 2, 3, 4])  # Various fault codes
            
            self.motor_states[motor["name"]] = {
                "status": status,
                "fault_code": fault_code,
                "runtime_hours": random.uniform(100, 5000)
            }
    
    def _get_value(self, normal_range, status, add_fault_effect=True):
        """Generate realistic sensor values"""
        if status == "Stopped":
            return 0.0
        elif status == "Fault" and add_fault_effect:
            # Fault causes abnormal readings
            if random.random() < 0.7:
                return random.uniform(normal_range[1] * 1.2, normal_range[1] * 1.8)
            else:
                return random.uniform(normal_range[0], normal_range[1])
        else:
            # Normal operation with some noise
            return random.uniform(normal_range[0], normal_range[1])
    
    def get_all_motor_data(self) -> List[MotorData]:
        """Get current data for all motors"""
        motor_data_list = []
        
        for motor in self.motors:
            name = motor["name"]
            state = self.motor_states[name]
            status = state["status"]
            
            # Generate sensor readings
            current = self._get_value(motor["normal_current"], status)
            temperature = self._get_value(motor["normal_temp"], status)
            vibration = self._get_value(motor["normal_vibration"], status)
            
            # Small random walk to simulate real data
            if status == "Running" and random.random() < 0.3:
                current += random.uniform(-2, 2)
                temperature += random.uniform(-1, 1)
                vibration += random.uniform(-0.2, 0.2)
            
            motor_data = MotorData(
                name=name,
                status=status,
                current=round(current, 1),
                temperature=round(temperature, 1),
                vibration=round(vibration, 2),
                runtime_hours=round(state["runtime_hours"], 1),
                fault_code=state["fault_code"]
            )

            # ── NEW: update rolling buffers & run analytics ──
            motor_data.update_history(motor_data.current, motor_data.temperature, motor_data.vibration)
            motor_data.current_trend = motor_data.compute_trend(motor_data.current_history)
            motor_data.temp_trend    = motor_data.compute_trend(motor_data.temp_history)
            motor_data.vibe_trend    = motor_data.compute_trend(motor_data.vibe_history)
            motor_data.run_fft()
            thresholds = {"current_high": 90, "temp_high": 90, "vibration_high": 7.0}
            motor_data.compute_health(thresholds)

            motor_data_list.append(motor_data)
        
        return motor_data_list
    
    def generate_alert(self, motor: MotorData) -> Dict:
        """Generate alert if values exceed thresholds"""
        alerts = []
        
        # Define thresholds
        thresholds = {
            "current": 90,
            "temperature": 90,
            "vibration": 7.0
        }
        
        if motor.status == "Fault":
            alerts.append({
                "level": "CRITICAL",
                "motor": motor.name,
                "message": f"Fault detected - Code {motor.fault_code}",
                "timestamp": datetime.datetime.now()
            })
        
        if motor.status == "Running":
            if motor.current > thresholds["current"]:
                alerts.append({
                    "level": "WARNING",
                    "motor": motor.name,
                    "message": f"High current: {motor.current}A (Threshold: {thresholds['current']}A)",
                    "timestamp": datetime.datetime.now()
                })
            
            if motor.temperature > thresholds["temperature"]:
                alerts.append({
                    "level": "WARNING",
                    "motor": motor.name,
                    "message": f"High temperature: {motor.temperature}°C",
                    "timestamp": datetime.datetime.now()
                })
            
            if motor.vibration > thresholds["vibration"]:
                alerts.append({
                    "level": "ALERT",
                    "motor": motor.name,
                    "message": f"Excessive vibration: {motor.vibration}mm/s",
                    "timestamp": datetime.datetime.now()
                })
        
        return alerts
    
    def update_status(self, motor_name: str, new_status: str):
        """Manually update motor status (for simulation control)"""
        if motor_name in self.motor_states:
            self.motor_states[motor_name]["status"] = new_status
            if new_status != "Fault":
                self.motor_states[motor_name]["fault_code"] = 0