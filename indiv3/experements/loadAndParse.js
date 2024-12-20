function parseOBJ(text) {
    const vertices = [];
    const normals = [];
    const textureCoords = [];
    const vertexIndices = [];

    const lines = text.split('\n');
    for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        if (parts[0] === 'v') {
            vertices.push(...parts.slice(1).map(Number));
        } else if (parts[0] === 'vn') {
            normals.push(...parts.slice(1).map(Number));
        } else if (parts[0] === 'vt') {
            textureCoords.push(...parts.slice(1).map(Number));
        } else if (parts[0] === 'f') {
            const face = parts.slice(1).map(part => part.split('/').map(Number));
            for (let i = 1; i < face.length - 1; i++) {
                vertexIndices.push(face[0], face[i], face[i + 1]);
            }
        }
    }

    const unpackedVertices = [];
    const unpackedNormals = [];
    const unpackedTexCoords = [];

    for (const [v, t, n] of vertexIndices) {
        unpackedVertices.push(
            vertices[(v - 1) * 3],
            vertices[(v - 1) * 3 + 1],
            vertices[(v - 1) * 3 + 2]
        );
        unpackedTexCoords.push(
            textureCoords[(t - 1) * 2],
            1.0 - textureCoords[(t - 1) * 2 + 1]
        );
        unpackedNormals.push(
            normals[(n - 1) * 3],
            normals[(n - 1) * 3 + 1],
            normals[(n - 1) * 3 + 2]
        );
    }

    return {
        vertices: unpackedVertices,
        normals: unpackedNormals,
        textureCoords: unpackedTexCoords,
    };
}

function loadObjFile(url) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, false); // false делает запрос синхронным
    xhr.send();

    if (xhr.status === 200) {
        return parseOBJ(xhr.responseText);
    } else {
        throw new Error('Ошибка загрузки файла');
    }
}

function loadTexture(gl, url) {
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);

    const pixel = new Uint8Array([255, 255, 255, 255]);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, pixel);

    const image = new Image();
    image.onload = () => {
        gl.bindTexture(gl.TEXTURE_2D, texture);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
        gl.generateMipmap(gl.TEXTURE_2D);
    };
    image.src = url;

    return texture;
}



