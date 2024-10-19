import subprocess

def run_command(command):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Command '{' '.join(command)}' executed successfully.")
        print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{' '.join(command)}':")
        print("Error:", e)
        print("Output:", e.stdout)
        print("Error output:", e.stderr)
        return False    