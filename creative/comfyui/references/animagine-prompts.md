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

### Bending Over Pose Variant (suggestive)
Add to the lewd base: `bending over, hands on knees, apron barely covering, suggestive pose`
This creates an inviting bent-over pose with the apron strategically failing.

### Bed Lying + Looking Back Pose (clothes slipping)
```
1girl, maid, sexy, huge breasts, curvy, wide hips, thick thighs, tall,
white hair, short hair, narrowed eyes, lustful expression,
looking back over shoulder, heavy blush, seductive smile, tongue out, sweat,
shiny skin, lying on bed, arched back, spread legs, see-through clothes,
clothes falling off, bare shoulders, nipple slip, underboob, sideboob,
almost naked, translucent fabric, apron slipping, frilled headband,
pantyhose torn, garter belt, bedroom, dim lighting, erotic, lewd,
suggestive, ((artist:melon22)), artist:ikarin
```
Key tags: `lying on bed` + `looking back over shoulder` + `apron slipping` — creates
a from-behind angle where the maid is on the bed looking back at the viewer,
clothes falling off her shoulders. `pantyhose torn` adds a ruined-clothing fetish
element, and `nipple slip` attempts partial nipple exposure (model-dependent).

### Service Kneeling POV Variant (first-person oral service)
```
1girl, maid, sexy, huge breasts, curvy, thick thighs, white hair, short hair,
narrowed eyes, lustful expression, looking up at viewer, from below, pov,
kneeling, heavy blush, open mouth, tongue out, drooling, sweat, shiny skin,
cleavage, apron, frilled headband, see-through clothes, open clothes,
underboob, bedroom, dim lighting, erotic, lewd, suggestive,
((artist:melon22)), artist:ikarin
```
Key tags: `from below` + `pov` + `kneeling` + `looking up at viewer` + `open mouth` —
first-person perspective looking down at a kneeling maid. "from below" is the
strongest perspective anchor; pair with "looking up at viewer" for eye contact.

### Sex Toy Tags (tricky — model quality varies)
For sex toys in anime-style prompts, simpler concrete tags outperform abstract ones:
- ✅ `egg vibrator` — the egg-shaped remote toy; model draws this more reliably
- ✅ `holding vibrator` — explicitly puts a wand/stick vibrator in hand
- ✅ `vibrator` — generic; may appear as a wand or ambiguous object
- ❌ `remote controlled vibrator` — too abstract; model produces deformed blobs
- ❌ `sex toy` — too generic; adds nothing visual

Always pair toy tags with hand-direction tags like `hand between legs` to
anchor the scene spatially.

### Clothes-Destruction Tags
- `apron slipping` — apron falling off one shoulder (subtler than `open clothes`)
- `clothes falling off` — general garment slip
- `see-through clothes` / `translucent fabric` — transparency effect
- `pantyhose torn` — ripped stockings (fetish element)
- `almost naked` — pushes the model toward more skin exposure

**Pose/attire tags glossary (extended):**

| Tag | Effect |
|-----|--------|
| `lustful expression`, `heavy blush`, `tongue out` | Ahegao-adjacent face |
| `sweat`, `shiny skin` | Glossy wet-look skin |
| `open clothes`, `underboob`, `sideboob`, `navel` | Partial undress with strategic exposure |
| `pantyhose`, `garter belt` | Lingerie accents |
| `leaning forward` | Inviting pose |
| `dim lighting`, `erotic`, `lewd` | Mood and content tone |
| `lying on bed`, `arched back`, `spread legs` | Reclining bed pose |
| `looking back over shoulder` | From-behind glance |
| `from below`, `pov`, `kneeling`, `looking up at viewer` | First-person service POV |
| `see-through clothes`, `translucent fabric` | Semi-transparent clothing |
| `apron slipping`, `clothes falling off` | Garment failure |
| `nipple slip`, `bare shoulders` | Partial nudity hints |
| `egg vibrator`, `holding vibrator`, `hand between legs` | Sex toy elements |
| `pantyhose torn` | Ruined-clothing fetish |
| `open mouth`, `tongue out`, `drooling` | Oral-service expression |

## Tags Reference

| Trait | Tags |
|-------|------|
| Hair | `white hair`, `short hair`, `long hair`, `twintails`, `ponytail` |
| Eyes | `narrowed eyes`, `closed eyes`, `sharp eyes`, `looking at viewer` |
| Body | `huge breasts`, `curvy`, `wide hips`, `thick thighs`, `tall`, `petite` |
| Outfit | `maid`, `apron`, `frilled headband`, `thighhighs`, `cleavage`, `pantyhose`, `garter belt`, `open clothes` |
| Expression | `blush`, `seductive smile`, `embarrassed`, `smirk`, `looking away`, `lustful expression`, `heavy blush`, `tongue out`, `open mouth`, `drooling` |
| Skin | `sweat`, `shiny skin` |
| Exposure | `underboob`, `sideboob`, `navel`, `cleavage`, `leaning forward`, `nipple slip`, `bare shoulders`, `almost naked` |
| Setting | `bedroom`, `soft lighting`, `night`, `candlelight`, `dim lighting` |
| Mood | `erotic`, `lewd`, `sexy`, `suggestive pose` |
| Pose | `bending over`, `hands on knees`, `leaning forward`, `lying on bed`, `arched back`, `spread legs`, `kneeling`, `looking back over shoulder`, `from below`, `pov`, `looking up at viewer` |
| Attire | `apron barely covering`, `apron slipping`, `clothes falling off`, `see-through clothes`, `translucent fabric`, `pantyhose torn` |
| Toys | `egg vibrator`, `holding vibrator`, `vibrator`, `hand between legs` |
| Artist | `artist:melon22`, `artist:ikarin`, `artist:wlop`, `artist:ask` |

## Notes
- `((tag))` doubles weight in NovelAI-style; may not work in all ComfyUI CLIP encoders
- Animagine XL 4.0 responds best to Danbooru tag format (comma-separated)
- "year 2024" pushes the model toward newer anime art styles
- For SD1.5 models (Realistic Vision etc.), use natural language prompts instead
