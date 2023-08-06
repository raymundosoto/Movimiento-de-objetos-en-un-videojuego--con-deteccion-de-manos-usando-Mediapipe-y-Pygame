import pygame
import os
import cv2
import mediapipe as mp

# Dimensiones de la ventana del juego y la ventana de la detección de manos
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500

# Velocidad del planeta
PLANET_SPEED = 5

# Inicialización de Pygame
pygame.init()

# Creación de la ventana del juego
game_screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Planeta que mueve con la mano")

pygame.mixer.init()
background_sound_path = os.path.join("sound_planet.mp3")
background_sound = pygame.mixer.Sound(background_sound_path)
background_sound.set_volume(0.5)  # Set the volume level (0.0 to 1.0)

# Reproducir el sonido en bucle
background_sound.play(loops=-1)

# Cargar la imagen de fondo del juego
background_image_path = os.path.join("space.png")
background_img = pygame.image.load(background_image_path)
background_img = pygame.transform.scale(background_img, (WINDOW_WIDTH, WINDOW_HEIGHT))

# Cargar la imagen del planeta
planet_image_path = os.path.join("planeta_chico.png")
planet_img = pygame.image.load(planet_image_path)
planet_img = pygame.transform.scale(planet_img, (100, 100))  # Ajustar el tamaño del planeta

# Obtener las dimensiones del planeta
planet_width, planet_height = planet_img.get_rect().size

# Posición inicial del planeta
planet_x = WINDOW_WIDTH // 2 - planet_width // 2
planet_y = WINDOW_HEIGHT // 2 - planet_height // 2

# Dirección inicial del movimiento del planeta
planet_dx = PLANET_SPEED
planet_dy = PLANET_SPEED

# Inicialización de Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)

# Bucle principal del juego
running = True
capture = cv2.VideoCapture(0)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Leer el fotograma de la cámara
    ret, image = capture.read()
    if not ret:
        continue

    # Convertir el fotograma de BGR a RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    # Obtener las coordenadas de la mano
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get the size of the hand tracking window
            image_height, image_width, _ = image.shape

            # Draw circles for all the landmarks in red
            for landmark in hand_landmarks.landmark:
                x = int(landmark.x * image_width)
                y = int(landmark.y * image_height)
                cv2.circle(image, (x, y), 5, (0, 0, 255), -1)

            # Calculate the average coordinates of all the landmarks
            total_x = 0
            total_y = 0
            num_landmarks = len(hand_landmarks.landmark)
            for landmark in hand_landmarks.landmark:
                total_x += landmark.x
                total_y += landmark.y

            average_x = total_x / num_landmarks
            average_y = total_y / num_landmarks

            # Dibujar un círculo en la posición del centro de la mano (verde)
            center_x = int(average_x * image_width)
            center_y = int(average_y * image_height)
            cv2.circle(image, (center_x, center_y), 10, (0, 255, 0), -1)

            # Mostrar la coordenada del centro de la mano que mueve el planeta en la ventana de detección de manos
            cv2.putText(image, f"Coordenadas del planeta: ({center_x}, {center_y})", (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Mapear las coordenadas del centro de la mano al movimiento del planeta
            planet_x = int((center_x / image_width) * WINDOW_WIDTH - planet_width // 2)
            planet_y = int((center_y / image_height) * WINDOW_HEIGHT - planet_height // 2)

    # Mover el planeta
    planet_x += planet_dx
    planet_y += planet_dy

    # Rebote en los bordes horizontales
    if planet_x <= 0 or planet_x + planet_width >= WINDOW_WIDTH:
        planet_dx = -planet_dx

    # Rebote en los bordes verticales
    if planet_y <= 0 or planet_y + planet_height >= WINDOW_HEIGHT:
        planet_dy = -planet_dy

    # Dibujar el fondo y el planeta en la pantalla del juego
    game_screen.blit(background_img, (0, 0))
    game_screen.blit(planet_img, (planet_x, planet_y))

    # Mostrar el fotograma de la cámara en la ventana de detección de manos
    cv2.imshow("Seguimientos de manos", image)

    # Actualizar la pantalla del juego
    pygame.display.update()

    # Controlar la velocidad del juego
    pygame.time.delay(30)

    # Salir del juego al presionar 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
capture.release()
cv2.destroyAllWindows()
pygame.quit()