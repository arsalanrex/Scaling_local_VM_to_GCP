# Scaling Local Virtual Machine to Google Cloud Platform 

## Overview
This project demonstrates how to monitor and scale a local VM instance to Google Cloud Platform (GCP) when CPU utilization exceeds a threshold (75%).

## Repository Structure
```
Scaling_local_VM_to_GCP/
│── app/
│   └── app.py                                     # Web application
│── scaling/
│   └── scaling.py                                 # Auto-scaling script
│── Resource Utilization Dashboard.json  # Grafana dashboard configuration
│── README.md                                   # Documentation
```

## Prerequisites
Ensure you have the following installed on your Ubuntu system:
- openssh-server
- gcloud-sdk
- Grafana
- Prometheus
- flask (for web application)
- stress (for CPU load testing)

## Installation and Setup

Step 1: Install openssh-server

- Update your Ubuntu system and install opessh-server using the following command:
```
sudo apt update
sudo apt install openssh-server
```
- The installation of all the necessary components will begin. Answer "Yes" to all the system prompts. 

- Start openssh-server
```
sudo systemctl enable ssh
sudo systemctl start ssh
```
- Check the status of your ssh server
```
sudo systemctl status ssh
```

Step 2: Install Google Cloud SDK (gcloud)

- Install the gcloud CLI snap package:
```
snap install google-cloud-cli --classic
```
- Verify installation
```
gcloud version
```
- Initialise gcloud
```
gcloud init
```
- Authenticate with your gcloud account and select a project/create new project to continue.

- Use the following command to create a new instance in your gcloud
```
arsalan@arsalanvm:~$ gcloud compute instances create gcloud-vm-instance \
                                --zone=us-central1-a \
                                --image-family=ubuntu-2204-lts \
                                --image-project=ubuntu-os-cloud \
                                --machine-type=e2-medium
```

Step 3: Install Prometheus

- Add a usergroup for Prometheus
```
sudo useradd --no-create-home --shell /bin/false prometheus
sudo mkdir /etc/prometheus /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus /var/lib/prometheus
```
- Download and extract Prometheus:
```
curl -LO https://github.com/prometheus/prometheus/releases/latest/download/prometheus-*.linux-amd64.tar.gz
tar xvf prometheus-*.linux-amd64.tar.gz
cd prometheus-*.linux-amd64
sudo mv prometheus promtool /usr/local/bin/
```
- Create a configuration file (/etc/prometheus/prometheus.yml):
```
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9090']
```
- Start Prometheus:
```
prometheus --config.file=/etc/prometheus/prometheus.yml
```

Step 4: Install Grafana

- Update your Ubuntu system using the following command:
```
sudo apt-get update
```
- Add the Grafana repository to your Ubuntu installation:
```
sudo apt-get install -y apt-transport-https
sudo apt-get install -y software-properties-common wget
sudo wget -q -O /usr/share/keyrings/grafana.key https://apt.grafana.com/gpg.key
echo "deb [signed-by=/usr/share/keyrings/grafana.key] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
```
- Install Grafana as a service
```
sudo apt-get update
sudo apt-get install grafana
```
- Check Grafana version
```
grafana-server -v
```
- Start the Grafana service and enable it on boot using the following command:
```
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```
- Check the status of the Grafana service:
```
sudo systemctl status grafana-server
```
- Access Grafana at (default credentials: admin/admin) : 
```
http://localhost:3000
```

Step 5: Import Grafana Dashboard
- Open Grafana `(http://localhost:3000)`
- Navigate to Dashboards > Import
- Upload Resource Utilization Dashboard.json from the monitoring/ directory
- Set Prometheus as the data source and import
- Running the Scaling Script

Step 7: Run `app.py`
- Run app.py to check if the application is working as expected.
- Go to `http://localhost:5000` to verify the application.

Step 7: Run `scaling.py`
- Navigate to the scaling/ directory and execute:
- python3 scaling.py
- The script continuously monitors CPU utilization and triggers auto-scaling when it exceeds 75%.

Step 8: Generate High CPU Load (stress)
- To test scaling behavior, run:
```
sudo apt install -y stress
stress --cpu 4 --timeout 180sec
```
- This will increase CPU usage, triggering the auto-scaling mechanism.

## Notes

- Ensure you have configured gcloud properly to deploy new instances.
- scaling.py will automatically create new instances when CPU usage crosses 75%.
- The Grafana dashboard helps visualize system resource usage.

## License

This project is licensed under the MIT License.
