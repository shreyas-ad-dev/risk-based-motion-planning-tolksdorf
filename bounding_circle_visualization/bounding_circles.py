import matplotlib
matplotlib.use('Agg')  # Non-interactive backend to avoid GUI warnings
import matplotlib.pyplot as plt
import numpy as np


def compute_bounding_circles(length, width, num_circles):
  """Computes center coordinates and minimum radius for n overlapping circles

  covering a rectangle of given length and width.
  """
  # Circle centers evenly spaced along the longitudinal (X) axis
  if num_circles == 1:
    x_centers = np.array([0.0])
    # Single circle must cover the full bounding box diagonal
    radius = np.sqrt((length / 2) ** 2 + (width / 2) ** 2)
  else:
    # Segment length covered by each circle's center interval
    segment_length = length / num_circles
    x_centers = np.linspace(
        -length / 2 + segment_length / 2,
        length / 2 - segment_length / 2,
        num_circles,
    )
    # Radius covers a sub-segment of length (length / num_circles) and full width
    radius = np.sqrt((segment_length / 2) ** 2 + (width / 2) ** 2)

  circles = [{'center': np.array([x, 0.0]), 'radius': radius} for x in x_centers]
  return circles


def plot_multi_circle_collision(num_circles=3):
  # 1. Define Ego Vehicle Geometry
  length, width = 4.5, 2.0
  ego_corners = np.array([
      [-length / 2, -width / 2],
      [length / 2, -width / 2],
      [length / 2, width / 2],
      [-length / 2, width / 2],
      [-length / 2, -width / 2],
  ])

  # 2. Compute Bounding Circles dynamically
  circles_ego = compute_bounding_circles(length, width, num_circles)

  # 3. Define Obstacle (Circle representation)
  obstacle_center = np.array([3.0, 1.5])
  r_obs = 0.8

  # Setup Plot
  fig, ax = plt.subplots(figsize=(10, 7))
  ax.set_aspect('equal')

  # Draw Vehicle Body
  ax.plot(
      ego_corners[:, 0],
      ego_corners[:, 1],
      'k--',
      linewidth=2,
      label='Ego Geometry',
  )
  ax.fill(ego_corners[:, 0], ego_corners[:, 1], color='gray', alpha=0.2)

  # Draw Obstacle
  obs_patch = plt.Circle(
      obstacle_center, r_obs, color='red', alpha=0.3, label='Obstacle Circle'
  )
  ax.add_patch(obs_patch)
  ax.plot(obstacle_center[0], obstacle_center[1], 'ro')

  # Color palette for ego circles
  colors = plt.cm.plasma(np.linspace(0.1, 0.8, num_circles))

  # 4. Check Collisions and Plot Circles
  any_collision = False

  # Variables to track the closest ego circle for annotation
  min_distance = float('inf')
  closest_circle_idx = -1
  closest_rho_bar = 0.0

  for i, circle in enumerate(circles_ego):
    c_i = circle['center']
    r_i = circle['radius']

    # Collision threshold distance: rho_bar = r_ego + r_obs
    rho_bar = r_i + r_obs
    d = np.linalg.norm(c_i - obstacle_center)
    is_collision = d <= rho_bar

    if d < min_distance:
      min_distance = d
      closest_circle_idx = i
      closest_rho_bar = rho_bar

    if is_collision:
      any_collision = True

    # Plot Bounding Circle
    circle_patch = plt.Circle(
        c_i,
        r_i,
        color=colors[i],
        fill=False,
        linewidth=2,
        label=f'Circle {i+1} (r={r_i:.2f}m)',
    )
    ax.add_patch(circle_patch)
    ax.plot(c_i[0], c_i[1], 'o', color=colors[i])

    # Draw connection line to obstacle
    line_style = 'r-' if is_collision else 'g--'
    ax.plot(
        [c_i[0], obstacle_center[0]],
        [c_i[1], obstacle_center[1]],
        line_style,
        alpha=0.5,
    )

  # 5. Annotate distance d and threshold rho_bar for the closest circle
  closest_center = circles_ego[closest_circle_idx]['center']
  ax.annotate(
      '',
      xy=obstacle_center,
      xytext=closest_center,
      arrowprops=dict(arrowstyle='<->', color='purple', lw=2),
  )

  mid_pt = (closest_center + obstacle_center) / 2
  r_ego_closest = circles_ego[closest_circle_idx]['radius']

  # Uses standard UTF-8 math characters to prevent Matplotlib layout/backend rendering errors
  annotation_text = (
      f'd = {min_distance:.2f} m\n'
      f'ρ_bar = r_ego + r_obs = {r_ego_closest:.2f} + {r_obs:.2f} ='
      f' {closest_rho_bar:.2f} m'
  )

  ax.text(
      mid_pt[0] - 0.4,
      mid_pt[1] + 0.25,
      annotation_text,
      color='purple',
      fontsize=10,
      fontweight='bold',
      bbox=dict(
          boxstyle='round,pad=0.4',
          facecolor='white',
          edgecolor='purple',
          alpha=0.85,
      ),
  )

  # Formatting & Labels
  status_text = 'COLLISION DETECTED' if any_collision else 'SAFE'
  status_color = 'red' if any_collision else 'green'

  ax.set_xlim(-3.5, 5.5)
  ax.set_ylim(-2.5, 3.5)
  ax.set_xlabel('X [m]')
  ax.set_ylabel('Y [m]')
  ax.set_title(
      f'Ego Approximation with N={num_circles} Circles | Status: {status_text}',
      fontsize=12,
      color=status_color,
      fontweight='bold',
  )
  ax.grid(True, linestyle=':', alpha=0.6)
  ax.legend(loc='upper left', fontsize=9, framealpha=0.9)

  plt.tight_layout()

  # Save figure to file
  output_filename = f'bounding_circles_n{num_circles}.png'
  plt.savefig(output_filename, dpi=300, bbox_inches='tight')
  print(f'Visualization saved as {output_filename}')


if __name__ == '__main__':
  # Change this parameter to try 1, 2, 3, 4, 5, etc.
  NUMBER_OF_CIRCLES = 3
  plot_multi_circle_collision(num_circles=NUMBER_OF_CIRCLES)
