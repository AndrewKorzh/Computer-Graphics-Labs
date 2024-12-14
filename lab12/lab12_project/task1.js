let gradientTetrahedron = {
    gl: null,
    program: null,
    buffer: null,
    positionAttribute: null,
    colorAttribute: null,
    rotationAngleX: 0,
    rotationAngleY: 0,

    setup() {
        const canvas = document.getElementById('webgl-canvas');
        this.gl = canvas.getContext('webgl');
        if (!this.gl) {
            alert('WebGL not supported');
            return;
        }
        this.initShaders();
        this.initBuffers();
        this.initEventListeners();
        this.render();
    },

    initShaders() {
        const vertexShaderSource = `
            attribute vec4 position;
            attribute vec4 color;
            varying vec4 vColor;
            uniform mat4 modelViewMatrix;
            void main() {
                gl_Position = modelViewMatrix * position;
                vColor = color;
            }
        `;
        const fragmentShaderSource = `
            precision mediump float;
            varying vec4 vColor;
            void main() {
                gl_FragColor = vColor;
            }
        `;

        const vertexShader = this.compileShader(vertexShaderSource, this.gl.VERTEX_SHADER);
        const fragmentShader = this.compileShader(fragmentShaderSource, this.gl.FRAGMENT_SHADER);
        this.program = this.createProgram(vertexShader, fragmentShader);
        this.gl.useProgram(this.program);
    },

    compileShader(source, type) {
        const shader = this.gl.createShader(type);
        this.gl.shaderSource(shader, source);
        this.gl.compileShader(shader);
        if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
            console.error(this.gl.getShaderInfoLog(shader));
            return null;
        }
        return shader;
    },

    createProgram(vertexShader, fragmentShader) {
        const program = this.gl.createProgram();
        this.gl.attachShader(program, vertexShader);
        this.gl.attachShader(program, fragmentShader);
        this.gl.linkProgram(program);
        if (!this.gl.getProgramParameter(program, this.gl.LINK_STATUS)) {
            console.error('Program linking failed');
            return null;
        }
        return program;
    },

    initBuffers() {
        const vertices = new Float32Array([
            // Tetrahedron vertices (positions + colors)
            0.0, 1.0, 0.0, 1.0, 0.0, 0.0,  // Vertex 1 (Red)
            -1.0, -1.0, 1.0, 0.0, 1.0, 0.0, // Vertex 2 (Green)
            1.0, -1.0, 1.0, 0.0, 0.0, 1.0,  // Vertex 3 (Blue)
            0.0, -1.0, -1.0, 1.0, 1.0, 0.0  // Vertex 4 (Yellow)
        ]);

        this.buffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.buffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, vertices, this.gl.STATIC_DRAW);

        this.positionAttribute = this.gl.getAttribLocation(this.program, 'position');
        this.colorAttribute = this.gl.getAttribLocation(this.program, 'color');

        this.gl.vertexAttribPointer(this.positionAttribute, 3, this.gl.FLOAT, false, 24, 0);
        this.gl.vertexAttribPointer(this.colorAttribute, 3, this.gl.FLOAT, false, 24, 12);

        this.gl.enableVertexAttribArray(this.positionAttribute);
        this.gl.enableVertexAttribArray(this.colorAttribute);
    },

    initEventListeners() {
        window.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'ArrowLeft':
                    this.rotationAngleY -= 0.05;
                    break;
                case 'ArrowRight':
                    this.rotationAngleY += 0.05;
                    break;
                case 'ArrowUp':
                    this.rotationAngleX -= 0.05;
                    break;
                case 'ArrowDown':
                    this.rotationAngleX += 0.05;
                    break;
            }
            this.render();
        });
    },

    render() {
        this.gl.clearColor(0.0, 0.0, 0.0, 1.0);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT);

        const modelViewMatrix = mat4.create();
        mat4.rotateX(modelViewMatrix, modelViewMatrix, this.rotationAngleX);
        mat4.rotateY(modelViewMatrix, modelViewMatrix, this.rotationAngleY);

        const modelViewMatrixLocation = this.gl.getUniformLocation(this.program, 'modelViewMatrix');
        this.gl.uniformMatrix4fv(modelViewMatrixLocation, false, modelViewMatrix);

        this.gl.drawArrays(this.gl.TRIANGLES, 0, 12);
    },

    cleanup() {
        // Очистка ресурсов (например, удаление событий, очистка буферов)
        window.removeEventListener('keydown', this.initEventListeners);
        this.gl.deleteBuffer(this.buffer);
        this.gl.deleteProgram(this.program);
    }
};
