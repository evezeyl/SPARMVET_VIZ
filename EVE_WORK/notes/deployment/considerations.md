## First deployment scope and inactive modules

For the first real deployment, the release should be conservative and centered on the core functionality.

Recommended approach:

- create a deployment-oriented release profile
- include only what is needed to run the intended user-facing application
- avoid relying only on the assumption that advanced modules are harmless because users will not access them

Important distinction:

- not intended to be used
- is not the same as
- impossible to access

If advanced or developer-oriented modules are already included in the app UI, they should not be considered fully harmless merely because they are expected to remain inaccessible under the selected deployment configuration.

Potential risks of keeping such modules present in the deployed UI or runtime include:

- accidental exposure through configuration mistakes
- indirect accessibility through UI state, query parameters, inputs, or reactive paths
- startup-time dependency loading
- confusion for users, testers, or administrators
- additional maintenance burden in production

Preferred deployment behavior:

- only modules explicitly enabled by configuration should be registered or rendered
- do not load all modules and merely hide some of them
- prefer positive inclusion over negative hiding

For first deployment, if possible:

- keep advanced modules in the repository
- but do not register them in the deployed UI unless explicitly enabled
- do not initialize their server-side logic unless explicitly enabled
- do not expose navigation or entry points for them in the deployment profile

If excluding them from the runtime bundle is difficult initially, the minimum requirement should be:

- they must not be activated by the selected configuration
- they must not create startup side effects
- they must not expose user-facing access paths
- they must not introduce brittle deployment dependencies

This should be treated as part of the deployment-hardening strategy for the first release.