# Animagine-XL 4.0 Prompt Cookbook

Danbooru tag-based prompt recipes tested with `animagine-xl-4.0.safetensors`.
Resolution: 896×1152 (portrait), steps: 25, CFG: 7, sampler: euler_ancestral.

## Baseline Negative Prompt

```
lowres, bad anatomy, bad hands, extra fingers, missing fingers, worst quality,
low quality, normal quality, censored, mosaic, watermark, signature, ugly, deformed
```

## Quality Boosters (always append)

```
masterpiece, best quality, very aesthetic, amazing quality, year 2024
```

## Recipes

### Sexy Maid (base)
```
1girl, maid, sexy, large breasts, apron, frilled headband, looking at viewer,
blush, seductive smile, thighhighs, cleavage, bedroom, soft lighting
```

### White Short Hair + Huge Breasts Variant
```
1girl, maid, sexy, huge breasts, white hair, short hair, apron, frilled headband,
looking at viewer, blush, seductive smile, thighhighs, cleavage, bedroom,
soft lighting
```

### Curvy Mature Variant (thick build + narrowed eyes)
```
1girl, maid, sexy, huge breasts, curvy, wide hips, thick thighs, tall,
white hair, short hair, narrowed eyes, looking at viewer, blush,
seductive smile, apron, frilled headband, thighhighs, cleavage, bedroom,
soft lighting
```

### Artist Style Injection
Add to prompt: `((artist:melon22)), artist:ikarin`

## Tags Reference

| Trait | Tags |
|-------|------|
| Hair | `white hair`, `short hair`, `long hair`, `twintails`, `ponytail` |
| Eyes | `narrowed eyes`, `closed eyes`, `sharp eyes`, `looking at viewer` |
| Body | `huge breasts`, `curvy`, `wide hips`, `thick thighs`, `tall`, `petite` |
| Outfit | `maid`, `apron`, `frilled headband`, `thighhighs`, `cleavage` |
| Expression | `blush`, `seductive smile`, `embarrassed`, `smirk`, `looking away` |
| Setting | `bedroom`, `soft lighting`, `night`, `candlelight` |
| Artist | `artist:melon22`, `artist:ikarin`, `artist:wlop`, `artist:ask` |

## Notes
- `((tag))` doubles weight in NovelAI-style; may not work in all ComfyUI CLIP encoders
- Animagine XL 4.0 responds best to Danbooru tag format (comma-separated)
- "year 2024" pushes the model toward newer anime art styles
- For SD1.5 models (Realistic Vision etc.), use natural language prompts instead
