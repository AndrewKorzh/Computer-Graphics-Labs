const canvas = document.getElementById("webgl-canvas");
const gl = canvas.getContext("webgl");

if (!gl) {
    alert("WebGL not supported!");
    throw new Error("WebGL not supported");
}

// Vertex shader source
const vertexShaderSource = `
    attribute vec3 coord;
    attribute vec2 texCoord;
    attribute vec3 vertexColor;
    uniform mat4 MVP;
    varying vec2 vTexCoord;
    varying vec3 vColor;
    void main() {
        gl_Position = MVP * vec4(coord, 1.0);
        vTexCoord = texCoord;
        vColor = vertexColor;
    }
`;

// Fragment shader source
const fragmentShaderSource = `
    precision mediump float;
    uniform vec4 color;
    uniform sampler2D textureSampler1;
    uniform sampler2D textureSampler2;
    uniform float mixRatio;
    varying vec2 vTexCoord;
    varying vec3 vColor;
    void main() {
        vec4 textureColor1 = texture2D(textureSampler1, vTexCoord);
        vec4 textureColor2 = texture2D(textureSampler2, vTexCoord);
        vec4 vertexColor = vec4(vColor, 1.0);
        gl_FragColor = mix(textureColor1, textureColor2, mixRatio);
    }
`;

// Compile shader function
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
const texCoordLoc = gl.getAttribLocation(program, "texCoord");
const colorLoc = gl.getUniformLocation(program, "color");
const vertexColorLoc = gl.getAttribLocation(program, "vertexColor");
const MVPLoc = gl.getUniformLocation(program, "MVP");
const textureSamplerLoc1 = gl.getUniformLocation(program, "textureSampler1");
const textureSamplerLoc2 = gl.getUniformLocation(program, "textureSampler2");
const mixRatioLoc = gl.getUniformLocation(program, "mixRatio");

// Cube: vertices and texture coordinates
const vertices = new Float32Array([
    // Coordinates (x, y, z)            // Texture coordinates (u, v)        // Colors (r, g, b)
    // Front face
    -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0,
    0.5, -0.5, 0.5, 1.0, 0.0, 1.0, 1.0, 0.0,
    0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 0.0,
    -0.5, 0.5, 0.5, 0.0, 1.0, 1.0, 1.0, 1.0,
    // Back face
    -0.5, -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0,
    0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 1.0,
    0.5, 0.5, -0.5, 1.0, 1.0, 0.0, 1.0, 0.0,
    -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0,
    // Left face
    -0.5, -0.5, -0.5, 0.0, 0.0, 1.0, 1.0, 0.0,
    -0.5, -0.5, 0.5, 1.0, 0.0, 1.0, 0.0, 0.0,
    -0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0,
    -0.5, 0.5, -0.5, 0.0, 1.0, 1.0, 0.0, 1.0,
    // Right face
    0.5, -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 1.0,
    0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
    0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 0.0, 0.0,
    0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
    // Top face
    -0.5, 0.5, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.5, 0.5, -0.5, 1.0, 0.0, 1.0, 0.0, 1.0,
    0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 1.0, 0.0,
    -0.5, 0.5, 0.5, 0.0, 1.0, 1.0, 0.0, 1.0,
    // Bottom face
    -0.5, -0.5, -0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
    0.5, -0.5, -0.5, 1.0, 0.0, 1.0, 0.0, 1.0,
    0.5, -0.5, 0.5, 1.0, 1.0, 0.0, 0.0, 0.0,
    -0.5, -0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0
]);

const indices = new Uint16Array([
    0, 1, 2, 2, 3, 0,  // Front face
    4, 5, 6, 6, 7, 4,  // Back face
    8, 9, 10, 10, 11, 8, // Left face
    12, 13, 14, 14, 15, 12, // Right face
    16, 17, 18, 18, 19, 16, // Top face
    20, 21, 22, 22, 23, 20  // Bottom face
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
gl.vertexAttribPointer(coordLoc, 3, gl.FLOAT, false, 32, 0);

gl.enableVertexAttribArray(texCoordLoc);
gl.vertexAttribPointer(texCoordLoc, 2, gl.FLOAT, false, 32, 12);

gl.enableVertexAttribArray(vertexColorLoc);
gl.vertexAttribPointer(vertexColorLoc, 3, gl.FLOAT, false, 32, 20);

// Load textures
const texture1 = gl.createTexture();
const image1 = new Image();
image1.src = "textures/forest.jpg"; // First texture
image1.onload = () => {
    gl.bindTexture(gl.TEXTURE_2D, texture1);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image1);
    gl.generateMipmap(gl.TEXTURE_2D);
};

const texture2 = gl.createTexture();
const image2 = new Image();
image2.src = "textures/max.jpg"; // Second texture
image2.onload = () => {
    gl.bindTexture(gl.TEXTURE_2D, texture2);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image2);
    gl.generateMipmap(gl.TEXTURE_2D);
};

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
let mixRatio = 0.5; // Initial texture-to-texture ratio

// Speed of rotation and mixing
const rotationSpeed = 2;
const mixSpeed = 0.01;

// Track pressed keys
const keys = {};
document.addEventListener("keydown", (event) => {
    keys[event.key] = true;
});
document.addEventListener("keyup", (event) => {
    keys[event.key] = false;
});

// Handle input
function handleInput() {
    if (keys["ArrowUp"]) angleX -= rotationSpeed;
    if (keys["ArrowDown"]) angleX += rotationSpeed;
    if (keys["ArrowLeft"]) angleY -= rotationSpeed;
    if (keys["ArrowRight"]) angleY += rotationSpeed;

    if (keys["z"]) mixRatio = Math.min(mixRatio + mixSpeed, 1.0);
    if (keys["x"]) mixRatio = Math.max(mixRatio - mixSpeed, 0.0);
}

// Render function
function render() {
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    handleInput();

    const MVP = createMVPMatrix(angleX, angleY, angleZ, scaleX, scaleY, scaleZ);
    gl.uniformMatrix4fv(MVPLoc, false, MVP);
    gl.uniform4f(colorLoc, 0.4, 0.0, 0.3, 1.0);
    gl.uniform1f(mixRatioLoc, mixRatio);

    // Set texture samplers
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, texture1);
    gl.uniform1i(textureSamplerLoc1, 0);

    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, texture2);
    gl.uniform1i(textureSamplerLoc2, 1);

    gl.drawElements(gl.TRIANGLES, indices.length, gl.UNSIGNED_SHORT, 0);
    requestAnimationFrame(render);
}

// Start rendering
render();
