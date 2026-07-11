import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball in Spinning Hexagon")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Ball properties
ball_radius = 20
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_vel = [random.uniform(-5, 5), random.uniform(-5, 5)]
GRAVITY = 0.2
FRICTION = 0.99
BOUNCE = 0.9  # Energy loss on bounce

# Hexagon properties
hex_radius = 200
hex_center = [WIDTH // 2, HEIGHT // 2]
rotation_angle = 0
ROTATION_SPEED = 0.02  # radians per frame

# Clock for controlling framerate
clock = pygame.time.Clock()


def rotate_point(point, angle, center):
    """Rotate a point around a center by given angle in radians"""
    x, y = point[0] - center[0], point[1] - center[1]
    new_x = x * math.cos(angle) - y * math.sin(angle)
    new_y = x * math.sin(angle) + y * math.cos(angle)
    return [new_x + center[0], new_y + center[1]]


def get_hexagon_points(center, radius, angle):
    """Calculate the vertices of a rotating hexagon"""
    points = []
    for i in range(6):
        vertex_angle = angle + (i * math.pi / 3)
        x = center[0] + radius * math.cos(vertex_angle)
        y = center[1] + radius * math.sin(vertex_angle)
        points.append([x, y])
    return points


def line_intersection(p1, p2, p3, p4):
    """Find intersection point between two line segments"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:  # Lines are parallel
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        return [x1 + t * (x2 - x1), y1 + t * (y2 - y1)]
    return None


def reflect_velocity(vel, normal):
    """Calculate reflection of velocity given a normal vector"""
    dot = vel[0] * normal[0] + vel[1] * normal[1]
    return [
        vel[0] - 2 * dot * normal[0],
        vel[1] - 2 * dot * normal[1]
    ]


# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update rotation
    rotation_angle += ROTATION_SPEED

    # Apply gravity and friction
    ball_vel[1] += GRAVITY
    ball_vel[0] *= FRICTION
    ball_vel[1] *= FRICTION

    # Update ball position
    new_pos = [ball_pos[0] + ball_vel[0], ball_pos[1] + ball_vel[1]]

    # Get current hexagon points
    hex_points = get_hexagon_points(hex_center, hex_radius, rotation_angle)

    # Check collision with hexagon walls
    for i in range(6):
        p1 = hex_points[i]
        p2 = hex_points[(i + 1) % 6]

        # Check if ball path intersects wall
        intersection = line_intersection(
            ball_pos, new_pos,
            p1, p2
        )

        if intersection:
            # Calculate wall normal
            wall_vec = [p2[0] - p1[0], p2[1] - p1[1]]
            length = math.sqrt(wall_vec[0] ** 2 + wall_vec[1] ** 2)
            normal = [-wall_vec[1] / length, wall_vec[0] / length]

            # Reflect velocity
            ball_vel = reflect_velocity(ball_vel, normal)
            ball_vel[0] *= BOUNCE
            ball_vel[1] *= BOUNCE

            # Position ball at intersection point
            ball_pos = [intersection[0] - ball_vel[0], intersection[1] - ball_vel[1]]
            break
    else:
        # If no collision, update position normally
        ball_pos = new_pos

    # Clear screen
    screen.fill(BLACK)

    # Draw hexagon
    pygame.draw.polygon(screen, WHITE, hex_points, 2)

    # Draw ball
    pygame.draw.circle(screen, RED, [int(ball_pos[0]), int(ball_pos[1])], ball_radius)

    # Update display
    pygame.display.flip()

    # Control framerate
    clock.tick(60)

pygame.quit()