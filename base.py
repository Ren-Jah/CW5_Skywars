from unit import BaseUnit


class BaseSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Arena(metaclass=BaseSingleton):
    STAMINA_PER_ROUND = 1
    player = BaseUnit
    enemy = BaseUnit
    game_is_running = False
    battle_result = None

    def start_game(self, player: BaseUnit, enemy: BaseUnit):
        """ Присваиваем экземпляру класса аттрибуты "игрок" и "противник",
        а также выставляем True для свойства "началась ли игра"""

        self.player = player
        self.enemy = enemy
        self.game_is_running = True

    def _check_players_hp(self):
        """ Проверка здоровья игрока и врага и возвращение результата строкой:
            может быть три результата: Игрок проиграл битву, выиграл, ничья и сохраняем его в (self.battle_result),
            если Здоровья игроков в порядке то ничего не происходит"""

        if self.player.hp <= 0 and self.enemy.hp <= 0:
            self.battle_result = 'Ничья'

        if self.player.hp <= 0:
            self.battle_result = 'Игрок проиграл битву!'

        if self.enemy.hp <= 0:
            self.battle_result = 'Игрок выиграл битву!'

        if self.battle_result:
            return self._end_game()

    def _stamina_regeneration(self):
        """ Регенерация здоровья и стамины для игрока и врага за ход,
        в этом методе к количеству стамины игрока и врага прибавляется константное значение"""

        if self.player.stamina + self.STAMINA_PER_ROUND > self.player.unit_class.max_stamina:
            self.player.stamina = self.player.unit_class.max_stamina

        elif self.player.stamina < self.player.unit_class.max_stamina:
            self.player.stamina += self.STAMINA_PER_ROUND

        if self.enemy.stamina + self.STAMINA_PER_ROUND > self.enemy.unit_class.max_stamina:
            self.enemy.stamina = self.enemy.unit_class.max_stamina

        elif self.enemy.stamina < self.enemy.unit_class.max_stamina:
            self.enemy.stamina += self.STAMINA_PER_ROUND

    def next_turn(self):
        """ Срабатывает когда игроп пропускает ход или когда игрок наносит удар."""

        # Проверка здоровья игрока и соперника
        result = self._check_players_hp()
        # если есть результат битвы, возвращается строкой итог битвы и информация о победителе.
        if result:
            return result

        # если бой продолжается, то каждый игрок регенерирует выносливость за раунд
        if self.game_is_running:
            self._stamina_regeneration()
            self.player.stamina = round(self.player.stamina, 1)
            self.enemy.stamina = round(self.enemy.stamina, 1)
            self.player.hp = round(self.player.hp, 1)
            self.enemy.hp = round(self.enemy.hp, 1)
            # и вызывается функция по ответному удару врага
            return self.enemy.hit(self.player)

    def _end_game(self):
        """ Завершение игры"""

        # очищаем синглтон
        self._instances = {}

        # останавливаем игру и вовзращаем результат
        result = self.battle_result
        self.game_is_running = False
        return result

    def player_hit(self):
        """ КНОПКА УДАР ИГРОКА """

        result = self.player.hit(self.enemy)
        # получаем результат от функции self.player.hit и запускаем следующий ход
        return f"{result} {self.next_turn()}"

    def player_use_skill(self):
        """ КНОПКА ИГРОК ИСПОЛЬЗУЕТ УМЕНИЕ"""

        # получаем результат от функции self.use_skill
        result = self._check_players_hp()
        if result:
            return result
        # включаем следующий ход и возвращаем результат удара
        return f"{result} {self.next_turn()}"
