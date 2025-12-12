import warnings
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI.*')
import ovito._extensions.pyscript

from ovito.io import import_file
import numpy as np
import os
import json

print("="*70)
print("FULL PARTICLE DENSITY - NO DOWNSAMPLING")
print("="*70)

pipeline = import_file(r"C:\Users\akshansh\Downloads\EXTRAS\fsw_process.lammpstrj")
total_frames = pipeline.source.num_frames
print(f"Total frames: {total_frames}")

# Export frames - ALL PARTICLES, NO DOWNSAMPLING
frames_to_export = [0, 285, 570, 855, 1141]
print(f"\nExporting {len(frames_to_export)} frames with FULL particle count...")

all_frames_data = []

for frame_idx in frames_to_export:
    data = pipeline.compute(frame_idx)
    
    # NO DOWNSAMPLING - USE ALL PARTICLES
    positions = np.array(data.particles.positions)
    property_values = np.array(data.particles['c_grain_atoms'])
    
    if len(property_values.shape) > 1:
        property_values = property_values[:, 0]
    
    # Normalize
    pmin, pmax = float(property_values.min()), float(property_values.max())
    prop_norm = (property_values - pmin) / (pmax - pmin) if pmax > pmin else np.ones_like(property_values) * 0.5
    
    all_frames_data.append({
        'frame': frame_idx,
        'positions': positions.tolist(),
        'colors': prop_norm.tolist(),
        'count': len(positions),
        'property_min': pmin,
        'property_max': pmax
    })
    
    print(f"  Frame {frame_idx}: {len(positions):,} particles")

first_pos = np.array(all_frames_data[0]['positions'])
center = first_pos.mean(axis=0)
size = float(np.linalg.norm(first_pos.max(axis=0) - first_pos.min(axis=0)))

global_min = min(f['property_min'] for f in all_frames_data)
global_max = max(f['property_max'] for f in all_frames_data)

frames_json = json.dumps({
    'frames': all_frames_data,
    'center': center.tolist(),
    'size': size,
    'global_min': global_min,
    'global_max': global_max
})

output_dir = r"C:\Users\pedit\Downloads\EXTRAS\ovito_vr_output"
os.makedirs(output_dir, exist_ok=True)

print(f"\nTotal data size: {len(frames_json)/1024/1024:.1f} MB")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>FSW Virtual Reality Viewer - Full Resolution</title>
    <style>
        * {{ margin: 0; padding: 0; }}
        body {{ font-family: Arial, sans-serif; background: #000; color: #fff; overflow: hidden; }}
        #container {{ width: 100vw; height: 100vh; }}
        #info {{
            position: absolute; top: 20px; left: 20px;
            background: rgba(0,0,0,0.9); padding: 20px; border-radius: 10px;
            border: 2px solid #0066ff; z-index: 1000; font-size: 14px; line-height: 1.8;
        }}
        #info h1 {{ font-size: 18px; margin-bottom: 10px; }}
        #colormap {{
            position: absolute; top: 20px; right: 20px;
            background: rgba(0,0,0,0.9); padding: 20px; border-radius: 10px;
            border: 2px solid #0066ff; z-index: 1000; text-align: center;
        }}
        select {{
            width: 150px; padding: 8px; margin-bottom: 15px;
            background: rgba(255,255,255,0.1); border: 1px solid #0066ff;
            color: white; border-radius: 5px; cursor: pointer;
        }}
        #colorbar {{ width: 50px; height: 200px; border: 2px solid #fff; border-radius: 5px; margin: 0 auto 10px; }}
        .label {{ font-size: 11px; color: #aaa; }}
        #controls {{
            position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%);
            background: rgba(0,0,0,0.9); padding: 20px 30px; border-radius: 10px;
            border: 2px solid #0066ff; z-index: 1000; text-align: center;
        }}
        button {{
            padding: 10px 20px; margin: 5px; font-size: 14px;
            background: #0066ff; color: white; border: none;
            border-radius: 5px; cursor: pointer;
        }}
        button:hover {{ background: #0052cc; }}
        #frameSlider {{ width: 400px; margin: 10px auto; }}
        #frameInfo {{ font-size: 16px; font-weight: bold; margin: 10px 0; }}
        #loading {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
            font-size: 24px; background: rgba(0,0,0,0.9); padding: 30px;
            border-radius: 10px; z-index: 2000;
        }}
    </style>
