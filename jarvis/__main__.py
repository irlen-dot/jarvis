from jarvis.codegen.controller import CodeGenController
from .main_controller import MainController


def main():
    controller = MainController()
    while True:
        user_input = input("What should I do: ")
        if user_input.lower() == "exit":
            break

        controller.manage_input(user_input)


if __name__ == "__main__":
    main()
