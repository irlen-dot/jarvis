from jarvis.helper.cmd_prompt import run_command
from .main_controller import MainController
from jarvis.git.service import create_and_push_repo

def main():
    # create_and_push_repo(r"C:\\Users\\irlen\\Documents\\projects\\python\\Armani", "Armani", "python")
    controller = MainController()
    while True:
        user_input = input("What should I do: ")
        if user_input.lower() == "exit":
            break
        controller.manage_input(user_input)

if __name__ == "__main__":
    main()