# Distribution, Updates, Associations, and Single Instance

Use this reference for in-app updates, update manifests and verification, installer selection, file associations, custom URL schemes, and forwarding second launches.

Sources: [updater](https://v3.wails.io/guides/updater/), [GitHub release assets](https://v3.wails.io/guides/updater-github-release-assets/), [update manifest](https://v3.wails.io/reference/update-manifest/), [self-update tutorial](https://v3.wails.io/tutorials/04-self-update-a-wails-app/), [installers](https://v3.wails.io/guides/installers/), [file associations](https://v3.wails.io/guides/file-associations/), [custom protocols](https://v3.wails.io/guides/distribution/custom-protocols/), [single instance](https://v3.wails.io/guides/single-instance/).

Contents: [Updater](#updater-setup) · [Verification](#verification-and-key-handling) · [Manifest](#wails-update-manifest-protocol) · [Checklist](#update-release-checklist) · [Associations](#file-associations) · [Protocols](#custom-url-protocols) · [Single instance](#single-instance)

## Updater setup

`app.Updater` manages check, download, verification, staging, swap-helper, restart, UI, and events:

```go
gh, err := github.New(github.Config{Repository: "myorg/myapp"})
if err != nil { return err }

if err := app.Updater.Init(updater.Config{
    CurrentVersion: currentVersion,
    Providers:      []updater.Provider{gh},
    PublicKey:      updaterPublicKey,
}); err != nil {
    return err
}
```

Provider options include GitHub Releases, keygen.sh, Sparkle AppCast, Wails endpoint manifest, and a custom `Provider`. Providers form an ordered fallback for errors/unavailability; the first release wins and an explicit up-to-date result stops fallback. Do not use fallback sources to resolve conflicting version truth.

Updater state progresses through checking, available/no-update, downloading, verifying, installing/staging, ready, and error. Use exported Go/frontend event constants rather than hand-written wire names. Built-in window, customized built-in HTML/theme, bring-your-own window, and headless `WindowNone` are supported.

Security-sensitive BYO updater windows may need `AllowSimpleEventEmit` for updater buttons. Enable it only for fully controlled local HTML: any script/XSS in that window can emit bare custom event names and trigger privileged Go event handlers.

## Verification and key handling

Generate a signing key once:

```bash
wails3 updater genkey
# updater.key: private, CI secret only
# updater.key.pub: embed in application
```

Pin the public key in the built app. The provider/manifest cannot replace this trust root. Supported verification includes Ed25519, Ed25519ph, ECDSA P-256, and SHA-256/SHA-512 digest-only metadata. A signature with no configured public key fails closed. Digest-only protects corruption but still trusts TLS/release hosting against malicious substitution; sign production updates.

Keep the private key outside source control, build artifacts, logs, and application bundles. Verify that the published bytes—not a pre-sign or pre-package intermediate—are the bytes described by checksums/signatures.

## Wails update manifest protocol

The endpoint provider GETs JSON with platform, arch, installed version, and channel query data. A static manifest can list all platform artifacts; a dynamic server may return one or `204` for no update. Each artifact provides platform, architecture, HTTP(S) URL, and optional digest/signature fields. The first matching platform/arch artifact is selected; SemVer comparison remains client-side.

```bash
wails3 updater manifest -version 2.1.0 -channel stable \
  -key updater.key -notes-file notes.md -url-prefix https://downloads.example.com/ \
  bin/MyApp-2.1.0-*
wails3 updater verify -manifest manifest.json -publickey updater.key.pub
```

Use the verify command as a CI gate. Authentication headers are reused for artifact downloads only on safe same-host/no-downgrade paths; authorization is stripped on cross-origin or HTTPS-to-HTTP redirect. Prefer short-lived scoped credentials.

GitHub’s default matcher chooses platform/arch application artifacts, ignores signature/checksum sidecars, and avoids installer executables. A custom `AssetMatcher` replaces all default filtering, so it must exclude installers, metadata, and wrong targets itself. Use conventional filenames and test the exact release asset set.

## Update release checklist

1. Build and sign application artifacts for every supported platform/architecture.
2. Publish an unpackable format supported by the updater; distinguish app payloads from installers.
3. Produce digest/signature metadata from final bytes.
4. Verify the manifest/feed and download URLs in CI.
5. Test update from the previous supported version, failure/retry, skip/remind, restart, locked-file replacement, and rollback/recovery expectations.
6. Keep application version injected consistently into updater `CurrentVersion` and package metadata.

## File associations

Declare associations in `build/config.yml`, regenerate/update build assets, and package/install the app. Then listen for files:

```go
app.Event.OnApplicationEvent(events.Common.ApplicationOpenedWithFile,
    func(event *application.ApplicationEvent) {
        filename := event.Context().Filename()
        openValidatedDocument(filename)
    })
```

Associations are installer/OS registrations, so testing an unpackaged development binary is insufficient. Validate extension and content, canonicalize the path, handle missing/inaccessible files, and forward to the appropriate existing/new window.

## Custom URL protocols

Declare protocols in `build/config.yml`; there is no `application.Protocol` or `application.Options.Protocols`. Platform packaging maps them to NSIS/MSIX, `Info.plist`, and Linux desktop/MIME registrations. Receive launches with `events.Common.ApplicationLaunchedWithUrl`.

Parse with `net/url`, require the exact scheme, allowlist hosts/actions, reject unexpected credentials/ports, validate and decode each argument once, cap lengths, and never concatenate URL values into shell commands, paths, SQL, or HTML. Treat protocol links from websites/chat/email as hostile input. Universal Links/App URI handlers require additional website and platform association files beyond custom-scheme configuration.

## Single instance

```go
app := application.New(application.Options{
    Name: "My App",
    SingleInstance: &application.SingleInstanceOptions{
        UniqueID: "com.example.myapp",
        OnSecondInstanceLaunch: func(data application.SecondInstanceData) {
            mainWindow.Show().Focus()
            // Validate data.Args/data.WorkingDir before forwarding.
        },
    },
})
```

Use a stable reverse-domain ID. An optional nonzero 32-byte `EncryptionKey` encrypts inter-instance messages with AES-256-GCM; load it from a stable secure source so versions can communicate. The second launch forwards arguments and working directory to the primary and exits. Validate forwarded data just like external CLI input and avoid UI access before the primary window exists—capture the app/window safely or queue until startup.

Combine single instance with file associations/protocols when subsequent launches should focus the existing app. Test simultaneous launches, upgrades with different binaries, crashes/stale locks, and per-user versus machine-session expectations on each OS.
