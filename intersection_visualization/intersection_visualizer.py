import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

def run_interactive_base_case():
    # Initial Parameters
    R = 1.2          # Base collision radius (r_ego + r_obs)
    L_o = 1.5        # Distance from object reference center to circle center
    L_e = 2.0        # Ego offset along x-axis
    
    # Ego reference center at (L_e, 0), Object center at (3.5, 1.8)
    ego_center = np.array([L_e, 0.0])
    obj_center = np.array([3.5, 1.8])
    
    fig = plt.figure(figsize=(14, 7))
    
    # Subplot 1: Geometry Canvas
    ax_plot = plt.subplot2grid((1, 3), (0, 0), colspan=2)
    ax_plot.set_aspect('equal')
    ax_plot.set_xlim(-1, 6)
    ax_plot.set_ylim(-2, 4)
    ax_plot.grid(True, linestyle=':', alpha=0.5)
    
    # Subplot 2: Table 3.1 Status Display
    ax_table = plt.subplot2grid((1, 3), (0, 2))
    ax_table.axis('off')
    
    # Draggable Circle Markers
    ego_patch = plt.Circle(ego_center, R, color='gold', fill=False, linewidth=2.5)
    ego_center_point, = ax_plot.plot(ego_center[0], ego_center[1], 'ko', markersize=8)
    
    obj_patch = plt.Circle(obj_center, 0.4, color='cyan', fill=True, alpha=0.4)
    obj_center_point, = ax_plot.plot(obj_center[0], obj_center[1], 'ro', markersize=8)
    
    # Add patches to axis
    ax_plot.add_patch(ego_patch)
    ax_plot.add_patch(obj_patch)
    
    # Geometric Connection Lines & Labels
    line_rho_prime, = ax_plot.plot([], [], 'k--', linewidth=1.5)
    text_rho_prime = ax_plot.text(0, 0, r"$\rho'$", fontsize=12, fontweight='bold', color='purple')
    text_le = ax_plot.text(L_e / 2, -0.3, r"$L_e$", fontsize=12, fontweight='bold', color='black')
    
    # Table 3.1 Data Preparation
    table_data = [
        ["L_o > R", r"$\rho' \geq L_o - R$", r"$[\underline{\theta}, \bar{\theta}]$"],
        ["L_o > R", r"$\rho' < L_o - R$", r"$\emptyset$ (No Intersection)"],
        [r"$R \geq L_o$", r"$\rho' > R - L_o$", r"$[\underline{\theta}, \bar{\theta}]$"],
        [r"$R \geq L_o$", r"$\rho' \leq R - L_o$", r"$[0, 2\pi)$ (Full Angle)"]
    ]
    
    col_labels = ["Geometry", "Radial Condition", "Angle Interval"]
    ui_table = ax_table.table(cellText=table_data, colLabels=col_labels, loc='center', cellLoc='center')
    ui_table.scale(1.2, 2.5)
    ui_table.auto_set_font_size(False)
    ui_table.set_fontsize(9)
    
    # Interactive Dragging Logic
    drag_state = {'active': None}

    def update_geometry():
        nonlocal ego_center, obj_center
        
        # Calculate derived quantities
        diff = obj_center - ego_center
        rho_prime = np.linalg.norm(diff)
        
        # Update patches and lines
        ego_patch.center = ego_center
        ego_center_point.set_data([ego_center[0]], [ego_center[1]])
        
        obj_patch.center = obj_center
        obj_center_point.set_data([obj_center[0]], [obj_center[1]])
        
        line_rho_prime.set_data([ego_center[0], obj_center[0]], [ego_center[1], obj_center[1]])
        
        # Position symbolic text near line midpoints
        mid = (ego_center + obj_center) / 2
        text_rho_prime.set_position((mid[0] + 0.1, mid[1] + 0.1))
        text_le.set_position((ego_center[0] / 2, -0.3))
        
        # Method 2: Update labels directly on elements, then update legend
        ego_patch.set_label(f'Ego Circle (R = {R:.2f} m)')
        ego_center_point.set_label(f'Ego Center (L_e = {ego_center[0]:.2f} m)')
        obj_patch.set_label(f'Object Circle (L_o = {L_o:.2f} m)')
        obj_center_point.set_label(f"Object Center (ρ' = {rho_prime:.2f} m)")
        
        ax_plot.legend(loc='upper left', framealpha=0.9, fontsize=9)
        
        # Evaluate Table 3.1 Active Row
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
                
        # Highlight Table Rows
        for (row_idx, col_idx), cell in ui_table.get_celld().items():
            if row_idx == 0:
                cell.set_facecolor('#d3d3d3')  # Header
            elif row_idx - 1 == active_row:
                cell.set_facecolor('#76ff03')  # Active condition (Bright Green)
            else:
                cell.set_facecolor('white')
                
        ax_plot.set_title(f"Base Case Analysis | Active Row: Condition {active_row + 1}", fontweight='bold')
        fig.canvas.draw_idle()

    # Event Handlers for Dragging
    def on_press(event):
        if event.inaxes != ax_plot:
            return
        m_pos = np.array([event.xdata, event.ydata])
        if np.linalg.norm(m_pos - ego_center) < 0.4:
            drag_state['active'] = 'ego'
        elif np.linalg.norm(m_pos - obj_center) < 0.4:
            drag_state['active'] = 'obj'

    def on_motion(event):
        if drag_state['active'] is None or event.inaxes != ax_plot:
            return
        new_pos = np.array([event.xdata, event.ydata])
        if drag_state['active'] == 'ego':
            ego_center[0] = new_pos[0]
            ego_center[1] = 0.0  # Constrain ego center to X-axis (L_e)
        elif drag_state['active'] == 'obj':
            obj_center[0] = new_pos[0]
            obj_center[1] = new_pos[1]
        update_geometry()

    def on_release(event):
        drag_state['active'] = None

    # Connect Matplotlib Canvas Events
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)
    fig.canvas.mpl_connect('button_release_event', on_release)

    # Initial Draw
    update_geometry()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    run_interactive_base_case()
