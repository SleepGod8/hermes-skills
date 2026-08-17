# ASLNet in Hermes Studio: visibility and failover notes

## Durable findings

- Hermes Studio model visibility depends on `providers.<id>` in profile-scoped config.
- `custom_providers` may be enough for CLI use but is not sufficient for Studio picker visibility.
- When syncing a provider to many Hermes profiles, verify each profile independently instead of assuming `default` implies the rest.

## Failover behavior

- Provider-level timeouts such as `request_timeout_seconds` and `stale_timeout_seconds` do not strictly bound user-visible wait time.
- Hermes may still spend additional wall-clock time on app-level retries before fallback takes over.
- When the user wants fast failover from a flaky provider to a stable provider, review both:
  - provider timeouts
  - `api_max_retries`

## Practical tuning guidance

For a cheap provider that is valuable when healthy but frustrating when stalled:

1. Keep the global default on the stable provider.
2. Add the cheap provider under `providers` so Studio can select it.
3. Add `fallback_providers` pointing to the stable provider.
4. Tune explicit provider timeouts.
5. Lower Hermes app-level retries if the user prioritizes responsiveness over patience.

## Communication lesson

When explaining fallback behavior, state clearly whether the configuration changes:

- picker visibility,
- runtime failover,
- or both.

Also make explicit that a timeout value is not the same thing as a hard wall-clock cap when retries remain enabled.
