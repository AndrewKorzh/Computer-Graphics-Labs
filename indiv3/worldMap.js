const canvas = document.getElementById('drawingCanvas');
const ctx = canvas.getContext('2d');

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function drawPoint(position, color) {
    const x = position[0] * canvas.width;
    const y = (1 - position[1]) * canvas.height;
    // const y = position[1] * canvas.height;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
}