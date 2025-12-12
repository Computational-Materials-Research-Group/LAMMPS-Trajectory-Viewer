# LAMMPS Trajectory VR Viewer

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![OVITO](https://img.shields.io/badge/OVITO-required-green.svg)
![WebXR](https://img.shields.io/badge/WebXR-enabled-orange.svg)
![License](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)

A high-fidelity 3D visualization tool for molecular dynamics simulations with full WebXR/VR support. Export any LAMMPS trajectory file from OVITO and explore your simulation data in an immersive virtual reality environment.

## Overview

This tool converts LAMMPS trajectory files (.lammpstrj) into interactive web-based 3D visualizations that can be experienced in virtual reality. The viewer maintains full particle resolution without downsampling, providing exact representation of your molecular dynamics simulation data.

## Features

- **Full Resolution Rendering**: Displays all particles from your MD simulation without any downsampling
- **Universal LAMMPS Support**: Works with any LAMMPS trajectory file format (.lammpstrj)
- **Flexible Property Visualization**: Visualize any particle property from your simulation
- **WebXR/VR Support**: Native virtual reality support for immersive data exploration
- **Multiple Colormaps**: Seven different scientific colormaps (Viridis, Plasma, Inferno, Magma, Jet, Hot, Cool)
- **Interactive Controls**: Frame-by-frame navigation with play/pause functionality
- **Responsive Interface**: Smooth camera controls with orbit, zoom, and pan capabilities
- **Keyboard Shortcuts**: Arrow keys for navigation, spacebar for play/pause

## Requirements

### Python Dependencies
- OVITO (with Python bindings)
- NumPy
- Python 3.x

### Browser Requirements
- Modern web browser with WebGL support
- For VR: WebXR-compatible VR headset and browser

## Installation

1. Install OVITO with Python bindings:
```bash
pip install ovito
```

2. Install NumPy (if not already installed):
```bash
pip install numpy
```

## Usage

### 1. Configure Input File

Edit the script to point to your LAMMPS trajectory file:

```python
pipeline = import_file(r"C:\path\to\your\simulation.lammpstrj")
```

### 2. Configure Property to Visualize

Specify which particle property you want to visualize:

```python
property_values = np.array(data.particles['c_grain_atoms'])  # Change to your property name
```

Common LAMMPS properties include:
- Particle type: `data.particles['Particle Type']`
- Velocities: `data.particles['Velocity']`
- Forces: `data.particles['Force']`
- Custom compute values: `data.particles['c_your_compute_name']`

### 2. Select Frames to Export

Modify the frames you want to visualize (frame indices from your trajectory):

```python
frames_to_export = [0, 285, 570, 855, 1141]  # Adjust frame numbers as needed
```

### 3. Set Output Directory

Specify where the HTML viewer should be saved:

```python
output_dir = r"C:\path\to\output\directory"
```

### 4. Run the Script

```bash
python lammps_vr_viewer.py
```

### 5. Open the Generated HTML

Open the generated HTML file in a web browser. For VR mode, click the "Enter VR" button (requires WebXR-compatible device).

## Controls

### Mouse/Trackpad
- **Left Click + Drag**: Rotate view
- **Right Click + Drag**: Pan camera
- **Scroll Wheel**: Zoom in/out

### Keyboard
- **Left Arrow**: Previous frame
- **Right Arrow**: Next frame
- **Spacebar**: Play/Pause animation

### Interface Buttons
- **First**: Jump to first frame
- **Previous**: Go to previous frame
- **Play/Pause**: Toggle animation
- **Next**: Go to next frame
- **Last**: Jump to last frame

### Frame Slider
Drag the slider to jump to any frame directly

## Output Information

The script provides detailed console output including:
- Total number of frames in the trajectory
- Number of particles per frame
- Data size in MB
- File size of generated HTML

## Technical Details

### Data Format
- Positions: 3D coordinates (x, y, z) for each particle
- Colors: Normalized property values mapped to selected colormap
- Property: Any particle property from your LAMMPS simulation

### Rendering
- Uses Three.js r160 for 3D graphics
- Point cloud rendering with vertex colors
- Dynamic particle sizing based on scene scale
- Adaptive point size: ~0.8% of total scene size

### Performance Notes
- Full resolution data may result in large HTML files (50-500+ MB depending on particle count)
- Frame switching may take a few seconds with high particle counts
- Recommended for desktop/VR viewing rather than mobile devices

## Customization

### Adjusting Particle Size
Modify the particle size multiplier in the HTML:

```javascript
const mat = new THREE.PointsMaterial({
    size: allData.size * 0.008,  // Adjust this multiplier
    vertexColors: true,
    sizeAttenuation: true
});
```

### Adding More Colormaps
Add new colormap definitions in the COLORMAPS object:

```javascript
customMap: [[r1,g1,b1], [r2,g2,b2], ...]
```

### Animation Speed
Change the frame interval (in milliseconds):

```javascript
playInterval = setInterval(window.nextFrame, 500);  // 500ms = 0.5 seconds per frame
```

## Troubleshooting

### Large File Size
- The HTML file embeds all particle data directly
- File size scales with particle count and number of frames
- Consider reducing the number of exported frames if file size is an issue

### Slow Frame Switching
- Normal behavior with 100,000+ particles per frame
- Browser needs time to rebuild geometry for each frame
- Consider using a more powerful computer or reducing particle count

### VR Button Not Appearing
- Ensure your browser supports WebXR
- Check that you're accessing via HTTPS or localhost
- Verify VR device is connected and recognized

### Property Not Found Error
- Check the exact property name in OVITO
- Ensure the property exists in your LAMMPS trajectory file
- Use OVITO's GUI to verify available properties before running the script

## Examples

This tool has been successfully used for visualizing:
- Friction Stir Welding (FSW) simulations
- Grain boundary dynamics
- Deformation processes
- Thermal transport phenomena
- Any molecular dynamics simulation with LAMMPS output

## Author

Created by Akshansh Mishra

GitHub: [https://github.com/akshansh11/](https://github.com/akshansh11/)

## License

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">
<img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" />
</a>

This work is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

You are free to:
- Share: copy and redistribute the material in any medium or format
- Adapt: remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- Attribution: You must give appropriate credit, provide a link to the license, and indicate if changes were made
- ShareAlike: If you remix, transform, or build upon the material, you must distribute your contributions under the same license

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Citation

If you use this tool in your research, please cite your work appropriately and link back to this repository.
