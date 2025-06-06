import pygame
import random
import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Finger Ninja Game")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Fruit class
class Fruit:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = -50
        self.radius = 30
        self.speed = random.randint(4, 7)
        self.color = random.choice([(255, 0, 0), (0, 255, 0), (255, 255, 0)])

    def move(self):
        self.y += self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)

    def is_cut(self, fx, fy):
        return (self.x - fx) ** 2 + (self.y - fy) ** 2 <= self.radius ** 2

# Count number of open fingers
def count_fingers(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    dips = [3, 6, 10, 14, 18]
    count = 0
    for tip, dip in zip(tips, dips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[dip].y:
            count += 1
    return count

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
cap = cv2.VideoCapture(0)

# Game state
def reset_game():
    return [], 0, True

fruits, score, running = reset_game()
game_active = True

while True:
    screen.fill((30, 30, 30))
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    fx, fy = None, None
    finger_count = 0

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            h, w, _ = frame.shape
            finger_tip = hand_landmarks.landmark[8]
            fx, fy = int(finger_tip.x * WIDTH), int(finger_tip.y * HEIGHT)
            pygame.draw.circle(screen, (0, 255, 255), (fx, fy), 10)
            finger_count = count_fingers(hand_landmarks)

    # 🛑 Stop condition: 5 fingers
    if game_active and finger_count == 5:
        game_active = False

    # 🔁 Restart condition: 2 fingers
    if not game_active and finger_count == 2:
        fruits, score, game_active = reset_game()
        continue

    if game_active:
        # Add new fruit randomly
        if random.randint(1, 20) == 1:
            fruits.append(Fruit())

        for fruit in fruits[:]:
            fruit.move()
            fruit.draw(screen)

            if fx and fy and fruit.is_cut(fx, fy):
                fruits.remove(fruit)
                score += 1
            elif fruit.y > HEIGHT:
                fruits.remove(fruit)

        text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(text, (10, 10))
    else:
        # Game over screen
        over_text = font.render("✋ Game Over! Show 2 fingers to restart", True, (255, 255, 255))
        score_text = font.render(f"Your Score: {score}", True, (255, 255, 0))
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 10))

    # Check for quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            exit()

    pygame.display.flip()
    clock.tick(30)
