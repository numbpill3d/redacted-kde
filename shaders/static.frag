#version 440
// Redacted panel widget: a tiny screen of live static with a censor bar.
// SPDX-FileCopyrightText: splicer scorn
// SPDX-License-Identifier: GPL-3.0-or-later
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float frame;
    float px;        // item size in pixels (square)
    float slip;      // bar offset, -1..1
};
float hash12(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}
void main() {
    vec2 cell = floor(qt_TexCoord0 * px / 2.0);          // 2 px static grains
    float n = hash12(cell + vec2(frame * 13.0, frame * 7.0));
    float v = (8.0 + 70.0 * n * n) / 255.0;
    if (mod(floor(qt_TexCoord0.y * px), 3.0) == 2.0) v *= 0.6;
    float y = qt_TexCoord0.y - 0.5 - slip * 0.22;
    if (abs(y) < 0.15) v = (y < -0.13) ? 33.0 / 255.0 : 0.0;
    // rounded-ish square: fade the corners
    vec2 d = abs(qt_TexCoord0 - 0.5) * 2.0;
    float a = 1.0 - smoothstep(0.86, 1.0, max(d.x, d.y));
    fragColor = vec4(v, v, v, 1.0) * a * qt_Opacity;
}
