import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider


def run_interactive_thesis_geometry():
  # Initial thesis parameters
  r_e_val = 0.55
  r_o_val = 0.40
  L_o_val = 0.75
  L_e_val = 2.0

  ego_center = np.array([L_e_val, 0.0])
  obj_veh_center = np.array([2.6, 0.25])
  
  # Default angle for offset circle relative to object vehicle center
  phi_o_offset = np.pi * 7 / 6
  obj_circle_center = obj_veh_center + L_o_val * np.array([np.cos(phi_o_offset), np.sin(phi_o_offset)])

  fig = plt.figure(figsize=(16, 9))

  # Canvas Subplots
  ax_plot = plt.subplot2grid((7, 3), (0, 0), rowspan=5, colspan=2)
  ax_plot.set_aspect('equal')
  ax_plot.set_xlim(-1, 6)
  ax_plot.set_ylim(-2, 4)
  ax_plot.grid(True, linestyle=':', alpha=0.5)

  # Table Panel
  ax_table = plt.subplot2grid((7, 3), (0, 2), rowspan=5)
  ax_table.axis('off')

  # Slider Control Panel
  ax_slider_re = plt.subplot2grid((7, 3), (5, 0))
  ax_slider_ro = plt.subplot2grid((7, 3), (5, 1))
  ax_slider_lo = plt.subplot2grid((7, 3), (5, 2))

  ax_slider_rho = plt.subplot2grid((7, 3), (6, 0), colspan=3)

  slider_re = Slider(
      ax_slider_re, r'$r_e$', 0.1, 2.0, valinit=r_e_val, valstep=0.05
  )
  slider_ro = Slider(
      ax_slider_ro, r'$r_o$', 0.1, 2.0, valinit=r_o_val, valstep=0.05
  )
  slider_lo = Slider(
      ax_slider_lo, r'$L_o$', 0.2, 3.0, valinit=L_o_val, valstep=0.05
  )
  
  init_rho = np.linalg.norm(obj_veh_center - ego_center)
  slider_rho = Slider(
      ax_slider_rho, r"$\rho'$ (Ego Center to Obj Veh Center)", 0.1, 6.0, valinit=init_rho, valstep=0.05
  )

  # Yellow Circle: Ego vehicle radius r_e ONLY
  ego_patch = plt.Circle(
      ego_center, r_e_val, color='gold', fill=False, linewidth=2.5
  )
  ego_center_pt, = ax_plot.plot(
      ego_center[0], ego_center[1], 'ko', markersize=7
  )

  # Object Vehicle Center (Blue square)
  obj_veh_pt, = ax_plot.plot(
      obj_veh_center[0], obj_veh_center[1], 'bs', markersize=8
  )

  # Object Offset Circle Center (Red dot)
  obj_circle_pt, = ax_plot.plot(
      obj_circle_center[0], obj_circle_center[1], 'ro', markersize=7
  )
  
  # Object Circle: Radius r_o
  obj_circle_patch = plt.Circle(
      obj_circle_center,
      r_o_val,
      color='gray',
      fill=False,
      linestyle='--',
      linewidth=1.2,
  )

  # Line connecting Ego Center to Obj Vehicle Center (rho')
  line_rho_prime, = ax_plot.plot([], [], 'k--', linewidth=1.5)

  # Line connecting Obj Vehicle Center to Obj Circle Center (L_o)
  line_lo, = ax_plot.plot([], [], 'g:', linewidth=1.5)

  # Angle bound ray lines originating from Blue Square (Obj Vehicle Center)
  ray_theta_min, = ax_plot.plot([], [], 'm-', linewidth=2)
  ray_theta_max, = ax_plot.plot([], [], 'c-', linewidth=2)

  text_rho_prime = ax_plot.text(
      0, 0, r"$\rho'$", fontsize=12, fontweight='bold', color='purple'
  )
  text_lo = ax_plot.text(
      0, 0, r"$L_o$", fontsize=11, fontweight='bold', color='green'
  )
  text_le = ax_plot.text(
      L_e_val / 2, -0.3, r'$L_e$', fontsize=12, fontweight='bold'
  )

  ax_plot.add_patch(ego_patch)
  ax_plot.add_patch(obj_circle_patch)

  # Table Setup
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
  is_updating = False

  def update_geometry(val=None):
    nonlocal ego_center, obj_veh_center, obj_circle_center, is_updating

    if is_updating:
      return
    is_updating = True

    r_e = slider_re.val
    r_o = slider_ro.val
    R = r_e + r_o
    L_o = slider_lo.val

    # Distance rho' from ego_center (black dot) to obj_veh_center (blue square)
    diff_veh = obj_veh_center - ego_center
    current_rho = np.linalg.norm(diff_veh)
    
    # Absolute line-of-sight direction angle from Ego Center to Obj Vehicle Center
    phi_ego_to_veh = np.arctan2(diff_veh[1], diff_veh[0]) if current_rho > 1e-6 else 0.0

    target_rho = slider_rho.val

    # Handle Slider vs Drag updates for rho'
    if abs(target_rho - current_rho) > 1e-4 and drag_state['active'] is None:
      obj_veh_center = ego_center + target_rho * np.array([np.cos(phi_ego_to_veh), np.sin(phi_ego_to_veh)])
      rho_prime = target_rho
    else:
      rho_prime = current_rho
      slider_rho.eventson = False
      slider_rho.set_val(rho_prime)
      slider_rho.eventson = True

    # Maintain L_o offset relative to Obj Veh Center
    diff_lo = obj_circle_center - obj_veh_center
    dist_lo = np.linalg.norm(diff_lo)
    if dist_lo > 1e-6:
      dir_lo = diff_lo / dist_lo
      obj_circle_center = obj_veh_center + L_o * dir_lo
    else:
      obj_circle_center = obj_veh_center + np.array([L_o, 0.0])

    # Yellow Circle = r_e radius ONLY
    ego_patch.set_radius(r_e)
    ego_patch.center = ego_center
    ego_center_pt.set_data([ego_center[0]], [ego_center[1]])

    obj_veh_pt.set_data([obj_veh_center[0]], [obj_veh_center[1]])
    obj_circle_pt.set_data([obj_circle_center[0]], [obj_circle_center[1]])
    obj_circle_patch.center = obj_circle_center
    obj_circle_patch.set_radius(r_o)

    # Connecting lines
    line_rho_prime.set_data(
        [ego_center[0], obj_veh_center[0]], [ego_center[1], obj_veh_center[1]]
    )
    line_lo.set_data(
        [obj_veh_center[0], obj_circle_center[0]], [obj_veh_center[1], obj_circle_center[1]]
    )

    mid_rho = (ego_center + obj_veh_center) / 2
    text_rho_prime.set_position((mid_rho[0] + 0.1, mid_rho[1] + 0.1))
    
    mid_lo = (obj_veh_center + obj_circle_center) / 2
    text_lo.set_position((mid_lo[0] + 0.1, mid_lo[1] + 0.1))
    text_le.set_position((ego_center[0] / 2, -0.3))

    # Correct Law of Cosines calculation:
    # phi' in the paper formula is the direction angle from Blue Square (Obj Veh Center) back to Yellow Center (Ego)
    phi_prime = phi_ego_to_veh + np.pi

    cos_val = (L_o**2 + rho_prime**2 - R**2) / (2 * L_o * rho_prime + 1e-9)

    if abs(cos_val) <= 1.0:
      delta_theta = np.arccos(cos_val)
      # Boundary rays for theta (direction of Red Dot relative to Blue Square)
      theta_upper = phi_prime + delta_theta
      theta_lower = phi_prime - delta_theta

      # Draw ray lines representing the boundary orientations of L_o (Blue Square -> Red Dot)
      ray_len = L_o * 1.5
      ray_theta_min.set_data(
          [obj_veh_center[0], obj_veh_center[0] + ray_len * np.cos(theta_lower)],
          [obj_veh_center[1], obj_veh_center[1] + ray_len * np.sin(theta_lower)],
      )
      ray_theta_max.set_data(
          [obj_veh_center[0], obj_veh_center[0] + ray_len * np.cos(theta_upper)],
          [obj_veh_center[1], obj_veh_center[1] + ray_len * np.sin(theta_upper)],
      )
    else:
      ray_theta_min.set_data([], [])
      ray_theta_max.set_data([], [])

    # Evaluate Table conditions
    cell_colors = np.full((4, 3), 'white', dtype=object)

    geom_cond1 = L_o > R
    active_rows_geom = [0, 1] if geom_cond1 else [2, 3]

    for r in active_rows_geom:
      cell_colors[r, 0] = '#b2ff59'

    active_row = -1
    if geom_cond1:
      if rho_prime >= (L_o - R):
        active_row = 0
      else:
        active_row = 1
    else:
      if rho_prime > (R - L_o):
        active_row = 2
      else:
        active_row = 3

    cell_colors[active_row, 1] = '#b2ff59'

    cell_colors[active_row, 2] = '#76ff03'
    cell_colors[active_row, 0] = '#76ff03'
    cell_colors[active_row, 1] = '#76ff03'

    for (r_idx, c_idx), cell in ui_table.get_celld().items():
      if r_idx == 0:
        cell.set_facecolor('#d3d3d3')
      else:
        cell.set_facecolor(cell_colors[r_idx - 1, c_idx])

    # Dynamic Legends and Labels
    ego_patch.set_label(f'Ego Circle (r_e = {r_e:.2f} m)')
    ego_center_pt.set_label(f'Ego Center (L_e = {ego_center[0]:.2f} m)')
    obj_veh_pt.set_label(f'Obj Vehicle Center (rho\' = {rho_prime:.2f} m)')
    obj_circle_pt.set_label(f'Obj Circle Center (L_o = {L_o:.2f} m)')
    obj_circle_patch.set_label(f'Obj Circle (r_o = {r_o:.2f} m)')
    ray_theta_min.set_label(r'$\underline{\theta}$ bound ray')
    ray_theta_max.set_label(r'$\bar{\theta}$ bound ray')

    ax_plot.legend(loc='upper left', framealpha=0.9, fontsize=8.5)
    ax_plot.set_title(
        f'Base Case Geometry | Active Condition: Row {active_row + 1} | R = r_e + r_o = {R:.2f} m',
        fontweight='bold',
    )
    fig.canvas.draw_idle()
    is_updating = False

  slider_re.on_changed(update_geometry)
  slider_ro.on_changed(update_geometry)
  slider_lo.on_changed(update_geometry)
  slider_rho.on_changed(update_geometry)

  def on_press(event):
    if event.inaxes != ax_plot:
      return
    m_pos = np.array([event.xdata, event.ydata])
    if np.linalg.norm(m_pos - ego_center) < 0.4:
      drag_state['active'] = 'ego'
    elif np.linalg.norm(m_pos - obj_veh_center) < 0.4:
      drag_state['active'] = 'obj_veh'
    elif np.linalg.norm(m_pos - obj_circle_center) < 0.4:
      drag_state['active'] = 'obj_circle'

  def on_motion(event):
    if drag_state['active'] is None or event.inaxes != ax_plot:
      return
    new_pos = np.array([event.xdata, event.ydata])
    if drag_state['active'] == 'ego':
      ego_center[0] = new_pos[0]
      ego_center[1] = 0.0
    elif drag_state['active'] == 'obj_veh':
      obj_veh_center[0] = new_pos[0]
      obj_veh_center[1] = new_pos[1]
      diff_lo = obj_circle_center - obj_veh_center
      if np.linalg.norm(diff_lo) > 1e-6:
        dir_lo = diff_lo / np.linalg.norm(diff_lo)
      else:
        dir_lo = np.array([1.0, 0.0])
      obj_circle_center[0] = obj_veh_center[0] + slider_lo.val * dir_lo[0]
      obj_circle_center[1] = obj_veh_center[1] + slider_lo.val * dir_lo[1]
    elif drag_state['active'] == 'obj_circle':
      diff = new_pos - obj_veh_center
      if np.linalg.norm(diff) > 1e-6:
        dir_vec = diff / np.linalg.norm(diff)
        obj_circle_center[0] = obj_veh_center[0] + slider_lo.val * dir_vec[0]
        obj_circle_center[1] = obj_veh_center[1] + slider_lo.val * dir_vec[1]

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
