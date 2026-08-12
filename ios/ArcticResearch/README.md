# Arctic Research iOS Test App

This is a lightweight native SwiftUI/WKWebView test harness for the live Arctic Research Simulator build.

## Why it loads the live game
The test app points at the GitHub Pages production URL so normal GitHub game updates appear in the iPhone app without rebuilding the native project every iteration. This is intentional for rapid UI/gameplay testing.

## Run on an iPhone
1. Install/open Xcode on the Mac.
2. Open `ArcticResearch.xcodeproj`.
3. Select the `ArcticResearch` target and choose your Apple Development Team under Signing & Capabilities.
4. Connect the iPhone, choose it as the run destination, and press Run.
5. If iOS asks, enable Developer Mode / trust the development certificate.

The bundle identifier is currently `com.ivansavelyev.ArcticResearchSimulator`; change it in Xcode if your signing account requires a different unique identifier.

## Production direction
This wrapper is for device testing. Before App Store submission we can add the native StoreKit bridge, haptics, native app icon/launch treatment, and decide whether the production build should bundle a tested web snapshot rather than load the live development site.
