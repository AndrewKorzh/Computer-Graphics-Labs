let texturedCube = {
    gl: null,
    program: null,
    buffer: null,
    texture: null,
    colorBlend: 0.5, // Пропорция смешивания цвета и текстуры
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
            uniform sampler2D uTexture;
            uniform float colorBlend;
            void main() {
                vec4 texColor = texture2D(uTexture, vTexCoord);
                vec4 color = vec4(1.0, 0.0, 0.0, 1.0); // Red color
                gl_FragColor = mix(color, texColor, colorBlend);
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
        }
        return program;
    },

    initBuffers() {
        const vertices = new Float32Array([
            // Cube vertices (position and texture coordinates)
            -1.0, -1.0, 1.0, 0.0, 0.0,
            1.0, -1.0, 1.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0, 1.0,
            -1.0, 1.0, 1.0, 0.0, 1.0,
            -1.0, -1.0, -1.0, 0.0, 0.0,
            1.0, -1.0, -1.0, 1.0, 0.0,
            1.0, 1.0, -1.0, 1.0, 1.0,
            -1.0, 1.0, -1.0, 0.0, 1.0
        ]);

        const indices = new Uint16Array([
            0, 1, 2, 0, 2, 3,
            4, 5, 6, 4, 6, 7,
            0, 1, 5, 0, 5, 4,
            3, 2, 6, 3, 6, 7,
            1, 2, 6, 1, 6, 5,
            0, 3, 7, 0, 7, 4
        ]);

        this.buffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.buffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, vertices, this.gl.STATIC_DRAW);

        this.positionAttribute = this.gl.getAttribLocation(this.program, 'position');
        this.texCoordAttribute = this.gl.getAttribLocation(this.program, 'texCoord');
        this.gl.vertexAttribPointer(this.positionAttribute, 3, this.gl.FLOAT, false, 20, 0);
        this.gl.vertexAttribPointer(this.texCoordAttribute, 2, this.gl.FLOAT, false, 20, 12);

        this.gl.enableVertexAttribArray(this.positionAttribute);
        this.gl.enableVertexAttribArray(this.texCoordAttribute);

        this.indexBuffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ELEMENT_ARRAY_BUFFER, this.indexBuffer);
        this.gl.bufferData(this.gl.ELEMENT_ARRAY_BUFFER, indices, this.gl.STATIC_DRAW);
    },

    initTextures() {
        this.texture = this.gl.createTexture();
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.texture);

        const img = new Image();
        img.src = '/textures/max.jpg';
        img.onload = () => {
            this.gl.texImage2D(this.gl.TEXTURE_2D, 0, this.gl.RGBA, this.gl.RGBA, this.gl.UNSIGNED_BYTE, img);
            this.gl.generateMipmap(this.gl.TEXTURE_2D);
            this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_MIN_FILTER, this.gl.LINEAR_MIPMAP_LINEAR);
            this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_MAG_FILTER, this.gl.LINEAR);
            this.render();
        };
    },

    initEventListeners() {
        window.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.rotationAngleY -= 0.05;
            if (e.key === 'ArrowRight') this.rotationAngleY += 0.05;
            if (e.key === 'ArrowUp') this.rotationAngleX -= 0.05;
            if (e.key === 'ArrowDown') this.rotationAngleX += 0.05;
            if (e.key === '+') this.colorBlend = Math.min(1.0, this.colorBlend + 0.05);
            if (e.key === '-') this.colorBlend = Math.max(0.0, this.colorBlend - 0.05);
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
        const colorBlendLocation = this.gl.getUniformLocation(this.program, 'colorBlend');
        const textureLocation = this.gl.getUniformLocation(this.program, 'uTexture');

        this.gl.uniformMatrix4fv(modelViewMatrixLocation, false, modelViewMatrix);
        this.gl.uniform1f(colorBlendLocation, this.colorBlend);
        this.gl.activeTexture(this.gl.TEXTURE0);
        this.gl.bindTexture(this.gl.TEXTURE_2D, this.texture);
        this.gl.uniform1i(textureLocation, 0);

        this.gl.drawElements(this.gl.TRIANGLES, 36, this.gl.UNSIGNED_SHORT, 0);
    },

    cleanup() {
        // Cleanup logic here (e.g., removing event listeners, clearing buffers)
    }
};
