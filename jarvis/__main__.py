from .controller import Controller

def main():
    controller = Controller()

    while True:
        user_input = input("What should I do: ")
        if user_input.lower() == "exit":
            break
        controller.manage_input(user_input)

if __name__ == "__main__":
    main()