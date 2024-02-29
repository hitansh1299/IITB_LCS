# IITB_LCS: Low-Cost Air Quality Sensor Network

## Introduction

The IITB_LCS project focuses on developing a low-cost sensor (LCS) network for air quality (AQ) monitoring. Aimed at providing high spatio-temporal coverage at a fraction of traditional monitoring costs, this project addresses the critical need for accurate and reliable AQ data across heterogeneous environments.

## Features

- **Self-Calibrating**: Periodically recalibrates against reference-grade analyzers to maintain accuracy.
- **Self-Diagnosable**: Alerts users for maintenance, ensuring continuous, high-quality data.
- **Optimized for Low Cost**: Enables widespread AQ monitoring with minimal financial investment.
- **High Spatial and Temporal Resolution**: Captures the highly variable nature of AQ in urban and non-urban settings.

## Installation

1. Clone the repository:
```
git clone https://github.com/hitansh1299/IITB_LCS.git
```
2. Install required dependencies:
```
pip install -r requirements.txt
```

## Usage

- To start collecting data from the LCS network, run:
```
python app.py
```
- For configuration details, refer to `config.py`.
- Data analysis and calibration scripts can be found under `models` and is under development.

## Contributing

We welcome contributions from the community, including bug reports, feature requests, and code contributions. Please open a PR to help with the code.
## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Contact

For any queries or further information, please contact hitanshah.j.shah@gmail.com
