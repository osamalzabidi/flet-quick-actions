# flet-quick-actions example

Every API on one screen.

```bash
uv run flet build apk --yes --project quick-actions --org flet.app -v
uv run flet-quick-actions-patch --project-root build/flutter
cd build/flutter/android && ./gradlew assembleRelease -Psplit-per-abi=true
```