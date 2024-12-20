const vertexShaderSource = `
attribute vec3 aVertexPosition;
attribute vec3 aNormal;
attribute vec2 aTextureCoord;

uniform mat4 uModelViewMatrix;
uniform mat4 uProjectionMatrix;
uniform mat4 uNormalMatrix;

uniform vec3 uLightPositions[10];  // До 10 источников света (Point Lights)
uniform vec3 uLightColors[10];     // Цвета источников света
uniform int uLightCount;           // Количество активных источников света

// Для Directional и Spot Light
uniform vec3 uDirectionalLightDirection;  // Направление для Directional Light
uniform vec3 uDirectionalLightColor;     // Цвет Directional Light

uniform vec3 uSpotLightPosition;         // Позиция для Spot Light
uniform vec3 uSpotLightDirection;        // Направление для Spot Light
uniform float uSpotLightAngle;           // Угол конуса Spot Light
uniform vec3 uSpotLightColor;            // Цвет Spot Light

varying highp vec3 vLighting;
varying highp vec2 vTextureCoord;

void main(void) {
    gl_Position = uProjectionMatrix * uModelViewMatrix * vec4(aVertexPosition, 1.0);
    vTextureCoord = aTextureCoord;

    highp vec3 transformedNormal = normalize(vec3(uNormalMatrix * vec4(aNormal, 0.0)));
    highp vec3 vertexPosition = vec3(uModelViewMatrix * vec4(aVertexPosition, 1.0));

    // Базовая освещенность (окружающий свет)
    highp vec3 ambientLight = vec3(0.2, 0.2, 0.2);
    highp vec3 lighting = ambientLight;

    // Освещение от Point Lights
    for (int i = 0; i < 10; i++) {
        if (i >= uLightCount) break; // Используем только активные источники света

        // Направление света
        highp vec3 lightDirection = normalize(uLightPositions[i] - vertexPosition);

        // Диффузное освещение
        highp float diffuse = max(dot(transformedNormal, lightDirection), 0.0);

        // Toon Shading: делаем освещенность дискретной, используя несколько уровней яркости
        highp float toonLighting = step(0.5, diffuse);  // Простая дискретизация

        lighting += uLightColors[i] * toonLighting;
    }

    // Освещение от Directional Light
    if (length(uDirectionalLightDirection) > 0.0) {
        highp vec3 lightDirection = normalize(uDirectionalLightDirection);
        highp float diffuse = max(dot(transformedNormal, lightDirection), 0.0);

        // Toon Shading
        highp float toonLighting = step(0.5, diffuse);  // Простая дискретизация
        lighting += uDirectionalLightColor * toonLighting;
    }


    
    if (length(uSpotLightPosition) > 0.0) {
        // Направление света от прожектора к вершине
        highp vec3 lightDirection = normalize(uSpotLightPosition - vertexPosition);

        // Диффузное освещение
        highp float diffuse = max(dot(transformedNormal, lightDirection), 0.0);

        // Затухание на основе расстояния
        highp float distance = length(uSpotLightPosition - vertexPosition);
        highp float attenuation = 1.0 / (1.0 + 0.1 * distance + 0.01 * distance * distance);

        // Итоговое освещение от Spot Light
        lighting += uSpotLightColor * diffuse * attenuation;
    }


    vLighting = lighting;
}
`;






const fragmentShaderSource = `
varying highp vec3 vLighting;
varying highp vec2 vTextureCoord;

uniform sampler2D uSampler;

void main(void) {
    highp vec4 texelColor = texture2D(uSampler, vTextureCoord);
    gl_FragColor = vec4(texelColor.rgb * vLighting, texelColor.a);
}
`;