import streamlit as st

# HTML content (your provided HTML)
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raindrop Sound Grid</title>
    <style>
        .grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 10px;
            max-width: 600px;
            margin: 20px auto;
        }

        .raindrop {
            aspect-ratio: 1;
            background-image: url('cat.png');
            background-size: contain;
            background-repeat: no-repeat;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .raindrop:hover {
            transform: scale(1.1); 
        }

        .raindrop.active {
            animation: glow-fade 6s linear infinite;
        }

        @keyframes glow-fade {
            0% {
                background-color: #ffeb3b;
                box-shadow: 0 0 20px rgba(255, 235, 59, 0.8);
            }
            100% {
                background-color: #3b82f6;
                box-shadow: none;
            }
        }

        .controls {
            text-align: center;
            margin: 20px;
        }

        button.cancel {
            padding: 10px 20px;
            font-size: 16px;
            background-color: #ef4444;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        button.cancel:hover {
            background-color: #dc2626;
        }
    </style>
</head>
<body>
    <div id="rainGrid" class="grid"></div>
    <div class="controls">
        <button class="cancel" onclick="cancelAll()">Cancel All</button>
    </div>

    <script>
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const LOOP_DURATION = 6000; 
        const GRID_WIDTH = 7;
        const GRID_HEIGHT = 6;

        let startTime = audioContext.currentTime * 1000;
        
        const raindrops = Array.from({ length: GRID_HEIGHT }, () => Array(GRID_WIDTH).fill(null));
        const audioBuffers = Array.from({ length: GRID_HEIGHT }, () => Array(GRID_WIDTH).fill(null));

        const grid = document.getElementById('rainGrid');

        // Create raindrop grid
        for (let row = 0; row < GRID_HEIGHT; row++) {
            for (let col = 0; col < GRID_WIDTH; col++) {
                const raindrop = document.createElement('div');
                raindrop.className = 'raindrop';
                raindrop.dataset.row = row;
                raindrop.dataset.col = col;
                raindrop.addEventListener('click', handleRaindropClick);
                grid.appendChild(raindrop);
            }
        }

        // Ensure audio plays after user interaction
        document.addEventListener('click', () => {
            if (audioContext.state === 'suspended') {
                audioContext.resume();
            }
        });

        // Load audio files dynamically
        async function loadAudio() {
            let fileNumber = 26;

            for (let row = 0; row < GRID_HEIGHT; row++) {
                for (let col = 0; col < GRID_WIDTH; col++) {
                    const fileName = `sounds/${fileNumber}.mp3`;

                    try {
                        console.log(`Loading ${fileName}`);
                        const response = await fetch(fileName);

                        if (response.ok) {
                            const arrayBuffer = await response.arrayBuffer();
                            audioBuffers[row][col] = await audioContext.decodeAudioData(arrayBuffer);
                            console.log(`Successfully loaded ${fileName}`);
                        } else {
                            console.warn(`File not found: ${fileName}`);
                        }
                    } catch (error) {
                        console.error(`Error loading ${fileName}:`, error);
                    }

                    fileNumber++;
                }
            }
        }

        let lastPlayedTimes = {};

        function playRaindropSound(row, col) {
            if (audioBuffers[row][col]) {
                const currentTime = audioContext.currentTime * 1000;
                const key = `${row}-${col}`;

                if (lastPlayedTimes[key] && currentTime - lastPlayedTimes[key] < 100) {
                    return;
                }

                lastPlayedTimes[key] = currentTime;

                const source = audioContext.createBufferSource();
                source.buffer = audioBuffers[row][col];

                const gainNode = audioContext.createGain();
                gainNode.gain.value = 0.8;

                source.connect(gainNode);
                gainNode.connect(audioContext.destination);
                source.start();
            }
        }

        function handleRaindropClick(event) {
            if (audioContext.state === 'suspended') {
                audioContext.resume();
            }

            const row = parseInt(event.target.dataset.row);
            const col = parseInt(event.target.dataset.col);
            const currentLoopTime = (audioContext.currentTime * 1000 - startTime) % LOOP_DURATION;

            if (raindrops[row][col] === null) {
                raindrops[row][col] = currentLoopTime;
                event.target.classList.add('active');
                playRaindropSound(row, col);
            } else {
                raindrops[row][col] = null;
                event.target.classList.remove('active');
            }
        }

        function cancelAll() {
            for (let row = 0; row < GRID_HEIGHT; row++) {
                for (let col = 0; col < GRID_WIDTH; col++) {
                    raindrops[row][col] = null;
                }
            }

            document.querySelectorAll('.raindrop').forEach(raindrop => raindrop.classList.remove('active'));
        }

        function updateLoop() {
            const currentLoopTime = (audioContext.currentTime * 1000 - startTime) % LOOP_DURATION;

            for (let row = 0; row < GRID_HEIGHT; row++) {
                for (let col = 0; col < GRID_WIDTH; col++) {
                    const timing = raindrops[row][col];

                    if (timing !== null) {
                        const timeDiff = Math.abs(currentLoopTime - timing);
                        const shouldPlay = timeDiff < 50 || timeDiff > LOOP_DURATION - 50;

                        if (shouldPlay) {
                            playRaindropSound(row, col);
                        }
                    }
                }
            }

            requestAnimationFrame(updateLoop);
        }

        loadAudio().catch(console.error);
        requestAnimationFrame(updateLoop);
    </script>
</body>
</html>
"""

# Render HTML in Streamlit
st.markdown(html_content, unsafe_allow_html=True)
