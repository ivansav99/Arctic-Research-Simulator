# Arctic Research iOS App Store Release Candidate

This Xcode project packages Arctic Research Simulator as a native SwiftUI/WKWebView iPhone app. The game HTML, JavaScript, CSS, photographs and sounds are bundled in the application; high-resolution terrain outside the Svalbard starter region downloads on demand and is cached on device.

## Release behavior

- App version: **1.0**
- Bundle identifier: `com.ivansavelyev.ArcticResearchSimulator`
- Target: **iPhone**
- Minimum iOS: **17.0**
- Private Funding uses Apple **StoreKit 2 consumable In-App Purchases**.
- The release UI does not expose the development TEST button.
- A native audio-session recovery hook plus Web Audio recovery handles app background/foreground transitions.

### Private Funding product IDs

Create these as **Consumable** In-App Purchases in App Store Connect:

| Product ID | Game cash |
| --- | ---: |
| `ars.private_funding.1m` | $1,000,000 |
| `ars.private_funding.10m` | $10,000,000 |
| `ars.private_funding.50m` | $50,000,000 |

The in-game store requests localized prices from StoreKit. A verified purchase is written into the expedition save before the StoreKit transaction is finished. Unfinished verified transactions are recovered on launch/resume so a paid consumable is not lost if the app closes during delivery.

## Offline behavior

The installed app contains all core game files and assets, the Arctic overview map, and a 5 × 5 block of 128 km / 1024 px GEBCO high-resolution terrain tiles centered on Longyearbyen/Svalbard. High-resolution terrain elsewhere is downloaded from the GEBCO North Polar WMS and stored in an approximately 150 MB cache.

## Release checks

GitHub Actions now runs both the browser smoke test and the iOS package workflow on pull requests to `main`. The iOS workflow:

1. syntax-checks the game JavaScript;
2. generates the offline WebApp snapshot;
3. validates bundled map/audio resources and StoreKit code;
4. compile-checks a Debug iPhone Simulator build;
5. compile-checks a Release iPhone device build with code signing disabled;
6. publishes an artifact named `ArcticResearch-iOS-AppStore-RC1`.

## Remaining App Store setup

Before archiving for App Store Connect:

1. Add a real 1024 × 1024 app icon to `Assets.xcassets/AppIcon.appiconset`. The placeholder catalog currently has no image.
2. In Xcode, select the ArcticResearch target, choose the Apple Developer Team, and confirm automatic signing.
3. Create the app record in App Store Connect using bundle ID `com.ivansavelyev.ArcticResearchSimulator`.
4. Create the three consumable In-App Purchases above and set their prices/localized display names.
5. Test all three purchases using StoreKit/Sandbox or TestFlight.
6. Add App Store screenshots, description, support URL, privacy policy URL, age rating, availability, and App Review notes.
7. Archive the Release build in Xcode and upload it to App Store Connect.
