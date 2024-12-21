const vertexShaderSource = `
attribute vec3 aVertexPosition;
attribute vec3 aNormal;
attribute vec2 aTextureCoord;

uniform mat4 uModelViewMatrix;
uniform mat4 uProjectionMatrix;
uniform mat4 uNormalMatrix;

uniform vec3 uLightPositions[10];
uniform vec3 uLightColors[10];
uniform int uLightCount;

uniform vec3 uDirectionalLightDirection;
uniform vec3 uDirectionalLightColor;

uniform vec3 uSpotLightPosition;
uniform vec3 uSpotLightDirection;
uniform float uSpotLightAngle;
uniform float uSpotLightSmoothness;
uniform vec3 uSpotLightColor;

varying highp vec3 vLighting;
varying highp vec2 vTextureCoord;

void main(void) {
    gl_Position = uProjectionMatrix * uModelViewMatrix * vec4(aVertexPosition, 1.0);
    vTextureCoord = aTextureCoord;

    highp vec3 transformedNormal = normalize(vec3(uNormalMatrix * vec4(aNormal, 0.0)));
    highp vec3 vertexPosition = vec3(uModelViewMatrix * vec4(aVertexPosition, 1.0));

    // Ambient Light
    highp vec3 ambientLight = vec3(0.2, 0.2, 0.2);
    highp vec3 lighting = ambientLight;

    // Point Lights
    for (int i = 0; i < 10; i++) {
        if (i >= uLightCount) break;

        highp vec3 lightDirection = normalize(uLightPositions[i] - vertexPosition);
        highp float diffuse = max(dot(transformedNormal, lightDirection), 0.0);

        highp float toonLighting = step(0.3, diffuse) + step(0.6, diffuse);
        lighting += uLightColors[i] * toonLighting;
    }

    // Directional Light
    if (uDirectionalLightColor != vec3(0.0)) {
        highp vec3 lightDirection = normalize(uDirectionalLightDirection);
        highp float diffuse = max(dot(transformedNormal, lightDirection), 0.0);

        highp float toonLighting = step(0.3, diffuse) + step(0.6, diffuse);
        lighting += uDirectionalLightColor * toonLighting;
    }

    // Spot Light
    if (uSpotLightColor != vec3(0.0)) {
        highp vec3 lightDirection = normalize(uSpotLightPosition - vertexPosition);
        highp float spotEffect = dot(lightDirection, normalize(-uSpotLightDirection));

        // Плавное затухание света на границах угла
        if (spotEffect > uSpotLightAngle) {
            highp float smoothEdge = (spotEffect - uSpotLightAngle) / uSpotLightSmoothness;
            highp float attenuation = max(0.0, min(1.0, smoothEdge));

            highp float diffuse = max(dot(transformedNormal, lightDirection), 0.0);
            highp float distance = length(uSpotLightPosition - vertexPosition);
            highp float distanceAttenuation = 1.0 / (1.0 + 0.1 * distance + 0.01 * distance * distance);

            lighting += uSpotLightColor * diffuse * attenuation * distanceAttenuation;
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