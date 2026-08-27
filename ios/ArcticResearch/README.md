# Arctic Research iOS Offline Test App

This is the first downloadable-device test build of Arctic Research Simulator. It uses a lightweight native SwiftUI/WKWebView shell, but the tested game itself is a frozen snapshot of the current web build packaged inside the app.

## Offline behavior

The installed app contains:

- all game HTML, JavaScript and CSS;
- all bundled photographs and visual assets;
- all bundled wildlife recordings and other audio assets;
- the 2048 px Arctic overview map for low-resolution coverage everywhere;
- a 5 × 5 block of 128 km / 1024 px GEBCO high-resolution terrain tiles centered on the Longyearbyen/Svalbard starting region.

The game therefore starts and remains playable without an Internet connection. High-resolution terrain outside the bundled Svalbard region is the only game content that normally requires a network connection.

When a remote high-resolution terrain tile is needed, the native shell downloads it from the GEBCO North Polar WMS and stores it in the iOS Caches directory. The terrain cache is capped at approximately **150 MB** and evicts the least recently used files when it grows beyond that size. Previously downloaded terrain remains available offline unless iOS later purges application cache storage under storage pressure.

## Package generation

`ios/prepare-offline-ios-package.py` creates `ArcticResearch/ArcticResearch/WebApp` at package time. It copies the current tested game and the complete `assets` directory, patches only that copy to use the native terrain transport, then downloads the 25 Svalbard tiles.

The normal GitHub Pages web build is not modified by this packaging step.

GitHub Actions runs the packager, validates the offline asset set, compile-checks the native shell against the iPhone Simulator SDK, and publishes an artifact named:

`ArcticResearch-iOS-Offline-Test-23aq`

## Install on an iPhone for testing

1. Download and unzip the packaged `ArcticResearch` folder on a Mac.
2. Install/open **Xcode** from Apple if it is not already installed.
3. Open `ArcticResearch.xcodeproj`.
4. In Xcode, select the **ArcticResearch** project and then the **ArcticResearch** target.
5. Open **Signing & Capabilities** and choose your Apple ID / Apple Development Team. Xcode can use a free personal development team for direct device testing.
6. Connect the iPhone to the Mac. On recent iOS versions, a wireless paired device can also be used after the first connection.
7. Choose the iPhone as the run destination at the top of Xcode and press **Run** (▶).
8. If iOS asks, enable **Developer Mode** and trust the developer certificate/account.
9. After installation, launch **Arctic Research** from the phone like a normal app.

The bundle identifier is `com.ivansavelyev.ArcticResearchSimulator`. If Xcode reports that the identifier is not available for your signing team, change it to another unique identifier in Signing & Capabilities.

## Recommended first offline test

1. Install and launch while online once.
2. Start a new expedition and verify the detailed terrain around Longyearbyen/Svalbard.
3. Put the iPhone in Airplane Mode.
4. Relaunch the app and confirm that the title screen, saves, photographs, sounds, Svalbard high-resolution terrain, and coarse Arctic map all still work.
5. Re-enable Internet access, sail/relocate beyond the preloaded region, allow some new high-resolution terrain to appear, then return to Airplane Mode and confirm those recently visited areas remain detailed from cache.

## Current test-build limits

This is not an App Store / TestFlight distribution build yet. Apple requires the app to be signed for installation, so the first test package is intentionally an Xcode project for direct installation on your own iPhone. Once the native/offline behavior is solid, the same project can be moved to TestFlight for much easier installation by additional testers.
