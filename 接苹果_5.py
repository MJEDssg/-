import time
import pygame
from pygame.locals import *
from sys import exit
import random
from random import randint

# 定义窗口分辨率
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# 图片
BACKGROUND_IMAGE_PATH = "beijing.jpg"
BACKGROUND_IMAGE_PATH2 = "./images/bg3.jpg"
MONKEY_IMAGE_PATH = "./images/people3.png"
APPLE_IMAGE_PATH = "./images/apple.png"
BOMB_IMAGE_PATH = "./images/bomb.png"
APPLE_SOUND_PATH = "./images/music4.mp3"
BACKGROUND_IMAGE_PATH3 = "./images/bg4.png"
BOMB_SOUND_PATH = "./images/music.mp3"
# 加载音频文件
pygame.mixer.init()
apple_sound = pygame.mixer.Sound(APPLE_SOUND_PATH)
bomb_sound = pygame.mixer.Sound(BOMB_SOUND_PATH)
MOVE_STATUS = False
OVER_FLAG = False
START_TIME = None
offset = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0, pygame.K_UP: 0, pygame.K_DOWN: 0,
          pygame.K_w: 0, pygame.K_a: 0, pygame.K_s: 0, pygame.K_d: 0}

# 定义画面帧率
FRAME_RATE = 60

# 定义动画周期（帧数）
ANIMATE_CYCLE = 30

ticks = 0
clock = pygame.time.Clock()


