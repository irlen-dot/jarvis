# import os
# import subprocess
# from contextlib import contextmanager
# from threading import local

# Thread-local storage to keep track of the current directory
# _thread_local = local()

# @contextmanager
# def change_dir(path):
#     """
#     Context manager for changing the current working directory
#     """
#     print(f"Changing to directory: {path}")
#     original_dir = os.getcwd()
#     try:
#         os.chdir(path)
#         _thread_local.current_dir = path
#         print(f"Current working directory: {os.getcwd()}")
#         yield
#     finally:
#         print(f"Changing back to original directory: {original_dir}")
#         os.chdir(original_dir)
#         _thread_local.current_dir = original_dir
#         print(f"Current working directory: {os.getcwd()}")

# def run_command(command):
#     if isinstance(command, list):
#         command = ' '.join(command)

#     current_dir = getattr(_thread_local, 'current_dir', os.getcwd())
#     full_command = f'cd /d "{current_dir}" && {command}' if os.name == 'nt' else f'cd "{current_dir}"; {command}'
    
#     try:
#         result = subprocess.run(full_command, check=True, capture_output=True, text=True, shell=True)
#         print(f"Command '{command}' executed successfully in {current_dir}.")
        
#         output = result.stdout
#         if result.stderr:
#             output += "\nError output:\n" + result.stderr
        
#         print("Output:", output)
        
#         return True, output
#     except subprocess.CalledProcessError as e:
#         print(f"Error executing command '{command}' in {current_dir}:")
#         print("Error:", e)
        
#         error_output = e.stdout
#         if e.stderr:
#             error_output += "\nError output:\n" + e.stderr
        
#         print("Output:", error_output)
        
#         return False, error_output