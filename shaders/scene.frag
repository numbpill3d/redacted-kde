#version 440
// Redacted scene: the grey face under static, mosaic, a slipping censor bar
// and a dissociated double. Works in 1920x1080 "scene pixels"; QML scales the
// item to cover the screen.
// SPDX-FileCopyrightText: splicer scorn
// SPDX-License-Identifier: GPL-3.0-or-later

layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float time;      // seconds (advances in 1/12 s steps)
    float frame;     // whole frames
    float resolve;   // 1 = normal; 0 = everything one coarse mosaic (splash start)
    float glitch;    // 0..1 burst
    float barSlip;   // px the censor bar is knocked off the eyes, perpendicular
    float bright;    // overall gain (lock screen / login dim it)
};
layout(binding = 1) uniform sampler2D face;

const vec2 RES = vec2(1920.0, 1080.0);
const vec2 EYE_L = vec2(298.0, 343.0);
const vec2 EYE_R = vec2(679.0, 552.0);

float hash12(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float faceAt(vec2 px) {
    if (px.x < 0.0 || px.y < 0.0 || px.x >= RES.x || px.y >= RES.y) return 0.0;
    return texture(face, px / RES).r;
}

// quantise px to a block grid inside a rectangle, else leave it
vec2 mosaic(vec2 px, vec4 r, float b) {
    if (px.x >= r.x && px.y >= r.y && px.x < r.z && px.y < r.w)
        return (floor(px / b) + 0.5) * b;
    return px;
}

void main() {
    vec2 px = qt_TexCoord0 * RES;
    float t = time;

    // torn rows: bands slide sideways for a few frames at a time
    float bandH = 3.0 + 6.0 * floor(hash12(vec2(floor(px.y / 9.0), 7.0)) * 3.0);
    float band = floor(px.y / bandH);
    float slot = floor(frame / 3.0);
    float hb = hash12(vec2(band, slot));
    float tearP = 0.012 + glitch * 0.22;
    if (hb < tearP) px.x += (hash12(vec2(band, slot + 91.0)) - 0.5) * (60.0 + 220.0 * glitch);
    // a glitch burst also shakes the whole frame a little
    px.y += glitch * (hash12(vec2(slot, 3.0)) - 0.5) * 10.0;

    // mosaic: fixed patches (as on the still) + one that wanders over the face
    vec2 q = px;
    float coarse = mix(96.0, 1.0, resolve);
    if (coarse > 1.5) q = (floor(q / coarse) + 0.5) * coarse;
    q = mosaic(q, vec4(456.0, 312.0, 936.0, 768.0), 24.0);
    q = mosaic(q, vec4(168.0, 744.0, 552.0, 1008.0), 12.0);
    q = mosaic(q, vec4(96.0, 480.0, 264.0, 744.0), 6.0);
    vec2 wc = vec2(430.0 + 260.0 * sin(t * 0.071), 560.0 + 300.0 * sin(t * 0.053 + 1.7));
    float wb = 8.0 + 8.0 * floor(2.99 * (0.5 + 0.5 * sin(t * 0.37)));
    q = mosaic(q, vec4(wc - vec2(150.0, 90.0), wc + vec2(150.0, 90.0)), wb);

    float v = faceAt(q);

    // dissociated double: drifts slowly off the face, flickering
    vec2 drift = vec2(46.0 + 22.0 * sin(t * 0.21), -10.0 + 9.0 * sin(t * 0.17 + 2.0));
    float flick = 0.36 + 0.10 * sin(t * 1.3) + 0.08 * hash12(vec2(slot, 11.0));
    v = max(v, faceAt(px - drift) * flick);

    // censor bar over both eyes; slips perpendicular when knocked
    vec2 c = 0.5 * (EYE_L + EYE_R);
    vec2 ax = normalize(EYE_R - EYE_L);
    vec2 nm = vec2(-ax.y, ax.x);
    vec2 d = px - c;
    float along = dot(d, ax), across = dot(d, nm) - barSlip;
    float halfL = 0.5 * distance(EYE_L, EYE_R) + 150.0;
    if (abs(along) < halfL && abs(across) < 60.0) {
        v = 0.0;
        if (across < -59.0) v = 33.0 / 255.0;       // its one lit edge
    }

    // scanlines
    if (mod(floor(px.y), 3.0) == 2.0) v *= 0.72;

    // static: sparse bright specks that re-roll every frame, plus a rolling tracking band
    vec2 cell = floor(qt_TexCoord0 * RES);
    float n = hash12(cell + vec2(frame * 17.0, frame * 5.0));
    float bandY = mod(t * 38.0, RES.y + 240.0) - 120.0;
    float inBand = 1.0 - smoothstep(0.0, 70.0, abs(qt_TexCoord0.y * RES.y - bandY));
    float speck = step(1.0 - (0.012 + 0.05 * inBand + 0.08 * glitch), n);
    v = max(v, speck * (18.0 + 52.0 * hash12(cell + frame)) / 255.0);
    v += inBand * 4.0 / 255.0;
    // fine dither so the black never sits perfectly flat
    v += (hash12(cell * 1.37 + frame) - 0.5) * 2.0 / 255.0;

    v = clamp(v * bright, 0.0, 1.0);
    fragColor = vec4(v, v, v, 1.0) * qt_Opacity;
}
