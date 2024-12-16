let gradientCircle = {
    gl: null,
    program: null,
    buffer: null,
    scaleX: 1.0,
    scaleY: 1.0,

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
            uniform mat4 modelViewMatrix;
            void main() {
                gl_Position = modelViewMatrix * position;
            }
        `;
        const fragmentShaderSource = `
            precision mediump float;
            uniform vec2 scale; // масштабирование
            void main() {
                vec2 uv = gl_FragCoord.xy / vec2(800.0, 600.0); // Нормализуем координаты пикселя
                uv = uv * 2.0 - 1.0; // Преобразуем в диапазон [-1, 1]
                uv.x *= scale.x; // Применяем масштаб по X
                uv.y *= scale.y; // Применяем масштаб по Y
                float dist = length(uv); // Рассчитываем расстояние от центра

                float hue = dist * 360.0; // Градиент по Hue
                vec3 color = hsv2rgb(vec3(hue, 1.0, 1.0)); // Преобразуем в RGB
                gl_FragColor = vec4(color, 1.0); // Устанавливаем цвет пикселя
            }

            vec3 hsv2rgb(vec3 c) {
                float h = c.x / 60.0;
                float x = c.z * (1.0 - abs(mod(h, 2.0) - 1.0));
                vec3 rgb = vec3(0.0);
                if (h < 1.0) rgb = vec3(c.z, x, 0.0);
                else if (h < 2.0) rgb = vec3(x, c.z, 0.0);
                else if (h < 3.0) rgb = vec3(0.0, c.z, x);
                else if (h < 4.0) rgb = vec3(0.0, x, c.z);
                else if (h < 5.0) rgb = vec3(x, 0.0, c.z);
                else rgb = vec3(c.z, 0.0, x);
                return rgb;
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
            // Используем прямоугольник для покрытия всей области
            -1.0, -1.0, 0.0,
            1.0, -1.0, 0.0,
            1.0, 1.0, 0.0,
            -1.0, 1.0, 0.0
        ]);

        this.buffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.buffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, vertices, this.gl.STATIC_DRAW);

        const positionAttribute = this.gl.getAttribLocation(this.program, 'position');
        this.gl.vertexAttribPointer(positionAttribute, 3, this.gl.FLOAT, false, 12, 0);
        this.gl.enableVertexAttribArray(positionAttribute);

        this.scaleUniformLocation = this.gl.getUniformLocation(this.program, 'scale');
    },

    initEventListeners() {
        window.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.scaleX *= 0.9; // Уменьшаем масштаб по оси X
            if (e.key === 'ArrowRight') this.scaleX *= 1.1; // Увеличиваем масштаб по оси X
            if (e.key === 'ArrowUp') this.scaleY *= 1.1; // Увеличиваем масштаб по оси Y
            if (e.key === 'ArrowDown') this.scaleY *= 0.9; // Уменьшаем масштаб по оси Y
            this.render();
        });
    },

    render() {
        this.gl.clearColor(0.0, 0.0, 0.0, 1.0);
        this.gl.clear(this.gl.COLOR_BUFFER_BIT);

        this.gl.uniform2fv(this.scaleUniformLocation, [this.scaleX, this.scaleY]);

        this.gl.drawArrays(this.gl.TRIANGLE_FAN, 0, 4);
    },

    cleanup() {
        // Очистка (например, удаление буферов, сброс состояния)
    }
};
