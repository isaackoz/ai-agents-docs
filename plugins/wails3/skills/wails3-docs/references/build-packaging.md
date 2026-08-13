# Build, Signing, and Platform Packaging

Use this reference for production builds, Taskfile customization, cross-compilation, icons/assets, signing, installers, platform packages, UAC, and Garble.

Sources: [build system](https://v3.wails.io/concepts/build-system/), [building](https://v3.wails.io/guides/build/building/), [customization](https://v3.wails.io/guides/build/customization/), [cross-platform](https://v3.wails.io/guides/build/cross-platform/), [signing](https://v3.wails.io/guides/build/signing/), [Windows](https://v3.wails.io/guides/build/windows/), [macOS](https://v3.wails.io/guides/build/macos/), [Linux](https://v3.wails.io/guides/build/linux/), [installers](https://v3.wails.io/guides/installers/), [UAC](https://v3.wails.io/guides/windows-uac/), [obfuscation](https://v3.wails.io/guides/build/obfuscation/).

Contents: [Build](#build-interface) · [Cross-building](#cross-building) · [Windows](#windows) · [macOS](#macos) · [Linux](#linux) · [Signing](#signing-configuration-and-secrets) · [Obfuscation](#obfuscated-builds) · [Failures](#release-failures)

## Build interface

```bash
wails3 dev
wails3 build
wails3 build GOOS=windows GOARCH=arm64
wails3 package GOOS=linux
wails3 task --list
```

`wails3 build` and `package` are Taskfile wrappers. Treat the project’s root and `build/<platform>/` Taskfiles as authoritative. Pass target/config variables as `KEY=value`; use CLI flags only if `wails3 build --help` documents them. Output normally goes to `bin/`.

`build/config.yml` holds product identity/version, bundle data, installer metadata, protocols, associations, and platform properties. There is no Wails v3 `build/build.json`. Refresh support files with `wails3 update build-assets`; review changes because generated platform files may overlap deliberate customization.

Before a release:

1. Pin/record Wails CLI/module and frontend dependency versions.
2. Run service/frontend tests and regenerate bindings.
3. Set version, identifier, product/company metadata, icons, and platform declarations.
4. Build each architecture/OS.
5. Package, sign, notarize where required, and verify signatures.
6. Install/test on clean representative machines, including upgrade/uninstall.

## Cross-building

```bash
wails3 task setup:docker
wails3 build GOOS=darwin GOARCH=arm64
wails3 build GOOS=linux GOARCH=amd64
wails3 build GOOS=windows GOARCH=arm64
```

Wails Taskfiles use a Docker/Zig cross toolchain for CGO-dependent non-host targets. Native runners remain preferable for release signing and realistic tests. Windows pure-Go targets can often cross-build natively; CGO forces Docker. macOS and Linux webview integrations use CGO. Universal macOS output is built with tasks such as `darwin:build:universal`/`darwin:package:universal` and `wails3 tool lipo` where needed.

Cross-built macOS applications are not ready for distribution until signed/notarized on macOS. Verify the Docker image/license implications of included SDKs in organizational environments.

## Windows

```bash
wails3 package GOOS=windows              # NSIS default
wails3 package GOOS=windows FORMAT=msix  # MSIX when tooling exists
wails3 setup signing --platform windows
wails3 task windows:sign
wails3 task windows:sign:installer
```

- Customize NSIS under `build/windows/nsis/`; MSIX requires Windows SDK or standalone tooling.
- Embed icons/version/manifest resources through generated build assets.
- Configure UAC in the Windows manifest template: use `asInvoker` by default, `highestAvailable` or `requireAdministrator` only for operations that truly require elevation. Elevated apps change drag/drop, IPC, file virtualization, and user expectations.
- Sign both executable and installer with a trusted certificate and timestamp. Self-signed certificates are testing-only; unsigned builds trigger SmartScreen warnings.
- Include or bootstrap WebView2 if supporting machines where the runtime may be absent.

## macOS

```bash
wails3 package GOOS=darwin
wails3 task darwin:package:universal
wails3 setup entitlements
wails3 setup signing --platform darwin
wails3 task darwin:sign:notarize
wails3 task darwin:package:dmg
```

- Configure bundle identifier, version, icons, `Info.plist` keys, usage descriptions, and entitlements.
- Development entitlements may allow JIT/debug/unsigned memory; production entitlements should be minimal.
- Sign nested code in correct order with hardened runtime, notarize the final distributable using `notarytool`, and staple/verify as appropriate.
- Credentials belong in the macOS keychain/CI secret store, not Taskfiles.
- Test both Apple Silicon and Intel or use a universal package.

## Linux

```bash
wails3 package GOOS=linux
wails3 task linux:create:appimage
wails3 task linux:create:deb
wails3 task linux:create:rpm
wails3 task linux:create:aur
```

- Customize `.desktop`, MIME, icon, and nfpm metadata under `build/linux/`.
- Default runtime is GTK4 + WebKitGTK 6.0. Build with `-tags gtk3` only for the temporary v3.0.x GTK3/WebKit2GTK 4.1 compatibility target; it is removed in v3.1.
- AppImage is portable but still depends on compatible kernel/display behavior. Test packaged outputs across minimum supported distributions and Wayland/X11 where relevant.
- Sign DEB/RPM packages with configured PGP keys. Store passwords outside repository files.
- If AppImage tooling cannot strip modern RELR binaries, Wails may disable stripping, increasing size rather than producing a broken package.

## Signing configuration and secrets

Use `wails3 setup signing`; shared defaults are stored under Wails user config and secrets in native credential storage. Resolution is explicit CLI flag, then project Taskfile variable, then global defaults. Keep identities/key paths configurable; never commit passwords, private keys, notarization credentials, or certificate exports.

macOS signing/notarization requires Apple tooling on a Mac. Windows and Linux package signing can use native or built-in/cross-platform backends as documented. Always verify the artifact after every packaging mutation—changing a signed file invalidates the signature.

## Obfuscated builds

Garble support requires stable binding IDs and JSON tags:

```bash
go install mvdan.cc/garble@<compatible-version>
wails3 generate bindings -obfuscated
wails3 build --obfuscated
```

Commit the generated `wails_obfuscated.gen.go` so stable IDs are reproducible. If `-obfuscated-output` targets another package, that package must be imported by `main` so its `init` registration runs. Add explicit JSON tags to all transported struct fields—Garble can rename fields invisible to reflection analysis, yielding empty/renamed frontend data despite a successful build. Check the installed Wails CLI for exact obfuscation flags and select a Garble version compatible with the Go toolchain.

Obfuscation is not encryption and may increase antivirus false positives. Sign release artifacts and submit false positives through vendor processes rather than weakening protections.

## Release failures

- Build ignores target/output flag: use Task variables/tasks; `wails3 build` exposes a narrow flag surface.
- Cross-build asks for compiler: build/setup the Wails Docker image or use a native CI runner.
- macOS says damaged/unidentified: verify Developer ID signature, hardened runtime, notarization, and stapling.
- Windows SmartScreen/UAC surprises: inspect embedded manifest and signatures on the final installer/exe.
- Linux missing libraries: verify target distro baseline and correct GTK tag/package dependencies.
- Package metadata stale: update `build/config.yml`, regenerate/update build assets, then review the platform files.
- Binding missing only when obfuscated: regenerate stable IDs and ensure the ID package is linked/initialized.
