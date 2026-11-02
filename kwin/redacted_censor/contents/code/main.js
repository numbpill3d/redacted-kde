// SPDX-FileCopyrightText: splicer scorn; window filter after Burn-My-Windows by
// Simon Schneegans, Vlad Zahorodnii and Martin Flöser
// SPDX-License-Identifier: GPL-3.0-or-later
'use strict';

function readRGBA(key, fallback) {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})?([a-f\d]{2})?$/i.exec(
    String(effect.readConfig(key, fallback)));
  if (!m) {
    return [0.6, 0.6, 0.6, 1.0];
  }
  const c = m.slice(1).filter(x => x !== undefined).map(x => parseInt(x, 16) / 255);
  return c.length == 3 ? [c[0], c[1], c[2], 1.0] : [c[1], c[2], c[3], c[0]];
}

const blacklist = [
  'ksmserver ksmserver', 'ksmserver-logout-greeter ksmserver-logout-greeter',
  'ksplashqml ksplashqml'
];

function shouldAnimate(window) {
  if (window.windowClass == 'plasmashell plasmashell' ||
      window.windowClass == 'plasmashell org.kde.plasmashell') {
    return window.hasDecoration;
  }
  if (!window.hasDecoration && window.onAllDesktops) {
    return false;
  }
  if (blacklist.indexOf(window.windowClass) != -1) {
    return false;
  }
  if (window.hasDecoration) {
    return true;
  }
  if (window.popupWindow || window.lockScreen || window.outline || !window.managed) {
    return false;
  }
  return window.normalWindow || window.dialog;
}

class RedactedCensor {
  constructor() {
    effect.configChanged.connect(this.loadConfig.bind(this));
    effects.windowAdded.connect(this.onAdded.bind(this));
    effects.windowClosed.connect(this.onClosed.bind(this));
    effects.windowDataChanged.connect(this.onDataChanged.bind(this));
    this.shader = effect.addFragmentShader(Effect.MapTexture, 'redacted-censor.frag');
    this.loadConfig();
  }

  loadConfig() {
    this.openMs = animationTime(effect.readConfig('OpenDuration', 380));
    this.closeMs = animationTime(effect.readConfig('CloseDuration', 300));
    effect.setUniform(this.shader, 'uColor', readRGBA('Color', '#9a9a9a'));
    effect.setUniform(this.shader, 'uInk', readRGBA('Ink', '#000000'));
  }

  run(window, opening) {
    const ms = opening ? this.openMs : this.closeMs;
    effect.setUniform(this.shader, 'uForOpening', opening ? 1.0 : 0.0);
    effect.setUniform(this.shader, 'uIsFullscreen', window.fullScreen ? 1.0 : 0.0);
    effect.setUniform(this.shader, 'uSeed', Math.random());
    effect.setUniform(this.shader, 'uDuration', ms * 0.001);
    return animate({
      window: window,
      duration: ms,
      animations: [{
        type: Effect.ShaderUniform,
        fragmentShader: this.shader,
        uniform: 'uProgress',
        curve: QEasingCurve.Linear,
        from: 0.0,
        to: 1.0
      }, {
        type: Effect.Scale,
        curve: opening ? QEasingCurve.OutCubic : QEasingCurve.InCubic,
        from: opening ? 0.965 : 1.0,
        to: opening ? 1.0 : 0.965
      }]
    });
  }

  onAdded(window) {
    if (effects.hasActiveFullScreenEffect || !shouldAnimate(window) || !window.visible) {
      return;
    }
    if (effect.isGrabbed(window, Effect.WindowAddedGrabRole)) {
      return;
    }
    window.redIn = this.run(window, true);
  }

  onClosed(window) {
    if (effects.hasActiveFullScreenEffect || !shouldAnimate(window)) {
      return;
    }
    if (!window.visible || window.skipsCloseAnimation) {
      return;
    }
    if (effect.isGrabbed(window, Effect.WindowClosedGrabRole)) {
      return;
    }
    if (window.redIn) {
      cancel(window.redIn);
      delete window.redIn;
    }
    window.redOut = this.run(window, false);
  }

  onDataChanged(window, role) {
    const key = role == Effect.WindowAddedGrabRole ? 'redIn' :
                role == Effect.WindowClosedGrabRole ? 'redOut' : null;
    if (key && window[key] && effect.isGrabbed(window, role)) {
      cancel(window[key]);
      delete window[key];
    }
  }
}

new RedactedCensor();
