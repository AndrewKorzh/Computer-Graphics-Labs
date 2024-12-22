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
uniform vec3 uDirectionalLightColor;      // Цвет Directional Light

uniform vec3 uSpotLightPosition;          // Позиция для Spot Light
uniform vec3 uSpotLightDirection;         // Направление для Spot Light
uniform float uSpotLightAngle;            // Косинус угла конуса Spot Light
uniform vec3 uSpotLightColor;             // Цвет Spot Light

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
    for (int i = 0; i < uLightCount; i++) {
        highp vec3 lightDirection = normalize(uLightPositions[i] - vertexPosition);
        highp float distance = length(uLightPositions[i] - vertexPosition);
        highp float attenuation = 1.0 / (1.0 + 0.1 * distance + 0.01 * distance * distance);

        highp float diffuse = max(dot(transformedNormal, lightDirection), 0.0);

        // Toon Shading: дискретизация яркости
        highp float toonLighting = step(0.3, diffuse) * 0.5 + step(0.6, diffuse) * 0.5;

        lighting += uLightColors[i] * toonLighting * attenuation;
    }

    // Освещение от Directional Light
    if (length(uDirectionalLightDirection) > 0.0) {
        highp vec3 lightDirection = normalize(uDirectionalLightDirection);
        highp float diffuse = max(dot(transformedNormal, lightDirection), 0.0);

        highp float toonLighting = step(0.3, diffuse) * 0.5 + step(0.6, diffuse) * 0.5;
        lighting += uDirectionalLightColor * toonLighting;
    }

    // Освещение от Spot Light
    if (length(uSpotLightPosition) > 0.0) {
        highp vec3 lightDirection = normalize(uSpotLightPosition - vertexPosition);

        // Проверяем, находится ли вершина в пределах угла прожектора
        highp float angle = dot(lightDirection, normalize(-uSpotLightDirection));
        if (angle > uSpotLightAngle) {
            highp float distance = length(uSpotLightPosition - vertexPosition);
            highp float attenuation = 1.0 / (1.0 + 0.1 * distance + 0.01 * distance * distance);

            highp float diffuse = max(dot(transformedNormal, lightDirection), 0.0);

            lighting += uSpotLightColor * diffuse * attenuation;
        }
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