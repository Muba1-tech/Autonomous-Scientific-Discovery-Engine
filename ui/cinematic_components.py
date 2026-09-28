import json
import logging

logger = logging.getLogger(__name__)

def render_3d_hypothesis_genome(hypothesis_data: dict, width: int = 700, height: int = 500) -> str:
    """
    Returns HTML/JS using Three.js (loaded from CDN) that visualizes a hypothesis genome.
    
    Args:
        hypothesis_data (dict): Dictionary with keys mechanism, variables, assumptions, causal_relationships, falsification_criteria, predictions
        width (int): Width of the component
        height (int): Height of the component
        
    Returns:
        str: Self-contained HTML string
    """
    data_json = json.dumps(hypothesis_data)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; background-color: #080c1d; overflow: hidden; font-family: sans-serif; }}
            #canvas-container {{ width: 100%; height: {height}px; }}
            #tooltip {{ position: absolute; padding: 8px; background: rgba(8, 12, 29, 0.8); border: 1px solid #38bdf8; color: #fff; pointer-events: none; display: none; border-radius: 4px; z-index: 10; font-size: 12px; }}
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="tooltip"></div>
        <div id="canvas-container"></div>
        <script>
            const data = {data_json};
            const container = document.getElementById('canvas-container');
            const tooltip = document.getElementById('tooltip');
            
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x080c1d);
            
            const camera = new THREE.PerspectiveCamera(75, {width} / {height}, 0.1, 1000);
            camera.position.z = 15;
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize({width}, {height});
            container.appendChild(renderer.domElement);
            
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);
            const pointLight = new THREE.PointLight(0xffffff, 1);
            pointLight.position.set(10, 10, 10);
            scene.add(pointLight);
            
            const group = new THREE.Group();
            scene.add(group);
            
            const interactables = [];
            
            // Mechanism (Center)
            const mechGeo = new THREE.SphereGeometry(2, 32, 32);
            const mechMat = new THREE.MeshPhongMaterial({{ color: 0x38bdf8, emissive: 0x1a5c7a, transparent: true, opacity: 0.9 }});
            const mechMesh = new THREE.Mesh(mechGeo, mechMat);
            mechMesh.userData = {{ type: 'Mechanism', label: data.mechanism || 'Mechanism' }};
            group.add(mechMesh);
            interactables.push(mechMesh);
            
            // Variables (Orbiting)
            const vars = data.variables || [];
            const varMeshes = [];
            vars.forEach((v, i) => {{
                const size = 0.5 + (v.length % 5) * 0.1;
                const varGeo = new THREE.SphereGeometry(size, 16, 16);
                const varMat = new THREE.MeshPhongMaterial({{ color: 0x10b981, emissive: 0x085d41 }});
                const varMesh = new THREE.Mesh(varGeo, varMat);
                
                const angle = (i / vars.length) * Math.PI * 2;
                const radius = 5;
                varMesh.position.x = Math.cos(angle) * radius;
                varMesh.position.z = Math.sin(angle) * radius;
                varMesh.userData = {{ type: 'Variable', label: v, angle, radius, speed: 0.01 + Math.random()*0.02 }};
                
                group.add(varMesh);
                interactables.push(varMesh);
                varMeshes.push(varMesh);
            }});
            
            // Raycaster for tooltips
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            
            window.addEventListener('mousemove', (event) => {{
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
                
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(interactables);
                
                if (intersects.length > 0) {{
                    const obj = intersects[0].object;
                    tooltip.style.display = 'block';
                    tooltip.style.left = event.clientX + 10 + 'px';
                    tooltip.style.top = event.clientY + 10 + 'px';
                    tooltip.innerHTML = `<strong>${{obj.userData.type}}</strong><br>${{obj.userData.label}}`;
                    document.body.style.cursor = 'pointer';
                }} else {{
                    tooltip.style.display = 'none';
                    document.body.style.cursor = 'default';
                }}
            }});
            
            // Animation Loop
            let time = 0;
            function animate() {{
                requestAnimationFrame(animate);
                time += 0.05;
                
                // Pulse mechanism
                const scale = 1 + Math.sin(time) * 0.05;
                mechMesh.scale.set(scale, scale, scale);
                
                // Orbit variables
                varMeshes.forEach(mesh => {{
                    mesh.userData.angle += mesh.userData.speed;
                    mesh.position.x = Math.cos(mesh.userData.angle) * mesh.userData.radius;
                    mesh.position.z = Math.sin(mesh.userData.angle) * mesh.userData.radius;
                }});
                
                group.rotation.y += 0.005;
                group.rotation.x = Math.sin(time*0.2) * 0.1;
                
                controls.update();
                renderer.render(scene, camera);
            }}
            animate();
        </script>
    </body>
    </html>
    """
    return html

def render_discovery_timeline(events: list, width: int = 700, height: int = 200) -> str:
    """
    Returns HTML/CSS/JS for a horizontal scrollable timeline.
    
    Args:
        events (list): List of dicts with keys timestamp, agent, action, detail, icon
        width (int): Component width
        height (int): Component height
        
    Returns:
        str: Self-contained HTML string
    """
    events_json = json.dumps(events)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; background-color: #080c1d; color: #fff; font-family: monospace; overflow: hidden; }}
            .timeline-container {{ display: flex; align-items: center; width: 100%; height: {height}px; overflow-x: auto; overflow-y: hidden; padding: 20px; box-sizing: border-box; cursor: grab; white-space: nowrap; }}
            .timeline-container:active {{ cursor: grabbing; }}
            .timeline-line {{ position: absolute; height: 2px; background: #38bdf8; top: 50%; left: 0; width: max-content; min-width: 100%; z-index: 0; box-shadow: 0 0 10px #38bdf8; }}
            .event-node {{ position: relative; z-index: 1; display: inline-block; margin-right: 150px; text-align: center; vertical-align: middle; }}
            .event-dot {{ width: 16px; height: 16px; border-radius: 50%; margin: 0 auto 10px auto; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; }}
            .event-dot:hover {{ transform: scale(1.5); }}
            
            .role-research {{ background: #38bdf8; box-shadow: 0 0 10px #38bdf8; }}
            .role-critic {{ background: #ef4444; box-shadow: 0 0 10px #ef4444; }}
            .role-experiment {{ background: #10b981; box-shadow: 0 0 10px #10b981; }}
            .role-innovator {{ background: #8b5cf6; box-shadow: 0 0 10px #8b5cf6; }}
            
            .event-content {{ opacity: 0.7; transition: opacity 0.2s; font-size: 12px; }}
            .event-node:hover .event-content {{ opacity: 1; }}
            .event-time {{ color: #a1a1aa; font-size: 10px; margin-bottom: 4px; }}
            .event-action {{ font-weight: bold; }}
            
            .detail-panel {{ position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); background: rgba(8, 12, 29, 0.9); border: 1px solid #38bdf8; padding: 10px; border-radius: 4px; display: none; z-index: 10; max-width: 80%; white-space: normal; }}
        </style>
    </head>
    <body>
        <div class="timeline-container" id="container">
            <div class="timeline-line"></div>
            <!-- Nodes will be injected here -->
        </div>
        <div class="detail-panel" id="detail-panel"></div>
        <script>
            const events = {events_json};
            const container = document.getElementById('container');
            const detailPanel = document.getElementById('detail-panel');
            
            events.forEach(ev => {{
                const node = document.createElement('div');
                node.className = 'event-node';
                
                const roleClass = ev.agent.toLowerCase().includes('critic') ? 'role-critic' : 
                                  ev.agent.toLowerCase().includes('experiment') ? 'role-experiment' :
                                  ev.agent.toLowerCase().includes('innovator') ? 'role-innovator' : 'role-research';
                
                const dot = document.createElement('div');
                dot.className = `event-dot ${{roleClass}}`;
                
                const content = document.createElement('div');
                content.className = 'event-content';
                content.innerHTML = `<div class="event-time">${{ev.timestamp}}</div><div class="event-action">${{ev.action}}</div>`;
                
                dot.onclick = () => {{
                    detailPanel.style.display = 'block';
                    detailPanel.innerHTML = `<strong>${{ev.agent}}</strong>: ${{ev.action}}<br><span style="color:#a1a1aa; font-size:11px;">${{ev.detail || ''}}</span>`;
                    setTimeout(() => {{ detailPanel.style.display = 'none'; }}, 5000);
                }};
                
                node.appendChild(dot);
                node.appendChild(content);
                container.appendChild(node);
            }});
            
            let isDown = false;
            let startX;
            let scrollLeft;
            
            container.addEventListener('mousedown', (e) => {{
                isDown = true;
                startX = e.pageX - container.offsetLeft;
                scrollLeft = container.scrollLeft;
            }});
            container.addEventListener('mouseleave', () => {{ isDown = false; }});
            container.addEventListener('mouseup', () => {{ isDown = false; }});
            container.addEventListener('mousemove', (e) => {{
                if(!isDown) return;
                e.preventDefault();
                const x = e.pageX - container.offsetLeft;
                const walk = (x - startX) * 2;
                container.scrollLeft = scrollLeft - walk;
            }});
        </script>
    </body>
    </html>
    """
    return html

