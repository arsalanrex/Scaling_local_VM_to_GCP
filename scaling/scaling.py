import os
import time
import subprocess

# GCP project details
GCP_PROJECT = "decent-genius-428706-k7"
GCP_ZONE = "us-central1-c"
GCP_INSTANCE_GROUP = "gcloud-instance-group"
LOCAL_APP_PATH = "~/app/app.py"
REMOTE_APP_PATH = "~/app/app.py"

def get_cpu_usage():
    # Run the 'top' command to get CPU stats
    cmd = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\\1/' | awk '{print 100 - $1}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    cpu_usage = float(result.stdout.strip())
    return cpu_usage

def get_active_instance():
    cmd = [
        "gcloud", "compute", "instances", "list",
        "--filter=zone:{} AND name:{}-*".format(GCP_ZONE, GCP_INSTANCE_GROUP),
        "--format=value(name)"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    instances = result.stdout.strip().split("\n")
    return instances[0] if instances else None

def check_and_kill_process_on_port(instance_name):
    # Check if a process is running on port 5000
    ssh_cmd_check = f"gcloud compute ssh {instance_name} --zone {GCP_ZONE} --command 'lsof -i :5000'"
    result = subprocess.run(ssh_cmd_check, capture_output=True, text=True, shell=True)
    if result.stdout:
        print("Process found on port 5000, killing the process...")
        # Extract the process ID from the output and kill the process
        pid = result.stdout.split("\n")[1].split()[1]
        kill_cmd = f"gcloud compute ssh {instance_name} --zone {GCP_ZONE} --command 'kill -9 {pid}'"
        subprocess.run(kill_cmd, shell=True, check=True)
        print(f"Process on port 5000 killed (PID: {pid})")
    else:
        print("No process found on port 5000.")

def deploy_app(instance_name):
    if not instance_name:
        print("No active instance found for deployment.")
        return

    # Check and kill any process running on port 5000 before deploying
    check_and_kill_process_on_port(instance_name)

    # Ensure the directory exists on the remote instance
    ssh_cmd_create_dir = f"gcloud compute ssh {instance_name} --zone {GCP_ZONE} --command 'mkdir -p ~/app'"
    subprocess.run(ssh_cmd_create_dir, shell=True, check=True)

    # Now SCP the file to the remote instance
    scp_cmd = f"gcloud compute scp {LOCAL_APP_PATH} {instance_name}:~/app/app.py --zone {GCP_ZONE}"
    subprocess.run(scp_cmd, shell=True, check=True)

    # Install pip3 if not already installed
    ssh_cmd_install_pip = f"gcloud compute ssh {instance_name} --zone {GCP_ZONE} --command 'sudo apt-get update && sudo apt-get install -y python3-pip'"
    subprocess.run(ssh_cmd_install_pip, shell=True, check=True)

    # Install Flask on the remote instance
    ssh_cmd_install_flask = f"gcloud compute ssh {instance_name} --zone {GCP_ZONE} --command 'pip3 install flask'"
    subprocess.run(ssh_cmd_install_flask, shell=True, check=True)

    # Run the application on the remote instance
    ssh_cmd_run_app = f"gcloud compute ssh {instance_name} --zone {GCP_ZONE} --command 'nohup python3 ~/app/app.py &'"
    subprocess.run(ssh_cmd_run_app, shell=True, check=True)

def scale_gcp():
    scale_cmd = [
        "gcloud", "compute", "instance-groups", "managed", "resize", 
        GCP_INSTANCE_GROUP, "--size=1", "--zone", GCP_ZONE
    ]
    subprocess.run(scale_cmd, check=True)

def main():
    while True:
        cpu_usage = get_cpu_usage()
        print(f"CPU Usage: {cpu_usage}%")

        if cpu_usage > 75:
            print("High CPU detected! Scaling to cloud...")
            scale_gcp()
            time.sleep(10)  # Wait for instance to start
            instance = get_active_instance()
            deploy_app(instance)

        time.sleep(10)  # Check CPU usage every 10 sec

if __name__ == "__main__":
    main()

