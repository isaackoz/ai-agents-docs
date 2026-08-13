# Mobile: iOS and Android

Mobile support in this snapshot is experimental. Use this reference only when the user explicitly targets iOS/Android or an existing project already does. Confirm APIs/tasks against the installed beta and test on actual simulators/devices.

Sources: [overview](https://v3.wails.io/guides/mobile/), [first mobile app](https://v3.wails.io/guides/mobile/first-mobile-app/), [iOS](https://v3.wails.io/guides/mobile/ios/), [Android](https://v3.wails.io/guides/mobile/android/), [Mobile API](https://v3.wails.io/guides/mobile/mobile-api/). Upstream source for the overview is `guides/mobile/index.mdx`.

Contents: [Model](#shared-model) · [Run](#run-and-inspect) · [Production](#production-tasks) · [Mobile API](#shared-applicationmobile) · [Native pattern](#native-feature-pattern) · [Constraints](#mobile-constraints)

## Shared model

The same Go application, services, generated bindings, frontend, events, dialogs, and clipboard compile for desktop and mobile. Native WebViews host the frontend and the in-process transport remains internal. Keep shared code platform-neutral and put native implementations in build-tagged files.

Important tag rules:

- iOS implies `darwin`; tag macOS-only files `//go:build darwin && !ios`.
- Android implies `linux`; tag desktop-Linux-only files `//go:build linux && !android`.
- `runtime.GOOS` is `ios` or `android` at runtime.
- Provide `!ios && !android` stubs for shared functions whose real implementation exists only on mobile.

Use `application.System.IsMobile()`, `IsDesktop()`, `IsServer()`, or `IsPlatform(...)` in shared Go code. Matching frontend helpers live under the runtime `System` namespace. Hide mobile-only frontend controls instead of letting desktop users trigger missing runtime namespaces.

## Run and inspect

iOS requires macOS, Xcode, simulator runtimes, Go 1.25+, and frontend tooling:

```bash
wails3 doctor
wails3 task ios:run
wails3 task ios:logs:dev
wails3 task ios:xcode
```

Android requires JDK, Android SDK platform/build tools, NDK 26.3.x, platform tools/emulator, and `ANDROID_HOME`/`ANDROID_SDK_ROOT`:

```bash
wails3 doctor
wails3 task android:run
wails3 task android:logs
adb devices
```

Generated Xcode/Gradle projects can be regenerated; keep durable configuration in `build/config.yml`, Taskfiles, entitlements, and documented source locations rather than one-off edits to generated output.

## Production tasks

iOS:

```bash
wails3 task ios:package
wails3 task ios:deploy-simulator
wails3 task ios:package IOS_PLATFORM=device \
  SIGNING_IDENTITY="..." PROVISIONING_PROFILE=path/to/profile.mobileprovision
wails3 task ios:package:ipa IOS_PLATFORM=device ...
```

For App Store archives and managed signing, open the generated Xcode project and use Xcode. Configure bundle ID, version, deployment target, orientation, usage descriptions, entitlements, signing identity, and provisioning.

Android:

```bash
wails3 task android:package
wails3 task android:deploy-emulator
wails3 task android:run:device
wails3 task android:bundle
wails3 task android:bundle:fat
```

Release APK/AAB must use the project’s real keystore/upload key and increment version code. Debug-keystore output is for testing and is rejected by Play. Keep keystore/passwords out of the repo and CI logs.

## Shared `application.Mobile`

The cross-platform manager covers native features with matching signatures:

- share sheet and external URL;
- keep-awake, torch, orientation, status bar, screen protection;
- safe areas, app/storage/power/network information and app-private storage path;
- biometrics and secure key/value storage;
- location, haptics, motion/proximity, text-to-speech, keyboard insets;
- camera capture.

Asynchronous results arrive through `common:*` events. `application.Mobile` dispatches to the platform implementation on iOS/Android and a safe stub elsewhere; still hide unsupported UI and handle errors/capability denial.

Use `application.IOS` or `application.Android` inside the respective build-tagged files for platform-specific functions. The frontend runtime exposes `IOS`/`Android` namespaces only on the matching platform; calling them on desktop fails.

## Native feature pattern

```go
//go:build ios

func registerNative(app *application.App) {
    app.Event.On("common:haptic", func(e *application.CustomEvent) {
        application.Mobile.Haptic("selection")
    })
}
```

Provide an Android implementation and desktop no-op in separate files. Use `common:*` event names for a shared semantic feature and `ios:*`/`android:*` only for truly platform-specific behavior. Keep returned payload shapes documented/typed in frontend code.

## Mobile constraints

- Design responsive UI with safe-area insets, virtual keyboard, touch targets, orientation, and reduced desktop chrome.
- Request camera/location/biometric/notification permissions in context and supply OS usage declarations.
- Expect background execution limits; do not port desktop daemons/goroutines unchanged.
- Use app-private storage paths and secure storage; desktop absolute paths are not portable.
- Desktop window/menu/tray behavior is absent or different. Feature-gate it.
- Test lifecycle transitions, network loss, rotation, keyboard, permission denial, suspend/resume, low-memory, and upgrades on real devices.

The upstream Kitchen Sink example under `v3/examples/mobile` is the best current executable reference for platform files and common events. Copy patterns only after reconciling them with the project’s installed Wails commit.
