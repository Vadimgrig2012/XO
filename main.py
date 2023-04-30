from random import randint

# классы исключений
# общий класс, который содержит в себе все остальные классы с исключениями (родительский класс)
class BoardException(Exception):
    pass

# исключение при попытке выстрела за территорию доски
class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь произвести выстрел за территорию игровой доски"
        
# исключение при повторной попытке выстрела в одну и ту же клетку
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

# исключение при некорректном размещении кораблей
class BoardWrongShipException(BoardException):
    pass



# класс с точками
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # метод сравнения объектов друг с другом
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # метод, которы выводит строку с координатомми точек
    def __repr__(self):
        return f"Dot({self.x}, {self.y})"




# класс корабля
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    # метод создания точек
    @property
    def dots(self):
        # создаем пустой список точек для корабля
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            # если параметр о = 0, у корабля положение вертикальное
            if self.o == 0:
                cur_x += i

            # если параметр о = 1, у корабля положение горизонтальное
            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    # метод для проверки на попадание
    def shooten(self, shot):
        return shot in self.dots




# класс поля
class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid

        # количество пораженных кораблей
        self.count = 0

        # сетка поля которая хранит состояние с пустыми клетками
        self.field = [ ["0"] * size for _ in range(size) ]

        # занятые точки (либо кораблем, либо выстрелом)
        self.busy = []
        # список кораблей на доске
        self.ships = []

    # вывод корабля на доску
    def __str__(self):
        res = ""
        res += " | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        # параметр, который отвечает за скрытие кораблей на доске
        if self.hid:
            res = res.replace("■", "0")
        return res

    # метод, который проверяет, находится ли точка за пределами доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    #  метод, который определяет контур корабля. Он поможет определить, куда нельзя ставить точки
    def contour (self, ship, verb = False):
        # список содержит все точки, вокруг которых мы находимся. (0, 0) это сама точка
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1),
        ]
        # в данном цикле мы находим все точки, которые находятся по соседству с кораблем
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                # проверка на невыхождение за границы и на отсутсвие в списке занятых
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    # метот для размещения корабля
    def add_ship(self, ship):
        # проверка на нахождение в границах поля каждой точки
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        #в каждой точке корабля устанавливаем ■ и добавляем точку в список занятых
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # метод стрельбы по доске
    def shot(self, d):
        # проверка на выстрел по территории доски
        if self.out(d):
            raise BoardException()
        # проверка на выстрел в разные клетки
        if d in self.busy:
            raise BoardUsedException()
        # добавляем точку выстрела в список занятых
        self.busy.append(d)
        # проходим циклом по кораблям и проверяем на: точка выстрела == точке корабля
        for ship in self.ships:
            # Если корабль был подтрелян - уменьшаем кол-во жизни корабля и ставим в эту точку "X"
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                # если у корабля нет жизней - прибавляем к счетчику уничтоженных кораблей 1, обводим по контуру и принтим сообщение
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        #  если ни один из кораблей не был поражен - ставим точку и принтим сообщение
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False
    
    # метод для хранения списка точек, в которые стрелял игрок
    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)




# класс игрока, в качестве аргументов передаются 2 доски
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    # метод для потомков класса
    def ask(self):
        raise NotImplementedError()
    # в бесконечном цикле спрашиваем координаты у пользователя
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)





# класс игрока ИИ (наследуемся от Player)
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d




# класс игрока-пользователя (наследуемся от Player)
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            # проверка на кол-во координат
            if len(cords)!=2:
                print(" Введите координаты! ")
                continue

            x, y = cords
            # проверка на ввод чисел
            if not(x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)




# класс игры и генерация игровой доски
class Game:
    # конструктор игры с размером доски 6 и скрытием кораблей у ИИ, генрация 2 случ. досок для ИИ и пользователя
    def __init__(self, size=6):
        # список длинн кораблей
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        # создаем 2 игроков
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    # метод, который пытается создать доску
    def try_board(self):
        # создадим доску
        board = Board(size=self.size)
        # количество попыток поставить корабли
        attempts = 0
        # для каждой длинны корабля пытаемся его поставить в беск.цикле
        for l in self.lens:
            while True:
                attempts += 1
                # если попыток больше 2000, то возвращаем пустую доску
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    # добавление корабля
                    board.add_ship(ship)
                    # если прошло, то завершаем цикл
                    break
                # если исключение, то новая итерация
                except BoardWrongShipException:
                    pass
        # когда мы разметили все корабли, возвращаем доску
        board.begin()
        return board
    
    # метод, который гарантированно генерит случайную доску
    def random_board(self):
        # пустая доска
        board = None
        # в беск.цикле пытаемся создать доску
        while board is None:
            board = self.try_board()
        return board

    # приветствие
    def greet(self):
        print("__________________")
        print("    Приветствую   ")
        print("       в игре     ")
        print("    морской бой   ")
        print("__________________")
        print(" формат ввода:x y ")
        print(" x - номер строки ")
        print(" y - номер столбца")

    # игровой цикл
    def loop(self):
        # номер хода
        num = 0
        # выводим доски и действуем в зависимости от номера хода
        while True:
            print("-"*20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-"*20)
            print("Доска ИИ:")
            print(self.ai.board)
            print("-"*20)
            # если номер хода четный - ходит пользователь
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                # если номер хода не четный - ходит ИИ
                print("Ходит ИИ!")
                repeat = self.ai.move()
            # если нужно повторить ход, то уменьшаем номер хода на 1
            if repeat:
                num -= 1
            # проверка на кол-во пораженных кораблей ИИ
            if self.ai.board.defeat():
                print("-"*20)
                print("Пользователь выиграл!")
                break
             # проверка на кол-во пораженных кораблей пользователя              
            if self.us.board.defeat():
                print("-"*20)
                print("ИИ выиграл!")
                break
            num += 1

    # старт игры
    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()