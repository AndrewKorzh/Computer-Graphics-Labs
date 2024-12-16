const canvas = document.getElementById("webgl-canvas");
const gl = canvas.getContext("webgl");

if (!gl) {
    alert("WebGL not supported!");
    throw new Error("WebGL not supported");
}

// Vertex shader source
const vertexShaderSource = `
    attribute vec3 coord;
    uniform mat4 MVP;
    void main() {
        gl_Position = MVP * vec4(coord, 1.0);
    }
`;

// Fragment shader source
const fragmentShaderSource = `
    precision mediump float;
    uniform vec4 color;
    void main() {
        gl_FragColor = color;
    }
`;

// Compile shader
function compileShader(type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error("Shader compile failed: ", gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
    }
    return shader;
}

// Initialize shaders
const vertexShader = compileShader(gl.VERTEX_SHADER, vertexShaderSource);
const fragmentShader = compileShader(gl.FRAGMENT_SHADER, fragmentShaderSource);

const program = gl.createProgram();
gl.attachShader(program, vertexShader);
gl.attachShader(program, fragmentShader);
gl.linkProgram(program);
if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    console.error("Program link failed: ", gl.getProgramInfoLog(program));
}

// Get attribute and uniform locations
const coordLoc = gl.getAttribLocation(program, "coord");
const colorLoc = gl.getUniformLocation(program, "color");
const MVPLoc = gl.getUniformLocation(program, "MVP");

// Cube vertices
const vertices = new Float32Array([
    -0.5, -0.5, -0.5,
    0.5, -0.5, -0.5,
    0.5, 0.5, -0.5,
    -0.5, 0.5, -0.5,
    -0.5, -0.5, 0.5,
    0.5, -0.5, 0.5,
    0.5, 0.5, 0.5,
    -0.5, 0.5, 0.5,
]);

const indices = new Uint16Array([
    0, 1, 2, 2, 3, 0,
    4, 5, 6, 6, 7, 4,
    0, 1, 5, 5, 4, 0,
    2, 3, 7, 7, 6, 2,
    0, 3, 7, 7, 4, 0,
    1, 2, 6, 6, 5, 1,
]);

// Create and bind buffers
const vertexBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

const indexBuffer = gl.createBuffer();
gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indexBuffer);
gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW);

// Enable attributes
gl.useProgram(program);
gl.enableVertexAttribArray(coordLoc);
gl.vertexAttribPointer(coordLoc, 3, gl.FLOAT, false, 0, 0);

// Set clear color
gl.clearColor(0.0, 0.0, 0.0, 1.0);
gl.enable(gl.DEPTH_TEST);

// Matrices for transformations
function createMVPMatrix(angleX, angleY, angleZ, scaleX, scaleY, scaleZ) {
    const radians = (angle) => angle * Math.PI / 180;

    const projection = mat4.perspective([], Math.PI / 4, canvas.width / canvas.height, 0.1, 100.0);
    const view = mat4.lookAt([], [0, 2, 4], [0, 0, 0], [0, 1, 0]);
    const model = mat4.create();

    mat4.rotateX(model, model, radians(angleX));
    mat4.rotateY(model, model, radians(angleY));
    mat4.rotateZ(model, model, radians(angleZ));
    mat4.scale(model, model, [scaleX, scaleY, scaleZ]);

    const MVP = mat4.create();
    mat4.multiply(MVP, projection, view);
    mat4.multiply(MVP, MVP, model);

    return MVP;
}

// Animation parameters
let angleX = 0, angleY = 0, angleZ = 0;
let scaleX = 1, scaleY = 1, scaleZ = 1;

// Speed of rotation and scaling
const rotationSpeed = 2; // degrees per frame
const scaleSpeed = 0.05; // scale factor per frame

// Track pressed keys
const keys = {};

// Event listeners for key presses
document.addEventListener("keydown", (event) => {
    keys[event.key] = true;
});
document.addEventListener("keyup", (event) => {
    keys[event.key] = false;
});

// Function to handle input
function handleInput() {
    // Rotation
    if (keys["ArrowUp"]) angleX -= rotationSpeed; // Rotate up
    if (keys["ArrowDown"]) angleX += rotationSpeed; // Rotate down
    if (keys["ArrowLeft"]) angleY -= rotationSpeed; // Rotate left
    if (keys["ArrowRight"]) angleY += rotationSpeed; // Rotate right

    // Scaling
    if (keys["z"]) { // Zoom in
        scaleX += scaleSpeed;
        scaleY += scaleSpeed;
        scaleZ += scaleSpeed;
    }
    if (keys["x"]) { // Zoom out
        scaleX = Math.max(scaleX - scaleSpeed, 0.1); // Prevent scaling to 0
        scaleY = Math.max(scaleY - scaleSpeed, 0.1);
        scaleZ = Math.max(scaleZ - scaleSpeed, 0.1);
    }
}

// Render function
function render() {
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    handleInput(); // Process keyboard input

    const MVP = createMVPMatrix(angleX, angleY, angleZ, scaleX, scaleY, scaleZ);
    gl.uniformMatrix4fv(MVPLoc, false, MVP);

    gl.uniform4f(colorLoc, 0.4, 0.0, 0.3, 1.0);

    gl.drawElements(gl.TRIANGLES, indices.length, gl.UNSIGNED_SHORT, 0);
    requestAnimationFrame(render);
}

// Start rendering
render();