# 猴子类
class Monkey(pygame.sprite.Sprite):
    # 苹果的数量
    apple_num = 0
    pygame.mixer.init()
    # 加载音频文件
    apple_sound = pygame.mixer.Sound(APPLE_SOUND_PATH)

    def __init__(self, mon_surface, monkey_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = mon_surface
        self.rect = self.image.get_rect()
        self.rect.topleft = monkey_pos
        self.speed = 5

    # 控制猴子的移动
    def get_velocity(self, _offset):
        velocity = pygame.math.Vector2(0, 0)  # 创建一个二维向量
        direction = None  # 表示人物移动的方向
        if _offset[pygame.K_UP] or _offset[pygame.K_w]:
            velocity += pygame.math.Vector2(0, -self.speed)  # 通过速度控制移动距离
            direction = 'up'
        if _offset[pygame.K_DOWN] or _offset[pygame.K_s]:
            velocity += pygame.math.Vector2(0, self.speed)
            direction = 'down'
        if _offset[pygame.K_LEFT] or _offset[pygame.K_a]:
            velocity += pygame.math.Vector2(-self.speed, 0)
            direction = 'left'
        if _offset[pygame.K_RIGHT] or _offset[pygame.K_d]:
            velocity += pygame.math.Vector2(self.speed, 0)
            direction = 'right'
        return velocity, direction

    def move(self, _offset):
        velocity, direction = self.get_velocity(_offset)
        x = self.rect.left + velocity.x
        y = self.rect.top + velocity.y
        if y < 0:
            self.rect.top = 0
        elif y >= SCREEN_HEIGHT - self.rect.height:
            self.rect.top = SCREEN_HEIGHT - self.rect.height
        else:
            self.rect.top = y
        if x < 0:
            self.rect.left = 0
        elif x > SCREEN_WIDTH - self.rect.width:
            self.rect.left = SCREEN_WIDTH - self.rect.width
        else:
            self.rect.left = x

    # 接炸弹
    def picking_bomb(self, bomb_group1):
        # 判断是否接到炸弹
        picked_bombs = pygame.sprite.spritecollide(self, bomb_group1, True)
        # 接到的炸弹消失
        if picked_bombs:
            bomb_sound.play()
            global OVER_FLAG
            OVER_FLAG = True
            self.kill()

    # 接苹果
    def picking_apple(self, app_group):

        # 判断接到几个苹果
        picked_apples = pygame.sprite.spritecollide(self, app_group, True)

        # 添加分数
        self.apple_num += len(picked_apples)

        # 接到的苹果消失
        for picked_apple in picked_apples:
            picked_apple.kill()

        apple_sound.set_volume(1.0)
        if picked_apples:
            apple_sound.set_volume(0.2)
            apple_sound.play()


# 苹果类
class Apple(pygame.sprite.Sprite):
    def __init__(self, app_surface, apple_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = app_surface
        self.rect = self.image.get_rect()
        self.rect.topleft = apple_pos
        self.speed = 1

    def update(self):
        global START_TIME
        if START_TIME is None:
            START_TIME = time.time()
        self.rect.top += (self.speed * (1 + (time.time() - START_TIME) / 40))
        if self.rect.top > SCREEN_HEIGHT:
            # 苹果落地游戏结束
            global OVER_FLAG
            OVER_FLAG = True
            self.kill()


# 炸弹类
class Bomb(pygame.sprite.Sprite):
    def __init__(self, bomb1_surface, bomb_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = bomb1_surface
        self.rect = self.image.get_rect()
        self.rect.topleft = bomb_pos
        self.speed = 1

    def update(self):
        global START_TIME
        if START_TIME is None:
            START_TIME = time.time()
        self.rect.top += (self.speed * (1 + (time.time() - START_TIME) / 40))
        if self.rect.top > SCREEN_HEIGHT:
            # 炸弹落地消失
            self.kill()


# # 初始化游戏

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("接苹果")

# 载入图片
background_surface = pygame.image.load(BACKGROUND_IMAGE_PATH).convert()
background_surface2 = pygame.image.load(BACKGROUND_IMAGE_PATH2).convert()
background_surface3 = pygame.image.load(BACKGROUND_IMAGE_PATH3).convert_alpha()
monkey_surface = pygame.image.load(MONKEY_IMAGE_PATH).convert_alpha()
apple_surface = pygame.image.load(APPLE_IMAGE_PATH).convert_alpha()
bomb_surface1 = pygame.image.load(BOMB_IMAGE_PATH).convert_alpha()
# 创建猴子
monkey = Monkey(monkey_surface, (200, 500))
# 创建苹果组
apple_group = pygame.sprite.Group()
bomb_group = pygame.sprite.Group()
# 分数字体
score_font = pygame.font.SysFont("arial", 40)

game_mode = None
score = None
# 主菜单
def main_menu():
    global game_mode
    font = pygame.font.SysFont("Georgia", 40, bold=1)
    start_text_surface = font.render("Press 'B' to Begin", True, (255, 255, 255))
    mode_text_surface = font.render("Press 'M' to Choose Mode", True, (255, 255, 255))
    while True:
        screen.blit(background_surface, (0, 0))
        screen.blit(start_text_surface, (200, 270))
        screen.blit(mode_text_surface, (160, 320))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_b:
                    return
                elif event.key == K_m:
                    return choose_game_mode()


def choose_game_mode():
    font = pygame.font.SysFont("Georgia", 50)
    easy_text_surface = font.render("Press 'E'  for Easy Mode", True, (255, 255, 255))
    hard_text_surface = font.render("Press 'H' for Hard Mode", True, (255, 255, 255))
    while True:
        screen.blit(background_surface, (0, 0))
        screen.blit(easy_text_surface, (120, 270))
        screen.blit(hard_text_surface, (120, 320))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_e:
                    return hard_mode()
                elif event.key == K_h:
                    return easy()
# 打印文本
def print_text1(font2, x, y, text, color=(255, 255, 255)):
    img_text = font2.render(text, True, color)
    screen2 = pygame.display.get_surface()
    screen2.blit(img_text, (x, y))

# 精灵类
class MySprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = None  # 添加image属性
        self.rect = None
        self.master_image = None
        self.frame = 0
        self.old_frame = -1
        self.frame_width = 1
        self.frame_height = 1
        self.first_frame = 0
        self.last_frame = 0
        self.columns = 1
        self.last_time = 0
        self.direction = 0
        self.velocity = Point(0.0, 0.0)

    def _getx(self):
        return self.rect.x

    def _setx(self, value):
        self.rect.x = value

    X = property(_getx, _setx)

    def _gety(self):
        return self.rect.y

    def _sety(self, value):
        self.rect.y = value

    Y = property(_gety, _sety)

    def _getpos(self):
        return self.rect.topleft

    def _setpos(self, pos):
        self.rect.topleft = pos

    position = property(_getpos, _setpos)

    def load(self, filename, width, height, columns):
        self.master_image = pygame.image.load(filename).convert_alpha()
        self.frame_width = width
        self.frame_height = height
        self.rect = Rect(0, 0, width, height)
        self.columns = columns
        rect = self.master_image.get_rect()
        self.last_frame = (rect.width // width) * (rect.height // height) - 1
        self.image = self.master_image.subsurface(Rect(0, 0, min(width, self.master_image.get_width()),
                                                       min(height, self.master_image.get_height()))).copy()

    #  设置image属性

    def update(self, current_time, rate=30):
        if current_time > self.last_time + rate:
            self.frame += 1
            if self.frame > self.last_frame:
                self.frame = self.first_frame
            self.last_time = current_time

        if self.frame != self.old_frame:
            frame_x = (self.frame % self.columns) * self.frame_width
            frame_y = (self.frame // self.columns) * self.frame_height

            frame_rect = Rect(frame_x, frame_y, self.frame_width, self.frame_height)
            image_rect = self.master_image.get_rect()

            if frame_rect.right > image_rect.width or frame_rect.bottom > image_rect.height:
                frame_rect = image_rect

            self.image = self.master_image.subsurface(frame_rect).copy()
            self.old_frame = self.frame

# 点类
class Point(object):
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def getx(self):
        return self.__x

    def setx(self, x):
        self.__x = x

    x = property(getx, setx)

    def gety(self):
        return self.__y

    def sety(self, y):
        self.__y = y

    y = property(gety, sety)

    def __str__(self):
        return "{X:" + "{:.0f}".format(self.__x) + ",Y:" + "{:.0f}".format(self.__y) + "}"


# noinspection PyTypeChecker
def hard_mode():
    # 初始化pygame
    pygame.init()
    screen3 = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("接苹果")
    font = pygame.font.Font(None, 50)
    timer = pygame.time.Clock()

    # 创建精灵组
    player_group = pygame.sprite.Group()
    apple1_group = pygame.sprite.Group()

    # 初始化玩家精灵组
    player = MySprite()
    player.load("./images/player_animation.png", 96, 96, 8)
    player.position = 80, 500
    player.direction = 0
    player_group.add(player)

    # 初始化苹果精灵组
    for i in range(10):
        apple = MySprite()
        apple.load("./images/apple.png", 64, 64, 1)
        apple.position = random.randint(100, 700), random.randint(-200, -100)
        apple.velocity = Point(0, random.randint(2, 6))
        apple1_group.add(apple)

    game_over = False  # 控制游戏进程变量，初始化为false
    player_moving = False  # 控制小人移动变量，初始化为false
    score2 = 0  # 分数初始化为0
    high_score = 0  # 最高分

    # 定义游戏时间（秒）
    game_time = 60
    start_time = time.time()  # 保存当前时间

    # 初始化最高分
    try:
        with open("high_score3.txt", "r") as file:
            high_score = int(file.read())
    except FileNotFoundError:
        with open("high_score3.txt", "w") as file:
            file.write(str(high_score))

    def show_game_over_screen():
        image1 = pygame.image.load("./images/bg4.png")
        font1 = pygame.font.Font(None, 50)
        font2 = pygame.font.Font(None, 70)
        screen3.blit(image1, (0, 0))
        print_text1(font1, 295, 120, "Game Over", (0, 0, 0))  # 121行定义font属性4  游戏结束显示Game Over
        print_text1(font2, 300, 220, "Score: " + str(score2), (0, 0, 0))  # 游戏结束显示Score+分数
        print_text1(font1, 290, 355, "HighScore: " + str(high_score), (190, 0, 0))
        print_text1(font1, 320, 480, "ESC exits", (0, 0, 0))
        keys1 = pygame.key.get_pressed()
        if keys1[K_ESCAPE]:
            restart_game()
        pygame.display.update()

    # 加载图片
    image = pygame.image.load("./images/img.png")

    def show_game_over_screen1():
        screen3.blit(image, (0, 0))
        print_text1(font, 100, 200, "Congratulations on breaking the record", (139, 0, 0))
        print_text1(font, 100, 250, "Your score is: " + str(score2), (139, 0, 0))
        pygame.display.flip()

    while True:
        timer.tick(30)
        Ticks = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            restart_game()
        elif keys[K_UP] or keys[K_w]:
            player.direction = 0
            player_moving = True
        elif keys[K_RIGHT] or keys[K_d]:
            player.direction = 2
            player_moving = True
        elif keys[K_DOWN] or keys[K_s]:
            player.direction = 4
            player_moving = True
        elif keys[K_LEFT] or keys[K_a]:
            player.direction = 6
            player_moving = True
        else:
            player_moving = False

        if not game_over:
            player.first_frame = player.direction * player.columns
            player.last_frame = player.first_frame + player.columns - 1
            if player.frame < player.first_frame:
                player.frame = player.first_frame

            if not player_moving:
                player.frame = player.first_frame = player.last_frame
            else:
                player.velocity = Point(0.0, 0.0)
                if player.direction == 0:
                    player.velocity.y = -6
                elif player.direction == 2:
                    player.velocity.x = 6
                elif player.direction == 4:
                    player.velocity.y = 6
                elif player.direction == 6:
                    player.velocity.x = -6

            if player_moving:
                player.X += player.velocity.x
                player.Y += player.velocity.y
                if player.X < 0:
                    player.X = 0
                elif player.X > 700:
                    player.X = 700
                if player.Y < 0:
                    player.Y = 0
                elif player.Y > 500:
                    player.Y = 500

            player_group.update(Ticks, 60)

            for apple in apple1_group:
                apple.Y += apple.velocity.y
                if apple.Y > 600:
                    apple.X = random.randint(100, 700)
                    apple.Y = random.randint(-200, -100)

                if pygame.sprite.collide_rect_ratio(0.5)(player, apple):
                    apple_sound.play()
                    apple.X = random.randint(100, 700)
                    apple.Y = random.randint(-200, -100)
                    score2 += 1

            apple1_group.update(Ticks, 70)

            if time.time() - start_time > game_time:
                game_over = True

            screen3.blit(background_surface2, (0, 0))
            apple1_group.draw(screen3)
            player_group.draw(screen3)
            print_text1(font, 0, 0, "Score: " + str(score2), (54, 54, 54))
            print_text1(font, 650, 0, "Time: " + str(int(game_time - (time.time() - start_time))), (54, 54, 54))
        else:
            if high_score < score2:
                high_score = score2
                with open("high_score3.txt", "w") as file:
                    file.write(str(high_score))
                show_game_over_screen1()
            else:
                show_game_over_screen()  # 游戏结束，绘制游戏页面
            time.sleep(3)
            restart_game()

        pygame.display.update()


# 重新开始游戏函数
def restart_game():
    global MOVE_STATUS, OVER_FLAG, START_TIME, offset, ticks, score
    MOVE_STATUS = False
    OVER_FLAG = False
    START_TIME = None
    offset = {pygame.K_LEFT: 0, pygame.K_RIGHT: 0, pygame.K_UP: 0, pygame.K_DOWN: 0,
              pygame.K_w: 0, pygame.K_a: 0, pygame.K_s: 0, pygame.K_d: 0}  # 重置初始位置
    apple_group.empty()  # 清空苹果组
    bomb_group.empty()  # 清空炸弹组
    pygame.mixer.music.stop()  # 停止音乐
    pygame.mixer.music.play(-1)  # 重新播放音乐
    main()
    ticks = 0
    score = 0
    monkey.apple_num = 0
    score_surface = score_font.render(str(monkey.apple_num), True, (255, 255, 255))
    screen.blit(score_surface, (620, 10))
    # 更新屏幕
    pygame.display.update()


# 从文件中读取最高分数
def load_high_score():
    try:
        with open('high_score.txt', 'r') as f:
            high_score = int(f.read())
    except FileNotFoundError:
        # 处理文件不存在的情况
        high_score = 0
    except ValueError:
        # 处理文件内容无法转换为整数的情况
        high_score = 0
    else:
        # 如果没有发生异常，则关闭文件
        f.close()
    return high_score

# 将最高分数保存到文件中
def save_high_score(high_score):
    with open('high_score.txt', 'w') as f:
        f.write(str(high_score))


# noinspection DuplicatedCode,PyTypeChecker
def easy():
    pygame.init()
    screen1 = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.mixer.music.load("./images/music1.mp3")

    # 播放音乐
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    # 初始化字体
    score1_font = pygame.font.SysFont("arial", 70)
    over_font = pygame.font.SysFont("arial", 40)
    high_score_font = pygame.font.SysFont("arial", 40)
    monkey1 = Monkey(monkey_surface, (200, 500))
    monkey1.apple_num = 0
    ticks_2 = 0
    high_score = load_high_score()
    # 主循环
    while True:
        if OVER_FLAG:
            break

        # 控制游戏最大帧率
        clock.tick(FRAME_RATE)

        # 绘制背景
        screen.blit(background_surface, (0, 0))
        if ticks_2 >= ANIMATE_CYCLE:
            ticks_2 = 0

        if ticks_2 % 40 == 0 and len(apple_group) <= 15:
            apple = Apple(apple_surface,
                          [randint(0, SCREEN_WIDTH - apple_surface.get_width()), -apple_surface.get_height()])
            while pygame.sprite.spritecollide(apple, bomb_group, False):
                apple.rect.top = -apple_surface.get_height()
                apple.rect.left = randint(0, SCREEN_WIDTH - apple_surface.get_width())
            apple_group.add(apple)

        if len(apple_group) >= 15 and ticks_2 % 30 == 0 and len(bomb_group) < 3:
            bomb = Bomb(bomb_surface1,
                        [randint(0, SCREEN_WIDTH - bomb_surface1.get_width()), -bomb_surface1.get_height()])
            while pygame.sprite.spritecollide(bomb, apple_group, False):
                bomb.rect.top = -bomb_surface1.get_height()
                bomb.rect.left = randint(0, SCREEN_WIDTH - bomb_surface1.get_width())
            bomb_group.add(bomb)

        # 控制苹果
        apple_group.update()
        bomb_group.update()
        # 绘制苹果组
        apple_group.draw(screen)
        # 绘制炸弹组
        bomb_group.draw(screen)

        # 绘制猴子
        screen.blit(monkey_surface, monkey1.rect)
        ticks_2 += 1

        # 接苹果
        monkey1.picking_apple(apple_group)
        monkey1.picking_bomb(bomb_group)
        # 更新分数
        score_surface = score_font.render(str(monkey1.apple_num), True, (255, 255, 255))
        screen.blit(score_surface, (640, 10))
        if high_score > monkey1.apple_num:
            high_score_surface = high_score_font.render("Highest: " + str(high_score), True, (255, 255, 255))
        else:
            high_score = monkey1.apple_num
            high_score_surface = high_score_font.render("Highest: " + str(high_score), True, (255, 255, 255))
            save_high_score(high_score)
        # 绘制最高分数
        screen.blit(high_score_surface, (10, 10))

        # 更新屏幕
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # 控制方向
            if event.type == pygame.KEYDOWN:
                if event.key in offset:
                    if event.key == pygame.K_UP:
                        offset[event.key] = 80
                    else:
                        offset[event.key] = monkey1.speed
            elif event.type == pygame.KEYUP:
                if event.key in offset:
                    offset[event.key] = 0
        monkey1.move(offset)

    # 游戏主循环
    while True:
        # 按钮字体
        button_font = pygame.font.SysFont("Georgia", 40)
        # 重新开始按钮
        restart_surface = button_font.render("Restart", True, (255, 255, 255))
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 检查用户是否点击重新启动按钮
                if restart_rect.collidepoint(event.pos):
                    # 重启游戏
                    restart_game()
                    apple_group.empty()
                    bomb_group.empty()
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.stop()
                    pygame.mixer.music.play(-1)
                    # 退出游戏
                    break

        high_score1_surface = high_score_font.render("Highest: " + str(high_score), True, (190, 0, 0))
        score1_surface = score1_font.render("Score: " + str(monkey1.apple_num), True, (0, 0, 0))
        over1_surface = over_font.render("Game Over!", True, (0, 0, 0))
        # 游戏结束退出界面
        screen1.blit(background_surface3, (0, 0))
        screen1.blit(score1_surface, (285, 200))
        screen1.blit(over1_surface, (305, 105))
        screen1.blit(high_score1_surface, (300, 350))
        screen1.blit(restart_surface, restart_rect)
        pygame.display.flip()


# 游戏主函数
# noinspection DuplicatedCode,PyTypeChecker
def main():
    pygame.init()
    screen1 = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.mixer.music.load("./images/music1.mp3")

    # 播放音乐
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    # 初始化字体
    score1_font = pygame.font.SysFont("arial", 70)
    over_font = pygame.font.SysFont("arial", 40)
    high_score_font = pygame.font.SysFont("arial", 40)
    monkey1 = Monkey(monkey_surface, (200, 500))
    monkey1.apple_num = 0
    main_menu()
    ticks_1 = 0
    high_score = load_high_score()
    # 主循环
    while True:
        if OVER_FLAG:
            break

        # 控制游戏最大帧率
        clock.tick(FRAME_RATE)

        # 绘制背景
        screen.blit(background_surface, (0, 0))
        if ticks_1 >= ANIMATE_CYCLE:
            ticks_1 = 0

        if ticks_1 % 40 == 0 and len(apple_group) <= 15:
            apple = Apple(apple_surface,
                          [randint(0, SCREEN_WIDTH - apple_surface.get_width()), -apple_surface.get_height()])
            while pygame.sprite.spritecollide(apple, bomb_group, False):
                apple.rect.top = -apple_surface.get_height()
                apple.rect.left = randint(0, SCREEN_WIDTH - apple_surface.get_width())
            apple_group.add(apple)

        if len(apple_group) >= 15 and ticks_1 % 30 == 0 and len(bomb_group) < 3:
            bomb = Bomb(bomb_surface1,
                        [randint(0, SCREEN_WIDTH - bomb_surface1.get_width()), -bomb_surface1.get_height()])
            while pygame.sprite.spritecollide(bomb, apple_group, False):
                bomb.rect.top = -bomb_surface1.get_height()
                bomb.rect.left = randint(0, SCREEN_WIDTH - bomb_surface1.get_width())
            bomb_group.add(bomb)

        # 控制苹果
        apple_group.update()
        bomb_group.update()
        # 绘制苹果组
        apple_group.draw(screen)
        # 绘制炸弹组
        bomb_group.draw(screen)

        # 绘制猴子
        screen.blit(monkey_surface, monkey1.rect)
        ticks_1 += 1

        # 接苹果
        monkey1.picking_apple(apple_group)
        monkey1.picking_bomb(bomb_group)
        # 更新分数
        score_surface = score_font.render(str(monkey1.apple_num), True, (255, 255, 255))
        screen.blit(score_surface, (640, 10))
        if high_score > monkey1.apple_num:
            high_score_surface = high_score_font.render("Highest: " + str(high_score), True, (255, 255, 255))
        else:
            high_score = monkey1.apple_num
            high_score_surface = high_score_font.render("Highest: " + str(high_score), True, (255, 255, 255))
            save_high_score(high_score)
        # 绘制最高分数
        screen.blit(high_score_surface, (10, 10))

        # 更新屏幕
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # 控制方向
            if event.type == pygame.KEYDOWN:
                if event.key in offset:
                    if event.key == pygame.K_UP:
                        offset[event.key] = 80
                    else:
                        offset[event.key] = monkey1.speed
            elif event.type == pygame.KEYUP:
                if event.key in offset:
                    offset[event.key] = 0
        monkey1.move(offset)

    # 游戏主循环
    while True:
        # 按钮字体
        button_font = pygame.font.SysFont("Georgia", 40)
        # 重新开始按钮
        restart_surface = button_font.render("Restart", True, (255, 255, 255))
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 检查用户是否点击重新启动按钮
                if restart_rect.collidepoint(event.pos):
                    # 重启游戏
                    restart_game()
                    apple_group.empty()
                    bomb_group.empty()
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.lostop()
                    pygame.mixer.music.play(-1)
                    # 退出游戏
                    break

        high_score1_surface = high_score_font.render("Highest: " + str(high_score), True, (190, 0, 0))
        score1_surface = score1_font.render("Score: " + str(monkey1.apple_num), True, (0, 0, 0))
        over1_surface = over_font.render("Game Over!", True, (0, 0, 0))
        # 游戏结束退出界面
        screen1.blit(background_surface3, (0, 0))
        screen1.blit(score1_surface, (285, 200))
        screen1.blit(over1_surface, (305, 105))
        screen1.blit(high_score1_surface, (300, 350))
        screen1.blit(restart_surface, restart_rect)
        pygame.display.flip()


if __name__ == '__main__':
    main()
