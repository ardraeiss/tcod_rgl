from game import Game


def main():
    print('Hello World!')
    session = Game()
    print("Game: {}".format(session))
    session.run()


if __name__ == '__main__':
    main()
