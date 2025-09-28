@ai-intent: consolidate-schema-config
@ai-cadence: config-refactor
- Refactored schema configuration to absolute default path with local validation
- Removed global override coupling; migrated to `config_registry.configure`
- Added fallback validation and consistent `.purpose` regeneration
