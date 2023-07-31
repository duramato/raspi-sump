#!/usr/bin/env python
import os
import subprocess
from datetime import datetime


def get_os_version():
    with open("/etc/os-release", "r") as file:
        for line in file:
            if line.startswith("VERSION_ID="):
                return line.strip().split("=")[1].strip('"')


def get_raspi_sump_version(actual_user):
    with open(f"/home/{actual_user}/raspi-sump/VERSION", "r") as file:
        return file.read().strip()


def get_python_version():
    return subprocess.check_output(["python3", "--version"], text=True).strip()


def run_command(command):
    try:
        # return subprocess.check_output(command, text=True).strip()
        return subprocess.check_output(
            command, text=True, stderr=subprocess.PIPE
        ).strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.cmd}. Return code: {e.returncode}. Output: {e.output}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def write_to_file(file_path, content):
    with open(file_path, "w") as file:
        file.write(content)


if __name__ == "__main__":
    # Determine the actual username
    actual_user = os.getlogin()

    # Paths
    home_folder = f"/home/{actual_user}"
    raspi_sump_folder = f"/home/{actual_user}/raspi-sump"
    support_folder = f"/home/{actual_user}/raspi-sump/support"
    support_file_path = f"/home/{actual_user}/raspi-sump/support/support.txt"

    # Create support folder if it doesn't exist
    os.makedirs(support_folder, exist_ok=True)

    # Get the required information
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os_version = get_os_version()
    raspi_sump_version = get_raspi_sump_version(actual_user)
    python_version = get_python_version()

    # Run commands with exception handling
    try:
        raspi_sump_status = run_command(["systemctl", "--user", "status", "raspisump"])
    except Exception as e:
        raspi_sump_status = f"Error getting status: {str(e)}"

    try:
        rsumpwebchart_timer_status = run_command(
            ["systemctl", "--user", "status", "rsumpwebchart.timer"]
        )
    except Exception as e:
        rsumpwebchart_timer_status = f"Error getting status: {str(e)}"

    try:
        logs_error_log = run_command(["cat", f"{raspi_sump_folder}/logs/error_log"])
    except Exception as e:
        logs_error_log = f"Error reading logs/error_log: {str(e)}"

    try:
        logs_info_log = run_command(["cat", f"{raspi_sump_folder}/logs/info_log"])
    except Exception as e:
        logs_info_log = f"Error reading logs/info_log: {str(e)}"

    try:
        logs_heartbeat_log = run_command(
            ["tail", "-n", "10", f"{raspi_sump_folder}/logs/heartbeat.log"]
        )
    except Exception as e:
        logs_heartbeat_log = f"Error reading logs/heartbeat.log: {str(e)}"

    try:
        logs_alert_log = run_command(
            ["tail", "-n", "10", f"{raspi_sump_folder}/logs/alert.log"]
        )
    except Exception as e:
        logs_alert_log = f"Error reading logs/alert.log: {str(e)}"

    # Prepare the content for the support.txt file
    content = f"""\
Date file generated: {current_date}
os version: {os_version}
raspi-sump version: {raspi_sump_version}
python version on system: {python_version}

Systemctl status for raspisump:
{raspi_sump_status}

Systemctl status for rsumpwebchart.timer:
{rsumpwebchart_timer_status}

Logs/error_log content:
{logs_error_log}

Logs/info_log content:
{logs_info_log}

Last 10 lines of logs/heartbeat.log:
{logs_heartbeat_log}

Last 10 lines of logs/alert.log:
{logs_alert_log}
"""

    # Write the content to the support.txt file
    write_to_file(support_file_path, content)

    print("Support information has been gathered and saved to support.txt.")
