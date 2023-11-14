import subprocess

def open_dfeet():
    try:
        # Launch D-feet using subprocess
        subprocess.run(["d-feet"])
    except FileNotFoundError:
        print("D-feet is not installed. Please install it using 'sudo apt-get install d-feet'.")

if __name__ == "__main__":
    open_dfeet()