def render_live_swarm_hud(agents: list, width: int = 700, height: int = 350) -> str:
    """
    Returns HTML/CSS/JS for an animated agent swarm visualization.
    
    Args:
        agents (list): List of dicts with keys name, role, status, activity
        width (int): Component width
        height (int): Component height
        
    Returns:
        str: Self-contained HTML string
    """
    agents_json = json.dumps(agents)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; background-color: #080c1d; overflow: hidden; font-family: monospace; }}
            #hud-container {{ position: relative; width: 100%; height: {height}px; }}
            .agent-node {{ position: absolute; border-radius: 50%; width: 40px; height: 40px; transform: translate(-50%, -50%); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px; cursor: pointer; text-align: center; }}
            
            .role-research {{ border: 2px solid #38bdf8; box-shadow: 0 0 15px #38bdf8; }}
            .role-critic {{ border: 2px solid #ef4444; box-shadow: 0 0 15px #ef4444; }}
            .role-experiment {{ border: 2px solid #10b981; box-shadow: 0 0 15px #10b981; }}
            .role-innovator {{ border: 2px solid #8b5cf6; box-shadow: 0 0 15px #8b5cf6; }}
            .role-validator {{ border: 2px solid #f59e0b; box-shadow: 0 0 15px #f59e0b; }}
            
            .pulse-active {{ animation: pulse 1.5s infinite; }}
            
            @keyframes pulse {{
                0% {{ transform: translate(-50%, -50%) scale(0.95); box-shadow: 0 0 0 0 rgba(255,255,255, 0.7); }}
                70% {{ transform: translate(-50%, -50%) scale(1); box-shadow: 0 0 0 10px rgba(255,255,255, 0); }}
                100% {{ transform: translate(-50%, -50%) scale(0.95); box-shadow: 0 0 0 0 rgba(255,255,255, 0); }}
            }}
            
            .agent-label {{ position: absolute; bottom: -20px; white-space: nowrap; color: #a1a1aa; font-size: 10px; }}
            
            svg {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }}
            line {{ stroke: rgba(255,255,255,0.2); stroke-width: 1; }}
        </style>
    </head>
    <body>
        <div id="hud-container">
            <svg id="svg-layer"></svg>
        </div>
        <script>
            const agents = {agents_json};
            const container = document.getElementById('hud-container');
            const svgLayer = document.getElementById('svg-layer');
            
            const centerX = {width} / 2;
            const centerY = {height} / 2;
            const radius = Math.min(centerX, centerY) - 50;
            
            const nodes = [];
            
            agents.forEach((ag, i) => {{
                const angle = (i / agents.length) * Math.PI * 2;
                const x = centerX + Math.cos(angle) * radius;
                const y = centerY + Math.sin(angle) * radius;
                
                nodes.push({{ x, y, agent: ag }});
                
                const node = document.createElement('div');
                let roleClass = 'role-research';
                if(ag.role === 'critic') roleClass = 'role-critic';
                else if(ag.role === 'experiment') roleClass = 'role-experiment';
                else if(ag.role === 'innovator') roleClass = 'role-innovator';
                else if(ag.role === 'validator') roleClass = 'role-validator';
                
                node.className = `agent-node ${{roleClass}} ${{ag.status === 'active' ? 'pulse-active' : ''}}`;
                node.style.left = `${{x}}px`;
                node.style.top = `${{y}}px`;
                node.innerHTML = `<div>${{ag.name.substring(0,2).toUpperCase()}}</div><div class="agent-label">${{ag.name}}</div>`;
                node.title = `Role: ${{ag.role}}\\nStatus: ${{ag.status}}\\nActivity: ${{ag.activity}}`;
                
                // Color fill based on status
                if(ag.status === 'active') node.style.backgroundColor = 'rgba(255,255,255,0.1)';
                else if(ag.status === 'waiting') node.style.backgroundColor = 'rgba(245, 158, 11, 0.2)';
                else node.style.backgroundColor = 'rgba(0,0,0,0.5)';
                
                container.appendChild(node);
            }});
            
            // Draw connections
            for(let i=0; i<nodes.length; i++) {{
                for(let j=i+1; j<nodes.length; j++) {{
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', nodes[i].x);
                    line.setAttribute('y1', nodes[i].y);
                    line.setAttribute('x2', nodes[j].x);
                    line.setAttribute('y2', nodes[j].y);
                    svgLayer.appendChild(line);
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html

def render_kill_chain_visualization(kill_chain_data: dict, width: int = 700, height: int = 300) -> str:
    """
    Returns HTML/CSS for a 10-stage kill chain progress visualization.
    
    Args:
        kill_chain_data (dict): Dictionary with keys overall_score, stages (list of dicts with name, score, detail)
        width (int): Component width
        height (int): Component height
        
    Returns:
        str: Self-contained HTML string
    """
    data_json = json.dumps(kill_chain_data)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; background-color: #080c1d; font-family: monospace; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: {height}px; }}
            .score-display {{ font-size: 24px; font-weight: bold; margin-bottom: 20px; text-shadow: 0 0 10px #38bdf8; color: #38bdf8; }}
            .pipeline {{ display: flex; align-items: center; width: 90%; justify-content: space-between; position: relative; }}
            .pipeline::before {{ content: ''; position: absolute; top: 50%; left: 0; right: 0; height: 4px; background: rgba(255,255,255,0.1); z-index: 0; transform: translateY(-50%); }}
            
            .stage-node {{ position: relative; z-index: 1; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; cursor: help; transition: transform 0.2s; }}
            .stage-node:hover {{ transform: scale(1.1); }}
            
            .score-good {{ background: #10b981; box-shadow: 0 0 10px #10b981; }}
            .score-warn {{ background: #f59e0b; box-shadow: 0 0 10px #f59e0b; color: black; }}
            .score-fail {{ background: #ef4444; box-shadow: 0 0 10px #ef4444; animation: shake 0.5s; }}
            
            @keyframes shake {{
                0% {{ transform: translateX(0); }}
                25% {{ transform: translateX(-5px); }}
                50% {{ transform: translateX(5px); }}
                75% {{ transform: translateX(-5px); }}
                100% {{ transform: translateX(0); }}
            }}
            
            .stage-name {{ position: absolute; top: -25px; font-size: 10px; color: #a1a1aa; white-space: nowrap; text-transform: uppercase; }}
            .stage-score {{ position: absolute; bottom: -20px; font-size: 10px; color: white; }}
        </style>
    </head>
    <body>
        <div class="score-display" id="total-score">Survival Score: --</div>
        <div class="pipeline" id="pipeline"></div>
        
        <script>
            const data = {data_json};
            document.getElementById('total-score').innerText = `Survival Score: ${{data.overall_score || 0}}/100`;
            const pipeline = document.getElementById('pipeline');
            
            const stages = data.stages || [];
            stages.forEach((stage, idx) => {{
                const node = document.createElement('div');
                let scoreClass = 'score-good';
                if(stage.score < 60) scoreClass = 'score-fail';
                else if(stage.score <= 80) scoreClass = 'score-warn';
                
                node.className = `stage-node ${{scoreClass}}`;
                node.title = stage.detail || stage.name;
                node.innerText = idx + 1;
                
                const nameLabel = document.createElement('div');
                nameLabel.className = 'stage-name';
                nameLabel.innerText = stage.name;
                
                const scoreLabel = document.createElement('div');
                scoreLabel.className = 'stage-score';
                scoreLabel.innerText = stage.score;
                
                node.appendChild(nameLabel);
                node.appendChild(scoreLabel);
                pipeline.appendChild(node);
            }});
        </script>
    </body>
    </html>
    """
    return html
