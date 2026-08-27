"""
visualizer.py
=============
Visualizes material discovery results, showing critical temperature distributions
and pressure relationships.
"""

from typing import List, Dict, Any

def render_ascii_chart(materials: List[Dict[str, Any]]):
    """
    Renders an ASCII bar chart of critical temperatures to display 
    performance characteristics directly in the console.
    """
    if not materials:
        print("No materials to visualize.")
        return
        
    print("\n" + "=" * 65)
    print("      SUPERCONDUCTOR CANDIDATE TRANSITION TEMPERATURES (Tc)")
    print("=" * 65)
    
    # Sort by Tc descending
    sorted_m = sorted(materials, key=lambda x: x["tc_predicted"], reverse=True)
    
    max_name_len = max(len(m["composition"]) for m in sorted_m)
    
    for m in sorted_m:
        tc = m["tc_predicted"]
        pressure = m["pressure_gpa"]
        name = m["composition"].ljust(max_name_len)
        
        # 1 character = 10 Kelvin
        bar = "#" * int(tc / 10)
        
        # Display room temperature marker
        if tc >= 273.15:
            marker_idx = int(273.15 / 10)
            if marker_idx < len(bar):
                bar_list = list(bar)
                bar_list[marker_idx] = "|"
                bar = "".join(bar_list)
                
        print(f" {name} | {bar:<40} {tc:5.1f} K (P: {pressure:4.1f} GPa)")
        
    print("-" * 65)
    print(" Note: '|' indicates the room-temperature threshold (273.15 K / 0°C)")
    print("=" * 65 + "\n")

def try_save_plot(materials: List[Dict[str, Any]], filename: str = "tc_distribution.png"):
    """
    Attempts to draw and save a scatter plot of Tc vs Pressure using matplotlib
    if the package is installed.
    """
    try:
        import matplotlib.pyplot as plt
        
        compositions = [m["composition"] for m in materials]
        tc_vals = [m["tc_predicted"] for m in materials]
        pressures = [m["pressure_gpa"] for m in materials]
        confidences = [m["confidence"] * 100 for m in materials]
        
        plt.figure(figsize=(10, 6))
        sc = plt.scatter(pressures, tc_vals, s=confidences, c=tc_vals, cmap="plasma", alpha=0.8, edgecolors="none")
        plt.colorbar(sc, label="Predicted Tc (K)")
        
        # Add labels
        for i, txt in enumerate(compositions):
            plt.annotate(txt, (pressures[i], tc_vals[i]), textcoords="offset points", xytext=(0,10), ha='center')
            
        plt.axhline(y=273.15, color="red", linestyle="--", alpha=0.5, label="0°C (273.15 K)")
        plt.title("Transition Temperature (Tc) vs Pressure requirements")
        plt.xlabel("Required Synthesis Pressure (GPa)")
        plt.ylabel("Transition Temperature (K)")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend()
        plt.tight_layout()
        plt.savefig(filename)
        print(f"Successfully saved matplotlib visualization chart to {filename}")
        
    except ImportError:
        # Silently fail if matplotlib is not present; ASCII chart is the fallback
        pass
