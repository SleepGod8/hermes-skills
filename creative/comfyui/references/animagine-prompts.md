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

### Full Lewd Variant (sweat, open clothes, erotic)
The maximal-sexy version combining all the above with explicit tags:
```
1girl, maid, sexy, huge breasts, curvy, wide hips, thick thighs, tall,
white hair, short hair, narrowed eyes, lustful expression, looking at viewer,
heavy blush, seductive smile, tongue out, sweat, shiny skin, open clothes,
underboob, sideboob, navel, apron, frilled headband, pantyhose, garter belt,
thighhighs, cleavage, leaning forward, bedroom, dim lighting, erotic, lewd,
((artist:melon22)), artist:ikarin
```

**Ero/lewd tags glossary:**

| Tag | Effect |
|-----|--------|
| `lustful expression`, `heavy blush`, `tongue out` | Ahegao-adjacent face |
| `sweat`, `shiny skin` | Glossy wet-look skin |
| `open clothes`, `underboob`, `sideboob`, `navel` | Partial undress with strategic exposure |
| `pantyhose`, `garter belt` | Lingerie accents |
| `leaning forward` | Inviting pose |
| `dim lighting`, `erotic`, `lewd` | Mood and content tone |

## Tags Reference

| Trait | Tags |
|-------|------|
| Hair | `white hair`, `short hair`, `long hair`, `twintails`, `ponytail` |
| Eyes | `narrowed eyes`, `closed eyes`, `sharp eyes`, `looking at viewer` |
| Body | `huge breasts`, `curvy`, `wide hips`, `thick thighs`, `tall`, `petite` |
| Outfit | `maid`, `apron`, `frilled headband`, `thighhighs`, `cleavage`, `pantyhose`, `garter belt`, `open clothes` |
| Expression | `blush`, `seductive smile`, `embarrassed`, `smirk`, `looking away`, `lustful expression`, `heavy blush`, `tongue out` |
| Skin | `sweat`, `shiny skin` |
| Exposure | `underboob`, `sideboob`, `navel`, `cleavage`, `leaning forward` |
| Setting | `bedroom`, `soft lighting`, `night`, `candlelight`, `dim lighting` |
| Mood | `erotic`, `lewd`, `sexy` |
| Artist | `artist:melon22`, `artist:ikarin`, `artist:wlop`, `artist:ask` |

## Notes
- `((tag))` doubles weight in NovelAI-style; may not work in all ComfyUI CLIP encoders
- Animagine XL 4.0 responds best to Danbooru tag format (comma-separated)
- "year 2024" pushes the model toward newer anime art styles
- For SD1.5 models (Realistic Vision etc.), use natural language prompts instead
