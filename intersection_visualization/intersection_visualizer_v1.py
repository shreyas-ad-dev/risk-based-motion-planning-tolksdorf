import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider


def run_interactive_thesis_geometry():
  # Initial thesis parameters
  R_val = 1.2  # R = r_e + r_o
  L_o_val = 1.5  # L_o offset distance
  L_e_val = 2.0  # L_e ego reference offset along X-axis

  # Positions: Ego circle center at (L_e, 0), Object reference point at (3.5, 1.8)
  ego_center = np.array([L_e_val, 0.0])
  obj_ref_pos = np.array([3.5, 1.8])

  fig = plt.figure(figsize=(15, 8))

  # Canvas Subplots
  ax_plot = plt.subplot2grid((5, 3), (0, 0), rowspan=4, colspan=2)
  ax_plot.set_aspect('equal')
  ax_plot.set_xlim(-1, 6)
  ax_plot.set_ylim(-2, 4)
  ax_plot.grid(True, linestyle=':', alpha=0.5)

  # Table 3.1 Panel
  ax_table = plt.subplot2grid((5, 3), (0, 2), rowspan=4)
  ax_table.axis('off')

  # Slider Control Panel
  ax_slider_lo = plt.subplot2grid((5, 3), (4, 0), colspan=2)
  ax_slider_r = plt.subplot2grid((5, 3), (4, 2))

  slider_lo = Slider(
      ax_slider_lo, r'$L_o$', 0.2, 3.0, valinit=L_o_val, valstep=0.05
  )
  slider_r = Slider(
      ax_slider_r, r'$R = r_e + r_o$', 0.5, 2.5, valinit=R_val, valstep=0.05
  )

  # Visual Elements
  ego_patch = plt.Circle(
      ego_center, R_val, color='gold', fill=False, linewidth=2.5
  )
  ego_center_pt, = ax_plot.plot(
      ego_center[0], ego_center[1], 'ko', markersize=7
  )

  obj_ref_pt, = ax_plot.plot(
      obj_ref_pos[0], obj_ref_pos[1], 'ro', markersize=7
  )
  obj_circle_patch = plt.Circle(
      obj_ref_pos, L_o_val, color='gray', fill=False, linestyle='--'
  )

  # Angle arc visualizers for theta range
  line_rho_prime, = ax_plot.plot([], [], 'k--', linewidth=1.5)
  arc_theta_min, = ax_plot.plot([], [], 'm-', linewidth=2)
  arc_theta_max, = ax_plot.plot([], [], 'c-', linewidth=2)

  # Labels
  text_rho_prime = ax_plot.text(
      0, 0, r"$\rho'$", fontsize=12, fontweight='bold', color='purple'
  )
  text_le = ax_plot.text(
      L_e_val / 2, -0.3, r'$L_e$', fontsize=12, fontweight='bold'
  )

  ax_plot.add_patch(ego_patch)
  ax_plot.add_patch(obj_circle_patch)

  # Table 3.1 Setup
  table_data = [
      ['L_o > R', r"$\rho' \geq L_o - R$", r'$[\underline{\theta}, \bar{\theta}]$'],
      ['L_o > R', r"$\rho' < L_o - R$", r'$\emptyset$ (No Intersection)'],
      [
          r'$R \geq L_o$',
          r"$\rho' > R - L_o$",
          r'$[\underline{\theta}, \bar{\theta}]$',
      ],
      [r'$R \geq L_o$', r"$\rho' \leq R - L_o$", r'$[0, 2\pi)$ (Full Overlap)'],
  ]
  col_labels = ['Geometry', 'Radial Condition', 'Angle Interval']
  ui_table = ax_table.table(
      cellText=table_data,
      colLabels=col_labels,
      loc='center',
      cellLoc='center',
  )
  ui_table.scale(1.1, 2.3)
  ui_table.auto_set_font_size(False)
  ui_table.set_fontsize(8.5)

  drag_state = {'active': None}

  def update_geometry(val=None):
    nonlocal ego_center, obj_ref_pos

    R = slider_r.val
    L_o = slider_lo.val

    # Derived geometric parameters (Eq. 3.8 / 5.3)
    diff = obj_ref_pos - ego_center
    rho_prime = np.linalg.norm(diff)
    phi_prime = np.arctan2(diff[1], diff[0])

    # Geometry updates
    ego_patch.set_radius(R)
    ego_patch.center = ego_center
    ego_center_pt.set_data([ego_center[0]], [ego_center[1]])

    obj_ref_pt.set_data([obj_ref_pos[0]], [obj_ref_pos[1]])
    obj_circle_patch.center = obj_ref_pos
    obj_circle_patch.set_radius(L_o)

    line_rho_prime.set_data(
        [ego_center[0], obj_ref_pos[0]], [ego_center[1], obj_ref_pos[1]]
    )

    mid = (ego_center + obj_ref_pos) / 2
    text_rho_prime.set_position((mid[0] + 0.1, mid[1] + 0.1))
    text_le.set_position((ego_center[0] / 2, -0.3))

    # Calculate intersection angles theta_min, theta_max if valid
    cos_val = (rho_prime**2 + L_o**2 - R**2) / (2 * rho_prime * L_o + 1e-9)

    if abs(cos_val) <= 1.0:
      gamma = np.arccos(cos_val)
      theta_min = phi_prime - gamma
      theta_max = phi_prime + gamma

      # Plot boundary intersection directions
      arc_theta_min.set_data(
          [
              obj_ref_pos[0],
              obj_ref_pos[0] + L_o * np.cos(theta_min + np.pi),
          ],
          [
              obj_ref_pos[1],
              obj_ref_pos[1] + L_o * np.sin(theta_min + np.pi),
          ],
      )
      arc_theta_max.set_data(
          [
              obj_ref_pos[0],
              obj_ref_pos[0] + L_o * np.cos(theta_max + np.pi),
          ],
          [
              obj_ref_pos[1],
              obj_ref_pos[1] + L_o * np.sin(theta_max + np.pi),
          ],
      )
    else:
      arc_theta_min.set_data([], [])
      arc_theta_max.set_data([], [])

    # Evaluate Active Row in Table 3.1
    active_row = -1
    if L_o > R:
      if rho_prime >= (L_o - R):
        active_row = 0
      else:
        active_row = 1
    else:  # R >= L_o
      if rho_prime > (R - L_o):
        active_row = 2
      else:
        active_row = 3

    # Update Table Colors
    for (r_idx, c_idx), cell in ui_table.get_celld().items():
      if r_idx == 0:
        cell.set_facecolor('#d3d3d3')
      elif r_idx - 1 == active_row:
        cell.set_facecolor('#76ff03')  # Active condition
      else:
        cell.set_facecolor('white')

    # Update Legend
    ego_patch.set_label(f'Joint Radius (R = {R:.2f} m)')
    ego_center_pt.set_label(f'Ego Offset (L_e = {ego_center[0]:.2f} m)')
    obj_circle_patch.set_label(f'Object Offset Circle (L_o = {L_o:.2f} m)')
    obj_ref_pt.set_label(
        f"Obj Position (ρ' = {rho_prime:.2f} m, φ' ="
        f' {np.degrees(phi_prime):.1f}°)'
    )
    arc_theta_min.set_label(r'$\underline{\theta}$ bound')
    arc_theta_max.set_label(r'$\bar{\theta}$ bound')

    ax_plot.legend(loc='upper left', framealpha=0.9, fontsize=8.5)
    ax_plot.set_title(
        f'Base Case Geometry | Active Condition: Row {active_row + 1}',
        fontweight='bold',
    )
    fig.canvas.draw_idle()

  # Interaction Callbacks
  slider_lo.on_changed(update_geometry)
  slider_r.on_changed(update_geometry)

  def on_press(event):
    if event.inaxes != ax_plot:
      return
    m_pos = np.array([event.xdata, event.ydata])
    if np.linalg.norm(m_pos - ego_center) < 0.4:
      drag_state['active'] = 'ego'
    elif np.linalg.norm(m_pos - obj_ref_pos) < 0.4:
      drag_state['active'] = 'obj'

  def on_motion(event):
    if drag_state['active'] is None or event.inaxes != ax_plot:
      return
    new_pos = np.array([event.xdata, event.ydata])
    if drag_state['active'] == 'ego':
      ego_center[0] = new_pos[0]
      ego_center[1] = 0.0
    elif drag_state['active'] == 'obj':
      obj_ref_pos[0] = new_pos[0]
      obj_ref_pos[1] = new_pos[1]
    update_geometry()

  def on_release(event):
    drag_state['active'] = None

  fig.canvas.mpl_connect('button_press_event', on_press)
  fig.canvas.mpl_connect('motion_notify_event', on_motion)
  fig.canvas.mpl_connect('button_release_event', on_release)

  update_geometry()
  plt.tight_layout()
  plt.show()


if __name__ == '__main__':
  run_interactive_thesis_geometry()
