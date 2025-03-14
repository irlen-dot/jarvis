import msvcrt
import os
import click


class Menu:
    def get_key(self) -> str:
        key = msvcrt.getch()
        if key == b"\xe0":
            key = msvcrt.getch()
            return {b"H": "up", b"P": "down"}.get(key, None)
        return key.decode("utf-8")

    def show_menu(self, options, title="Select version type") -> str:
        selected = 0
        while True:
            os.system("cls")
            click.echo(f"\n{title} (↑↓ to move, Enter to select):\n")
            for i, proj_type in enumerate(options):
                if i == selected:
                    click.echo(f" > {proj_type} <")
                else:
                    click.echo(f"   {proj_type}  ")
            key = self.get_key()

            if key == "up" and selected > 0:
                selected -= 1
            elif key == "down" and selected < len(options) - 1:
                selected += 1
            elif key == "\r":
                return options[selected]
