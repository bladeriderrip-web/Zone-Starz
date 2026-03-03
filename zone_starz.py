# ------- Import and Initialize Pygame ------ 
import pygame
import random
import time
pygame.init()
pygame.mixer.init()


# ----------- Setting up Screen ------
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
game_state = "start_menu"
player_point_font = pygame.font.SysFont ("arial", 30)


def draw_start_menu():
    screen.fill((0, 0, 0))
    screen.blit(menuimage,(0,0))
    pygame.display.update()

def draw_game_over_screen():
    screen.fill((0, 0, 0))
    if winner == 1:
        screen.blit(player1_win_screen, (0,0))
    elif winner == 2:
        screen.blit(player2_win_screen, (0,0))
        pygame.display.update()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption('Zone Starz')
controlmenu = pygame.image.load("controlmenu.png").convert_alpha()
menuimage = pygame.image.load("mainmenuscreen.jpg").convert_alpha()
player1_win_screen = pygame.image.load("player 1 wins.jpg")
player2_win_screen = pygame.image.load("red win screen.jpg")
translucent_surface = pygame.Surface ((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

class Player:
    def __init__(self, x, y, playernumber):
        self.playernumber = playernumber
        self.player_rect = pygame.Rect(x, y, 50, 50)
        self.hitbox = pygame.Rect(x, y, 50, 50)

        # Load idle and attack sprites
        if self.playernumber == 1:
            self.idle_image = pygame.image.load("player_1_idle_sprite.png").convert_alpha()  # Single image
            self.attack_sprite_sheet = pygame.image.load("player_1_shoving_sprite.png").convert_alpha()
        elif self.playernumber == 2:
            self.idle_image = pygame.image.load("player_2_idle_sprite.png").convert_alpha()  # Single image
            self.attack_sprite_sheet = pygame.image.load("player_2_shoving_sprite.png").convert_alpha()
        
        # Split attack sprite sheet into frames
        self.attack_frames = self.load_frames(self.attack_sprite_sheet, 2, 3)  # 2 columns, 3 rows
        
        self.current_frame = 0
        self.animation_timer = 0
        self.frame_duration = 100  # Duration of each frame in ms

        self.direction = "down"
        self.rotation_angle = 180
        self.last_shove_time = 0
        self.shove_cooldown = 1.5
        self.is_attacking = False  # Tracks if the player is attacking
        self.attack_duration = 500  # Duration of the attack animation in ms
        self.attack_start_time = 0  # Track when the attack starts
        
        # Knockback attributes
        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_decay = 0.8

    def load_frames(self, sprite_sheet, cols, rows):
        """ Split the sprite sheet into individual frames. """
        frame_width = sprite_sheet.get_width() // cols
        frame_height = sprite_sheet.get_height() // rows
        frames = []
        for row in range(rows):
            for col in range(cols):
                frame = sprite_sheet.subsurface(pygame.Rect(
                    col * frame_width, row * frame_height, frame_width, frame_height))
                frames.append(frame)
        return frames

    def draw_player(self, screen):
        if self.is_attacking:
            # Animate attack frames
            self.animate()
            rotated_frame = pygame.transform.rotate(self.attack_frames[self.current_frame], self.rotation_angle)

            # Check if the attack animation duration has ended
            if pygame.time.get_ticks() - self.attack_start_time >= self.attack_duration:
                self.is_attacking = False  # End attack
                self.current_frame = 0  # Reset animation frame
        else:
        # Display idle sprite directly after attack ends
            rotated_frame = pygame.transform.rotate(self.idle_image, self.rotation_angle)

    # Draw the current frame
        rotated_rect = rotated_frame.get_rect(center=self.player_rect.center)
        screen.blit(rotated_frame, rotated_rect.topleft)

    def animate(self):
        """ Cycle through attack animation frames based on a timer. """
        self.animation_timer += clock.get_time()
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.attack_frames)
    def move(self):
        # Player movement controls
        key = pygame.key.get_pressed()
        if self.playernumber == 1:
            if key[pygame.K_w]:
                self.player_rect.move_ip(0, -4)
                self.direction = "up"
                self.rotation_angle = 0
            if key[pygame.K_s]:
                self.player_rect.move_ip(0, 4)
                self.direction = "down"
                self.rotation_angle = 180
            if key[pygame.K_a]:
                self.player_rect.move_ip(-4, 0)
                self.direction = "left"
                self.rotation_angle = 90
            if key[pygame.K_d]:
                self.player_rect.move_ip(4, 0)
                self.direction = "right"
                self.rotation_angle = -90

        if self.playernumber == 2:
            if key[pygame.K_UP]:
                self.player_rect.move_ip(0, -4)
                self.direction = "up"
                self.rotation_angle = 0
            if key[pygame.K_DOWN]:
                self.player_rect.move_ip(0, 4)
                self.direction = "down"
                self.rotation_angle = 180
            if key[pygame.K_LEFT]:
                self.player_rect.move_ip(-4, 0)
                self.direction = "left"
                self.rotation_angle = 90
            if key[pygame.K_RIGHT]:
                self.player_rect.move_ip(4, 0)
                self.direction = "right"
                self.rotation_angle = -90

        # Apply knockback
        self.player_rect.move_ip(self.knockback_x, self.knockback_y)
        self.knockback_x *= self.knockback_decay
        self.knockback_y *= self.knockback_decay

        # Stop knockback if velocity is negligible
        if abs(self.knockback_x) < 0.1:
            self.knockback_x = 0
        if abs(self.knockback_y) < 0.1:
            self.knockback_y = 0

        # Clamp position to stay within screen boundaries
        self.player_rect.clamp_ip(pygame.Rect(0, 40, SCREEN_WIDTH, SCREEN_HEIGHT - 40))
        self.hitbox.topleft = self.player_rect.topleft

    def attack(self, screen, opponent):
        current_time = pygame.time.get_ticks() / 1000
        key = pygame.key.get_pressed()
        shove_sound = pygame.mixer.Sound("shove_sfx.wav")
        shove_hitsfx = pygame.mixer.Sound("shove_hitsound.wav")

        # Define shove hitbox initially
        shove_hitbox = self.player_rect.copy()
        if self.direction == "up":
            shove_hitbox.move_ip(0, -shove_hitbox.height)
        elif self.direction == "down":
            shove_hitbox.move_ip(0, shove_hitbox.height)
        elif self.direction == "left":
            shove_hitbox.move_ip(-shove_hitbox.width, 0)
        elif self.direction == "right":
            shove_hitbox.move_ip(shove_hitbox.width, 0)
        shove_hitbox.inflate_ip(20, 20)

        if (self.playernumber == 1 and key[pygame.K_g]) or (self.playernumber == 2 and key[pygame.K_KP0]):
            if current_time - self.last_shove_time >= self.shove_cooldown:
                self.last_shove_time = current_time
                self.is_attacking = True
                self.attack_start_time = pygame.time.get_ticks()
                shove_sound.play()

            # Apply knockback to opponent if attack happens
            if shove_hitbox.colliderect(opponent.hitbox):
                push_distance = 80
                if self.direction == "up":
                    opponent.knockback_y = -push_distance
                elif self.direction == "down":
                    opponent.knockback_y = push_distance
                elif self.direction == "left":
                    opponent.knockback_x = -push_distance
                elif self.direction == "right":
                    opponent.knockback_x = push_distance
                shove_hitsfx.play()





player_1 = Player(50, 200, 1)
player_2 = Player(1800, 200, 2)
zone_x = random.randint(0, 1520)
zone_y = random.randint(0, 680)
zone_width = 400
zone_height = 400
zone = pygame.Rect(zone_x, zone_y, 400, 400)
map_background = pygame.image.load("Zone Starz Map Image.png").convert_alpha()
player_1_score = 0
player_1_in_zone = False
player_1_zone_start_time = None
player_2_score = 0
player_2_in_zone = False
player_2_zone_start_time = None
channel = pygame.mixer.Channel(0)
title_screen_music = pygame.mixer.Sound("title_screen_background_music.wav")
channel.set_volume(0.25)
title_screen_music_play = False
channel1 = pygame.mixer.Channel(1)
game_background_music = pygame.mixer.Sound("game_background_music.wav")
channel1.set_volume(0.25)
game_music_play = False
point_notification = pygame.mixer.Sound("point_notification.mp3")
zone_notification = pygame.mixer.Sound("zone_enter_notification.wav")
zone_notification_play = False
zone_change_interval = 12  # Time in seconds for the zone to move
last_zone_change_time = time.time()  # Track the last time the zone was updated
winner = None

# ----- Game Loop -----
GOLD = (219, 172, 52, 75)
run = True
clock = pygame.time.Clock()

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if game_state == "start_menu":
        draw_start_menu()
        if title_screen_music_play == False:
            channel.play(title_screen_music, loops=-1)
            title_screen_music_play = True
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if channel.get_busy() == True:
                channel.stop()
                title_screen_music_play = False
            game_music_play = False
            game_state = "game"
            game_over = False
        player_1.player_rect.topleft = (50, 200)
        player_2.player_rect.topleft = (1800, 200)

        if keys[pygame.K_c]:
            game_state = "control_menu"

    elif game_state == "game_over":
        draw_game_over_screen()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_state = "start_menu"
            winner = None
        if keys[pygame.K_q]:
            run = False

    elif game_state == "control_menu":
        screen.blit(controlmenu, (0,0))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_state = "start_menu"

    elif game_state == "game":

        # Clear the screen
        screen.fill((0, 0, 0))
        translucent_surface.fill((0, 0, 0, 0))  # Clear the translucent surface

        # Check if it's time to move the zone
        current_time = time.time()
        if current_time - last_zone_change_time >= zone_change_interval:
            # Move the zone to a new random position
            zone_x = random.randint(0, (SCREEN_WIDTH - zone_width))  # Ensure the zone fits within the screen
            zone_y = random.randint(0, (SCREEN_HEIGHT - zone_height))
            zone = pygame.Rect(zone_x, zone_y, 400, 400)  # Update the zone rectangle
            last_zone_change_time = current_time  # Reset the timer

        # Draw the map and zone
        player2_point_counter = player_point_font.render(f'Player 2 Score: {player_2_score}', True, (255, 0, 0))
        player1_point_counter = player_point_font.render(f'Player 1 Score: {player_1_score}', True, (144,213,255))
        screen.blit(map_background, (0, 40))
        pygame.draw.rect(translucent_surface, GOLD, zone)  # Draw the zone
        screen.blit(translucent_surface, (0, 0))
        if game_music_play == False:
            channel1.play(game_background_music, loops = -1)
            game_music_play = True
        # Draw players
        player_1.draw_player(screen)
        player_2.draw_player(screen)
        player_1.move()
        player_2.move()
        player_1.attack(screen, player_2)
        player_2.attack(screen, player_1)

        # Handle collision detection and scoring
        if player_1.hitbox.colliderect(player_2.hitbox):
            dx = player_1.hitbox.centerx - player_2.hitbox.centerx
            dy = player_1.hitbox.centery - player_2.hitbox.centery

            if abs(dx) > abs(dy):  # Horizontal collision
                if dx > 0:
                    player_1.player_rect.move_ip(2, 0)
                    player_2.player_rect.move_ip(-2, 0)
                else:
                    player_1.player_rect.move_ip(-2, 0)
                    player_2.player_rect.move_ip(2, 0)
            else:  # Vertical collision
                if dy > 0:
                    player_1.player_rect.move_ip(0, 2)
                    player_2.player_rect.move_ip(0, -2)
                else:
                    player_1.player_rect.move_ip(0, -2)
                    player_2.player_rect.move_ip(0, 2)

        player_1.hitbox.topleft = player_1.player_rect.topleft
        player_2.hitbox.topleft = player_2.player_rect.topleft

        if player_1.hitbox.colliderect(zone):
            if player_1_in_zone == False:
                player_1_zone_start_time = time.time()
                if zone_notification_play == False:
                    zone_notification.play()
                    zone_notification_play = True
                player_1_in_zone = True

            player_1_time_ellapsed = time.time() - player_1_zone_start_time
            if player_1_time_ellapsed >= 3:
                player_1_score += 1
                point_notification.play()
                player1_point_counter = player_point_font.render(f'Player 1 Score: {player_1_score}', True, (0, 0, 0))
                player_1_in_zone = False

        else:
            player_1_in_zone = False
            player_1_zone_start_time = None
            zone_notification_play = False

        if player_2.hitbox.colliderect(zone):
            if player_2_in_zone == False:
                player_2_zone_start_time = time.time()
                if zone_notification_play == False:
                    zone_notification.play()
                    zone_notification_play = True
                player_2_in_zone = True

            player_2_time_ellapsed = time.time() - player_2_zone_start_time
            if player_2_time_ellapsed >= 3:
                point_notification.play()
                player_2_score += 1
                player2_point_counter = player_point_font.render(f'Player 2 Score: {player_2_score}', True, (0, 0, 0))
                player_2_in_zone = False

        else:
            player_2_in_zone = False
            player_2_zone_start_time = None
            zone_notification_play = False

        # Draw scores
        screen.blit(player1_point_counter, (310, 0))
        screen.blit(player2_point_counter, (1410, 0))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LALT] and keys[pygame.K_F4]:
            run = False

        if player_1_score >= 15:
            winner = 1
            game_state = "game_over"
            player_1_score = 0
            player_2_score = 0
            channel1.stop()
        
        elif player_2_score >= 15:
            winner = 2
            game_state = "game_over"
            player_1_score = 0
            player_2_score = 0
            channel1.stop()
            

    clock.tick(60)
    pygame.display.update()