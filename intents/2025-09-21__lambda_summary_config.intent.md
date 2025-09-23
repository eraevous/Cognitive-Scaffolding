@ai-intent: inject-remote-config-into-lambda-summary
- Lambda wrapper now requires a caller-supplied RemoteConfig so orchestration layers control region/bucket selection without implicit file reads.
- Cached Lambda clients by region string to keep performance parity while avoiding unhashable RemoteConfig caching issues.
- Updated module purpose contract to document the config dependency and client caching expectations.
@ai-risk-io: update-callers
- Any remaining code paths must be updated to pass RemoteConfig explicitly; otherwise invocations will fail fast when signatures diverge.
