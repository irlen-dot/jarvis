import os
import subprocess
from contextlib import contextmanager
from threading import local
from langchain_core.tools import tool

# Thread-local storage to keep track of the current directory
_thread_local = local()


@contextmanager
def change_dir(path):
    """
    Context manager for changing the current working directory.
    """
    print(f"Changing to directory: {path}")
    original_dir = os.getcwd()
    try:
        os.chdir(path)
        _thread_local.current_dir = path
        print(f"Current working directory: {os.getcwd()}")
        yield
    finally:
        print(f"Changing back to original directory: {original_dir}")
        os.chdir(original_dir)
        _thread_local.current_dir = original_dir
        print(f"Current working directory: {os.getcwd()}")


@tool
def run_command(command):
    """This tool runs commands in the command prompt."""
    if isinstance(command, list):
        command = " ".join(command)

    try:
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, shell=True
        )
        print(f"Command '{command}' executed successfully in {command}.")

        output = result.stdout
        if result.stderr:
            output += "\nError output:\n" + result.stderr

        print("Output:", output)

        return True, output
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{command}' in {command}:")
        print("Error:", e)

        error_output = e.stdout
        if e.stderr:
            error_output += "\nError output:\n" + e.stderr

        print("Output:", error_output)

        return False, error_output
