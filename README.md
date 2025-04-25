# 🛰️ Universal Spacecraft Telemetry Analyzer

A powerful Streamlit application for analyzing spacecraft telemetry data with real-time anomaly detection and visualization capabilities.

## 📋 Features

- **Data Import**: Upload CSV telemetry data for instant analysis
- **Real-time Anomaly Detection**: Automated detection of anomalous readings based on configurable thresholds
- **Interactive Visualizations**:
  - 2D time-series plots for each telemetry parameter
  - 3D scatter plots and mesh visualizations of multiple parameters
  - Health status gauges for quick system assessment
- **Mission Profiles**: Pre-defined parameter thresholds for different mission types (LEO, Deep Space, Mars, etc.)
- **Alert System**:
  - Visual alerts for anomalous readings
  - Audio notifications for critical issues (using pyttsx3)
  - Email notification capability
- **Data Export**: Download analysis results in Excel format and plots as PNG
- **Simulated Data**: Option to generate synthetic telemetry data for testing and demonstration

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/spacecraft-telemetry-analyzer.git
cd spacecraft-telemetry-analyzer

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 📦 Requirements

- Python 3.7+
- Streamlit
- Pandas
- Matplotlib
- Plotly
- NumPy
- pyttsx3
- openpyxl

## 🖥️ Usage

1. Start the Streamlit application:
   ```bash
   streamlit run main.py
   ```

2. Access the application in your web browser (typically at http://localhost:8501)

3. Either:
   - Upload a telemetry CSV file using the sidebar
   - Use the simulated data option for demonstration

4. Explore the various visualizations and analysis tools

## 📊 Data Format

The application expects CSV files with the following columns:
- `timestamp`: Date and time of the telemetry reading (format: DD-MM-YYYY HH:MM)
- `temperature`: Temperature readings in °C
- `pressure`: Pressure readings in atm
- `velocity`: Velocity readings in m/s
- `battery`: Battery level percentage
- `fuel`: Fuel level percentage

Example:
```
timestamp,temperature,pressure,velocity,battery,fuel
25-04-2025 10:30,24,0.97,7071,60,97
25-04-2025 10:35,-3,0.67,7172,57,96
```

## ✨ Mission Profiles

The application comes with pre-configured parameter thresholds for different mission types:
- LEO Satellite
- Deep Space Probe
- Mars Mission
- Venus Orbiter
- Lunar Lander

You can also create and save custom profiles with your own threshold values.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io/) for the web application framework
- [Plotly](https://plotly.com/) for interactive 3D visualizations
- [Matplotlib](https://matplotlib.org/) for 2D plotting capabilities
