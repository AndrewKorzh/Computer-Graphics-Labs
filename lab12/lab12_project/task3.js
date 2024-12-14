let mixedTexturesCube = {
    gl: null,
    program: null,
    buffer: null,
    texture1: null,
    texture2: null,
    blendFactor: 0.5, // Пропорция смешивания текстур
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
        this.initBuffers();  // Метод, вызывающий ошибку
        this.initTextures();
        this.initEventListeners();
        this.render();
    },

    initShaders() {
        const vertexShaderSource = `
            attribute vec4 position;
            attribute vec2 texCoord;
            varying vec2 vTexCoord;
            uniform mat4 modelViewMatrix;
            void main() {
                gl_Position = modelViewMatrix * position;
                vTexCoord = texCoord;
            }
        `;
        const fragmentShaderSource = `
            precision mediump float;
            varying vec2 vTexCoord;
            uniform sampler2D uTexture1;
            uniform sampler2D uTexture2;
            uniform float blendFactor;
            void main() {
                vec4 texColor1 = texture2D(uTexture1, vTexCoord);
                vec4 texColor2 = texture2D(uTexture2, vTexCoord);
                gl_FragColor = mix(texColor1, texColor2, blendFactor);
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
            console.error('Error compiling shader: ' + this.gl.getShaderInfoLog(shader));
        }
        return shader;
    },

    createProgram(vertexShader, fragmentShader) {
        const program = this.gl.createProgram();
        this.gl.attachShader(program, vertexShader);
        this.gl.attachShader(program, fragmentShader);
        this.gl.linkProgram(program);
        if (!this.gl.getProgramParameter(program, this.gl.LINK_STATUS)) {
            console.error('Program linking failed: ' + this.gl.getProgramInfoLog(program));
        }
        return program;
    },

    // Добавление метода initBuffers
    initBuffers() {
        const vertices = new Float32Array([
            -1.0, -1.0, -1.0, 0.0, 0.0,
            1.0, -1.0, -1.0, 1.0, 0.0,
            1.0, 1.0, -1.0, 1.0, 1.0,
            -1.0, 1.0, -1.0, 0.0, 1.0,
            -1.0, -1.0, 1.0, 0.0, 0.0,
            1.0, -1.0, 1.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0, 1.0,
            -1.0, 1.0, 1.0, 0.0, 1.0
        ]);

        const indices = new Uint16Array([
            0, 1, 2, 0, 2, 3,
            4, 5, 6, 4, 6, 7,
            0, 1, 5, 0, 5, 4,
            2, 3, 7, 2, 7, 6,
            1, 2, 6, 1, 6, 5,
            0, 3, 7, 0, 7, 4
        ]);

        this.buffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.buffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, vertices, this.gl.STATIC_DRAW);

        const indexBuffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ELEMENT_ARRAY_BUFFER, indexBuffer);
        this.gl.bufferData(this.gl.ELEMENT_ARRAY_BUFFER, indices, this.gl.STATIC_DRAW);

        const positionAttribute = this.gl.getAttribLocation(this.program, 'position');
        const texCoordAttribute = this.gl.getAttribLocation(this.program, 'texCoord');
        this.gl.vertexAttribPointer(positionAttribute, 3, this.gl.FLOAT, false, 20, 0);
        this.gl.vertexAttribPointer(texCoordAttribute, 2, this.gl.FLOAT, false, 20, 12);

        this.gl.enableVertexAttribArray(positionAttribute);
        this.gl.enableVertexAttribArray(texCoordAttribute);
    },

    initTextures() {
        // Пример загрузки текстур
    },

    initEventListeners() {
        window.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.rotationAngleY -= 0.05;
            if (e.key === 'ArrowRight') this.rotationAngleY += 0.05;
            if (e.key === 'ArrowUp') this.rotationAngleX -= 0.05;
            if (e.key === 'ArrowDown') this.rotationAngleX += 0.05;
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

        this.gl.drawElements(this.gl.TRIANGLES, 36, this.gl.UNSIGNED_SHORT, 0);
    },

    cleanup() {
        this.gl.deleteBuffer(this.buffer);
        this.gl.deleteProgram(this.program);
        this.gl.deleteTexture(this.texture1);
        this.gl.deleteTexture(this.texture2);
    }
};