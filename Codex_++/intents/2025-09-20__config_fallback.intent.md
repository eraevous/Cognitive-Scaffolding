@ai-intent: soften-config-dependencies
- Added runtime fallback for PathConfig.from_file() so tests and local runs don't abort when JSON is absent. Default PathConfig keeps schema path pointing at repo defaults while logging a warning.
- Introduced RemoteConfig environment fallback to support unit tests that mock Lambda helpers without provisioning AWS secrets. Prefers JSON file when available.
- Deferred lambda_summary remote client initialization until runtime to avoid import-time config loading. Added caching to minimize repeated reads.
- validate_metadata() now pulls PathConfig lazily, deferring environment resolution until invocation.
@ai-risk-behavior: silent-misconfig
- Warns in logs but proceeds with empty AWS credentials; downstream cloud calls will still fail loudly when invoked.
