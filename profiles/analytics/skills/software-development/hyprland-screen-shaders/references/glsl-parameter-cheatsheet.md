# GLSL Parameter Cheat Sheet

## Gamma
- `pow(color, vec3(GAMMA))`
- `< 1.0` brightens midtones
- `> 1.0` darkens midtones
- `1.0` = no change

## Vibrance / Saturation
- `mix(vec3(y), pix.rgb, VIBRANCE)` where `y` is luma
- `1.0` = unchanged saturation
- `0.0` = full grayscale
- `0.65–0.85` = subtle to moderate desaturation

## Contrast
- `(color - 0.5) * CONTRAST + 0.5`
- `1.0` = unchanged
- `< 1.0` = softer, less punch
- `> 1.0` = more punch

## Per-Channel Tweaks
- Apply AFTER contrast, BEFORE final clamp
- Use smoothstep-blended multiply:
  `color *= mix(vec3(R_scale, G_scale, B_scale), vec3(1.0), smoothstep(0.0, 1.0, y));`
- Example phone-sleep-mode green lift: `vec3(1.0, 1.02, 0.97)`
- Example yellow/green tint: `vec3(0.95, 1.04, 0.92)`
- Example reduced red: `vec3(0.95, ...)`

## Clamping Rule
- **Exactly one `clamp(color, 0.0, 1.0)` at the end**
- Do NOT clamp intermediate results
- Early clamping causes white-layer artifacts

## Dark-Area Boost Pattern
```glsl
vec3 boost = mix(pix.rgb, mix(vec3(y), pix.rgb, BOOST_AMOUNT), smoothstep(0.0, BOOST_THRESHOLD, y));
vec3 saturated = mix(mix(pix.rgb, boost, VIBRANCE), pix.rgb, smoothstep(BOOST_THRESHOLD + BOOST_FALLOFF, 1.0, y));
```
- Boosts vibrance in dark areas while preserving highlights
- `BOOST_THRESHOLD` = luminance cutoff for boost
- `BOOST_FALLOFF` = width of transition zone
- `BOOST_AMOUNT` = how much vibrance to add in darks
