function multiplyMatrixVector(matrix, vector) {
    return [
        matrix[0][0] * vector[0] + matrix[0][1] * vector[1] + matrix[0][2] * vector[2],
        matrix[1][0] * vector[0] + matrix[1][1] * vector[1] + matrix[1][2] * vector[2],
        matrix[2][0] * vector[0] + matrix[2][1] * vector[1] + matrix[2][2] * vector[2],
    ];
}

// Умножение двух матриц
function multiplyMatrices(a, b) {
    return a.map((row, i) =>
        b[0].map((_, j) =>
            row.reduce((sum, _, k) => sum + a[i][k] * b[k][j], 0)
        )
    );
}


function rotatePointsInPlace(points, angles, rotationCenter = [0, 0, 0]) {
    const { sin, cos } = Math;
    const [alpha, beta, gamma] = angles; // Углы вращения в радианах вокруг осей X, Y, Z соответственно
    const [cx, cy, cz] = rotationCenter; // Координаты точки вращения

    // Матрицы вращения вокруг осей
    const rotationX = [
        [1, 0, 0],
        [0, cos(alpha), -sin(alpha)],
        [0, sin(alpha), cos(alpha)],
    ];

    const rotationY = [
        [cos(beta), 0, sin(beta)],
        [0, 1, 0],
        [-sin(beta), 0, cos(beta)],
    ];

    const rotationZ = [
        [cos(gamma), -sin(gamma), 0],
        [sin(gamma), cos(gamma), 0],
        [0, 0, 1],
    ];

    // Комбинированная матрица вращения: R = Rz * Ry * Rx
    const combinedRotation = multiplyMatrices(
        multiplyMatrices(rotationZ, rotationY),
        rotationX
    );

    // Модифицируем точки на месте
    points.forEach((point, index) => {
        // Сдвигаем точку относительно центра вращения
        const [x, y, z] = point;
        const shiftedPoint = [x - cx, y - cy, z - cz];

        // Применяем вращение
        const [nx, ny, nz] = multiplyMatrixVector(combinedRotation, shiftedPoint);

        // Возвращаем точку на исходное место
        points[index][0] = nx + cx;
        points[index][1] = ny + cy;
        points[index][2] = nz + cz;
    });
}


function euclideanDistance(point1, point2) {
    const sumOfSquares = point1.reduce((sum, value, index) => {
        return sum + Math.pow(value - point2[index], 2);
    }, 0);
    return Math.sqrt(sumOfSquares);
}



function findClosestArray(targetArray, arrayOfArrays) {
    let closestArray = null;
    let closestDistance = Infinity;

    let i = 0;
    let min_i = 0;
    for (const array of arrayOfArrays) {
        const distance = euclideanDistance(targetArray, array);
        if (distance < closestDistance) {
            closestDistance = distance;
            closestArray = array;
            min_i = i;
        }
        i += 1;
    }

    return min_i;
}