</head>
<body>
    <div id="loading">Loading {all_frames_data[0]['count']:,} particles...</div>
    <div id="container"></div>
    
    <div id="info" style="display:none;">
        <h1>Friction Stir Welding Virtual Reality Viewer</h1>
        <div id="particleInfo">Loading...</div>
        <div style="font-size:12px; color:#0f0; margin-top:5px;">FULL RESOLUTION - ALL PARTICLES</div>
    </div>
    
    <div id="colormap" style="display:none;">
        <h3 style="font-size:14px; margin-bottom:10px;">Colormap</h3>
        <select id="cmap" onchange="updateColormap()">
            <option value="viridis">Viridis</option>
            <option value="plasma">Plasma</option>
            <option value="inferno">Inferno</option>
            <option value="magma">Magma</option>
            <option value="jet">Jet</option>
            <option value="hot">Hot</option>
            <option value="cool">Cool</option>
        </select>
        <div id="colorbar"></div>
        <div class="label">{global_max:.2f}</div>
        <div style="height:160px;"></div>
        <div class="label">{global_min:.2f}</div>
    </div>
    
    <div id="controls" style="display:none;">
        <div id="frameInfo">Frame 1 / {len(frames_to_export)}</div>
        <div>
            <button onclick="firstFrame()">First</button>
            <button onclick="prevFrame()">Previous</button>
            <button id="playBtn" onclick="togglePlay()">Play</button>
            <button onclick="nextFrame()">Next</button>
            <button onclick="lastFrame()">Last</button>
        </div>
        <input type="range" id="frameSlider" min="0" max="{len(frames_to_export)-1}" value="0" oninput="onSliderChange()">
        <div style="font-size:12px; margin-top:10px;">Drag to rotate • Scroll to zoom • Right-drag to pan</div>
    </div>

    <script type="importmap">
    {{"imports": {{"three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"}}}}
    </script>

    <script type="module">
        import * as THREE from 'three';
        import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
        import {{ VRButton }} from 'three/addons/webxr/VRButton.js';

        console.log('Loading full particle data...');
        const allData = {frames_json};
        console.log('Data loaded:', allData.frames[0].count, 'particles per frame');
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('info').style.display = 'block';
        document.getElementById('colormap').style.display = 'block';
        document.getElementById('controls').style.display = 'block';

        const COLORMAPS = {{
            viridis: [[0.267,0.005,0.329],[0.283,0.141,0.458],[0.254,0.265,0.530],[0.164,0.471,0.558],[0.135,0.659,0.518],[0.478,0.821,0.318],[0.993,0.906,0.144]],
            plasma: [[0.050,0.030,0.528],[0.417,0.001,0.658],[0.693,0.165,0.565],[0.881,0.393,0.383],[0.987,0.810,0.145]],
            inferno: [[0.001,0.000,0.014],[0.144,0.047,0.338],[0.502,0.092,0.472],[0.855,0.258,0.283],[0.988,0.553,0.111]],
            magma: [[0.001,0.000,0.014],[0.129,0.046,0.285],[0.429,0.101,0.478],[0.670,0.188,0.427],[0.892,0.364,0.279],[0.987,0.810,0.145]],
            jet: t => {{const r=Math.max(0,Math.min(1,1.5-Math.abs(4*t-3))),g=Math.max(0,Math.min(1,1.5-Math.abs(4*t-2))),b=Math.max(0,Math.min(1,1.5-Math.abs(4*t-1)));return[r,g,b]}},
            hot: t => [Math.min(1,3*t),Math.min(1,Math.max(0,3*t-1)),Math.min(1,Math.max(0,3*t-2))],
            cool: t => [t,1-t,1]
        }};

        function getColor(cmap,t){{if(typeof cmap==='function')return cmap(t);const i=Math.min(Math.floor(t*(cmap.length-1)),cmap.length-2),f=t*(cmap.length-1)-i;return cmap[i].map((v,k)=>v+(cmap[i+1][k]-v)*f)}}

        let scene,camera,renderer,controls,particleSystem;
        let currentCmap='viridis',currentFrameIdx=0,isPlaying=false,playInterval;

        scene=new THREE.Scene();
        scene.background=new THREE.Color(0x0a0a0a);
        camera=new THREE.PerspectiveCamera(60,window.innerWidth/window.innerHeight,0.1,10000);
        renderer=new THREE.WebGLRenderer({{antialias:true}});
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(window.innerWidth,window.innerHeight);
        renderer.xr.enabled=true;
        document.getElementById('container').appendChild(renderer.domElement);
        document.body.appendChild(VRButton.createButton(renderer));
        controls=new OrbitControls(camera,renderer.domElement);
        controls.enableDamping=true;
        controls.dampingFactor=0.05;
        scene.add(new THREE.AmbientLight(0xffffff,0.8));
        const light=new THREE.DirectionalLight(0xffffff,0.6);
        light.position.set(100,100,50);
        scene.add(light);

        const dist=allData.size*1.5;
        camera.position.set(allData.center[0]+dist,allData.center[1]+dist*0.7,allData.center[2]+dist);
        controls.target.set(allData.center[0],allData.center[1],allData.center[2]);
        controls.update();

        const grid=new THREE.GridHelper(allData.size*2,40,0x444444,0x222222);
        grid.position.y=allData.center[1]-allData.size*0.5;
        scene.add(grid);
        scene.add(new THREE.AxesHelper(allData.size*0.5));

        function updateFrame(){{
            const frameData=allData.frames[currentFrameIdx];
            if(particleSystem)scene.remove(particleSystem);
            
            console.log('Creating', frameData.count, 'particles...');
            const geo=new THREE.BufferGeometry();
            const pos=new Float32Array(frameData.count*3);
            const col=new Float32Array(frameData.count*3);
            const cmap=COLORMAPS[currentCmap];
            
            for(let i=0;i<frameData.count;i++){{
                pos[i*3]=frameData.positions[i][0];
                pos[i*3+1]=frameData.positions[i][1];
                pos[i*3+2]=frameData.positions[i][2];
                const c=getColor(cmap,frameData.colors[i]);
                col[i*3]=c[0];col[i*3+1]=c[1];col[i*3+2]=c[2];
            }}
            
            geo.setAttribute('position',new THREE.BufferAttribute(pos,3));
            geo.setAttribute('color',new THREE.BufferAttribute(col,3));
            
            // Smaller particle size since we have MANY more particles
            const mat=new THREE.PointsMaterial({{size:allData.size*0.008,vertexColors:true,sizeAttenuation:true}});
            particleSystem=new THREE.Points(geo,mat);
            scene.add(particleSystem);
            
            document.getElementById('particleInfo').innerHTML=
                `Particles: ${{frameData.count.toLocaleString()}}<br>Property: c_grain_atoms<br>Range: ${{frameData.property_min.toFixed(2)}} - ${{frameData.property_max.toFixed(2)}}`;
            document.getElementById('frameInfo').textContent=
                `Frame ${{currentFrameIdx+1}} / ${{allData.frames.length}} (Step ${{frameData.frame}})`;
            document.getElementById('frameSlider').value=currentFrameIdx;
            console.log('Frame updated');
        }}

        function updateGradient(){{
            const cmap=COLORMAPS[currentCmap];let grad='linear-gradient(to bottom';
            for(let i=0;i<=100;i++){{const c=getColor(cmap,1-i/100);grad+=`,rgb(${{Math.round(c[0]*255)}},${{Math.round(c[1]*255)}},${{Math.round(c[2]*255)}}) ${{i}}%`}}
            grad+=')';document.getElementById('colorbar').style.background=grad;
        }}

        window.updateColormap=()=>{{currentCmap=document.getElementById('cmap').value;updateFrame();updateGradient()}};
        window.firstFrame=()=>{{currentFrameIdx=0;updateFrame()}};
        window.lastFrame=()=>{{currentFrameIdx=allData.frames.length-1;updateFrame()}};
        window.nextFrame=()=>{{currentFrameIdx=(currentFrameIdx+1)%allData.frames.length;updateFrame()}};
        window.prevFrame=()=>{{currentFrameIdx=(currentFrameIdx-1+allData.frames.length)%allData.frames.length;updateFrame()}};
        window.onSliderChange=()=>{{currentFrameIdx=parseInt(document.getElementById('frameSlider').value);updateFrame()}};
        window.togglePlay=()=>{{
            if(isPlaying){{
                clearInterval(playInterval);
                document.getElementById('playBtn').textContent='Play';
                isPlaying=false;
            }}else{{
                playInterval=setInterval(window.nextFrame,500);
                document.getElementById('playBtn').textContent='Pause';
                isPlaying=true;
            }}
        }};

        document.addEventListener('keydown',e=>{{
            if(e.key==='ArrowLeft')window.prevFrame();
            if(e.key==='ArrowRight')window.nextFrame();
            if(e.key===' '){{e.preventDefault();window.togglePlay();}}
        }});

        updateFrame();
        updateGradient();

        renderer.setAnimationLoop(()=>{{controls.update();renderer.render(scene,camera)}});
        window.addEventListener('resize',()=>{{camera.aspect=window.innerWidth/window.innerHeight;camera.updateProjectionMatrix();renderer.setSize(window.innerWidth,window.innerHeight)}});

        console.log('READY - ALL',allData.frames[0].count,'PARTICLES LOADED!');
    </script>
</body>
</html>"""

html_file = os.path.join(output_dir, 'fsw_vr_full.html')
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html)

file_size = os.path.getsize(html_file) / (1024 * 1024)

print(f"\n{'='*70}")
print(f"FULL RESOLUTION VR VIEWER CREATED!")
print(f"{'='*70}")
print(f"\nSaved: {html_file}")
print(f"File size: {file_size:.1f} MB")
print(f"\nParticles per frame: {all_frames_data[0]['count']:,}")
print(f"Total frames: {len(frames_to_export)}")
print(f"\nNO DOWNSAMPLING - EXACT SAME AS OVITO!")
print(f"\nNote: May take a few seconds to switch frames due to particle count")
print(f"{'='*70}")
