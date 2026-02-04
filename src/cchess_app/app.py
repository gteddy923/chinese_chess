from turtle import mainloop

from .state import get_app


def main():
    get_app().run()
    mainloop()


if __name__ == "__main__":
    main()
