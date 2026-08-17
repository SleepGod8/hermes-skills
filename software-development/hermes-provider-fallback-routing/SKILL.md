---
name: hermes-provider-fallback-routing
description: "Use when Hermes providers need Studio visibility/fallback."
version: 1.0.0
tags: [hermes, providers, studio, fallback, routing, config]
metadata:
  hermes:
    category: software-development
    tags: [hermes, providers, studio, fallback, routing, config]
---

# Hermes Provider Fallback Routing

Configure Hermes providers so they are selectable in Hermes Studio and degrade cleanly when an upstream is slow, stalled, or flaky.

## Use when

- The user added a custom provider and Hermes CLI can use it, but Hermes Studio cannot see it in the model picker.
- A provider works but stalls for too long, and the user wants automatic fallback to a safer default.
- The same provider configuration must be synced across multiple Hermes profiles.
- The user wants a cheap or specialized provider available without making it the default runtime.

## Core rules

1. Treat Hermes Studio and Hermes CLI as separate integration surfaces until proven otherwise.
2. For Studio model-picker visibility, configure `providers.<id>`; `custom_providers` alone is not enough.
3. Keep the user's stable default model unchanged unless they explicitly ask to switch defaults.
4. Fast fallback needs both provider-level timeouts and low app-level retry counts. Timeouts alone do not cap wall-clock delay.
5. Sync provider additions to every requested profile, but verify each profile separately.

## Workflow

1. Identify the user's target behavior:
   - selectable in Studio only
   - selectable in all profiles
   - automatic runtime fallback
   - or all three
2. Add or verify a `providers.<id>` entry for each custom provider the Studio UI must expose.
3. Keep `custom_providers` aligned for CLI/direct usage when the existing setup depends on it.
4. If the user wants failover, add root-level `fallback_providers` with an explicit safe model.
5. Add provider-level `request_timeout_seconds` and `stale_timeout_seconds` to the flaky provider.
6. Check Hermes app-level retries. If the goal is fast failover, lower `api_max_retries` rather than assuming provider timeouts are enough.
7. For multi-profile setups, apply the same change to each `profiles/<name>/config.yaml` that should inherit the provider.
8. Back up each config before editing.
9. Verify by loading the config in profile scope and confirming:
   - `providers.<id>` is present
   - `fallback_providers` is present when requested
   - provider timeouts resolve at runtime
10. Tell the user plainly whether the result is:
   - UI visibility only,
   - runtime failover only,
   - or both.

## Pitfalls

### Studio picker pitfall

Hermes Studio model selection is driven by `providers` and profile-scoped runtime config. A provider that works in CLI via `custom_providers` may still be invisible in Studio until `providers.<id>` exists.

### Timeout pitfall

A provider-level timeout like `request_timeout_seconds: 75` or `stale_timeout_seconds: 90` does not guarantee the user only waits 75-90 seconds total. Hermes also has app-level retry behavior. A stalled request can consume:

- one provider timeout,
- then Hermes retry attempts,
- then fallback activation.

If the user wants aggressive failover, review `api_max_retries` and consider lowering it to `0` or `1`.

### Fallback pitfall

Adding `fallback_providers` enables a route to a backup model, but a long retry budget can still make the backup feel unreachable. Fast failover is a combined tuning problem:

- provider request timeout
- provider stale timeout
- Hermes `api_max_retries`
- fallback chain target

### Multi-profile pitfall

Seeing the provider in `default` does not prove subprofiles are correct. Verify the target profiles explicitly.

## Recommended tuning pattern

For a cheap-but-flaky provider that should remain selectable but not block work:

- leave the global default on the stable provider
- expose the flaky provider through `providers.<id>`
- add `fallback_providers` to a stable model
- set explicit provider timeouts
- reduce `api_max_retries` when the user wants fast failover instead of patience

## Verification checklist

- Provider appears in Studio-backed profile config under `providers`
- Fallback target is explicitly configured
- Runtime timeout helpers resolve the expected values
- Default provider/model remains unchanged unless the user requested otherwise
- User understands whether remaining delay comes from retries versus a single request timeout

## References

- `references/aslnet-studio-fallback-notes.md` — concrete notes from an ASLNet/DeepSeek Studio integration and failover tuning case
