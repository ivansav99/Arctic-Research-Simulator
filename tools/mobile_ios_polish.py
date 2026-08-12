from pathlib import Path


def replace_once(text, old, new, label):
    count=text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old,new,1)

# ---------- index.html ----------
p=Path('index.html')
s=p.read_text()
s=replace_once(s,
'''  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">\n  <meta name="theme-color" content="#082f49">''',
'''  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">\n  <meta name="theme-color" content="#082f49">\n  <meta name="apple-mobile-web-app-capable" content="yes">\n  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n  <meta name="apple-mobile-web-app-title" content="Arctic Research">\n  <link rel="manifest" href="manifest.webmanifest">''','standalone meta')
s=replace_once(s,'style.css?v=expedition-21','style.css?v=expedition-22k-mobile','style cache bust')
s=replace_once(s,'game.js?v=expedition-22j-progression','game.js?v=expedition-22k-mobile','game cache bust')
p.write_text(s)

# ---------- manifest ----------
Path('manifest.webmanifest').write_text('''{
  "name": "Arctic Research Simulator",
  "short_name": "Arctic Research",
  "description": "Lead an Arctic research expedition, build a scientific career, and operate increasingly capable research vessels.",
  "start_url": "./?standalone=1",
  "scope": "./",
  "display": "standalone",
  "orientation": "any",
  "background_color": "#082f49",
  "theme_color": "#082f49"
}\n''')

# ---------- mobile HUD CSS ----------
p=Path('style.css')
s=p.read_text()
mobile_css=r'''

/* Expedition 22k: compact phone HUD and touch-first map controls. */
.time-controls { display:none !important; }
.minimap {
  width:148px; height:148px; padding:0; overflow:hidden; border:0; border-radius:50%;
  background:transparent; box-shadow:none; backdrop-filter:none; -webkit-backdrop-filter:none;
}
.minimap > div { display:none !important; }
#minimap { width:100%; height:100%; }

@media (max-width:640px), ((pointer:coarse) and (max-width:900px)) {
  .top-hud {
    top:max(6px, env(safe-area-inset-top)); left:max(6px, env(safe-area-inset-left)); right:max(6px, env(safe-area-inset-right));
    min-height:70px; padding:0; border:0; border-radius:0; background:transparent; box-shadow:none;
    backdrop-filter:none; -webkit-backdrop-filter:none; pointer-events:none;
  }
  .brand { display:none !important; }
  .status { position:relative; display:block; width:100%; height:70px; text-align:left; pointer-events:none; }
  .status > * { pointer-events:auto; }
  .ice-status,.weather-status,.date-status,.position-status,.speed-status { display:none !important; }
  .game-menu-button {
    position:absolute; left:0; top:0; width:34px; height:34px; padding:0; border-radius:50%; font-size:0;
    background:rgba(5,31,48,.72); backdrop-filter:blur(7px); -webkit-backdrop-filter:blur(7px);
  }
  .game-menu-button::after { content:'☰'; color:#d9f5fb; font:700 17px/1 system-ui; }
  .vessel-button { position:absolute; right:0; top:0; width:72px; height:43px; padding:2px; border-radius:9px; }
  .fuel-status,.food-status {
    position:absolute; right:0; display:grid !important; grid-template-columns:28px 1fr; grid-template-rows:8px 3px;
    align-items:center; width:72px; height:11px; padding:0 2px; border-radius:3px; background:rgba(5,31,48,.72);
    line-height:1; backdrop-filter:blur(6px); -webkit-backdrop-filter:blur(6px);
  }
  .fuel-status { top:45px; }
  .food-status { top:58px; }
  .fuel-status small,.food-status small { display:block !important; margin:0; color:#93bdc8; font-size:5px; letter-spacing:.06em; }
  .fuel-status b,.food-status b { display:block !important; margin:0; color:#eafaff; font-size:6px; text-align:right; letter-spacing:.02em; }
  .fuel-status > i,.food-status > i { grid-column:1 / -1; display:block; width:68px !important; height:3px; margin:0; }
  .zoom-controls,.compass { display:none !important; }
  .minimap {
    right:max(5px, env(safe-area-inset-right)); bottom:max(6px, env(safe-area-inset-bottom));
    width:86px; height:86px;
  }
  .scale { left:max(7px, env(safe-area-inset-left)); bottom:max(7px, env(safe-area-inset-bottom)); transform:scale(.76); transform-origin:left bottom; opacity:.72; }
  .resource-warning { top:max(80px, calc(env(safe-area-inset-top) + 75px)); }
}
'''
if '/* Expedition 22k: compact phone HUD' not in s:
    s += mobile_css
p.write_text(s)

# ---------- game.js pinch-to-zoom ----------
p=Path('game.js')
s=p.read_text()
old="""  canvas.addEventListener('pointerdown',e=>{sound.unlock();analytics.track('map_interaction',{map_area:'main',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});handleMapPointer(e.clientX,e.clientY);});\n  miniCanvas.addEventListener('pointerdown',e=>{sound.unlock();analytics.track('map_interaction',{map_area:'minimap',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});navigateFromMiniMap(e);});\n  canvas.addEventListener('pointermove',e=>{canvas.style.cursor=researchGuidanceAt(e.clientX,e.clientY)||wildlifeAtScreenPoint(e.clientX,e.clientY)||nearbyNpcVesselAt(e.clientX,e.clientY)||nearbyResearchTargetAt(e.clientX,e.clientY)||nearbyCityAt(e.clientX,e.clientY)?'pointer':'crosshair';});"""
new="""  const mapTouchPointers=new Map();let mapTouchTap=null,mapPinchDistance=0,mapPinchActive=false;\n  function mapPinchStep(){if(mapTouchPointers.size<2)return;const points=[...mapTouchPointers.values()],distance=Math.hypot(points[0].x-points[1].x,points[0].y-points[1].y);if(!mapPinchDistance){mapPinchDistance=distance;return;}const ratio=distance/Math.max(1,mapPinchDistance);if(ratio>1.16){setZoom(1);mapPinchDistance=distance;analytics.track('zoom_changed',{zoom_direction:'pinch-in-detail'});}else if(ratio<.86){setZoom(-1);mapPinchDistance=distance;analytics.track('zoom_changed',{zoom_direction:'pinch-out-overview'});}}\n  canvas.addEventListener('pointerdown',e=>{sound.unlock();if(e.pointerType!=='touch'){analytics.track('map_interaction',{map_area:'main',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});handleMapPointer(e.clientX,e.clientY);return;}e.preventDefault();canvas.setPointerCapture?.(e.pointerId);mapTouchPointers.set(e.pointerId,{x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY});if(mapTouchPointers.size===1){mapTouchTap={id:e.pointerId,x:e.clientX,y:e.clientY,moved:false};mapPinchActive=false;}else{mapPinchActive=true;mapTouchTap=null;mapPinchDistance=0;mapPinchStep();}});\n  miniCanvas.addEventListener('pointerdown',e=>{sound.unlock();analytics.track('map_interaction',{map_area:'minimap',pointer_x:Math.round(e.clientX),pointer_y:Math.round(e.clientY)});navigateFromMiniMap(e);});\n  canvas.addEventListener('pointermove',e=>{if(e.pointerType==='touch'&&mapTouchPointers.has(e.pointerId)){e.preventDefault();const point=mapTouchPointers.get(e.pointerId);point.x=e.clientX;point.y=e.clientY;if(Math.hypot(point.x-point.startX,point.y-point.startY)>10&&mapTouchTap?.id===e.pointerId)mapTouchTap.moved=true;if(mapTouchPointers.size>=2){mapPinchActive=true;mapTouchTap=null;mapPinchStep();}return;}canvas.style.cursor=researchGuidanceAt(e.clientX,e.clientY)||wildlifeAtScreenPoint(e.clientX,e.clientY)||nearbyNpcVesselAt(e.clientX,e.clientY)||nearbyResearchTargetAt(e.clientX,e.clientY)||nearbyCityAt(e.clientX,e.clientY)?'pointer':'crosshair';});\n  function finishMapTouch(e,cancelled=false){if(!mapTouchPointers.has(e.pointerId))return;const tap=mapTouchTap&&mapTouchTap.id===e.pointerId&&!mapTouchTap.moved&&!mapPinchActive&&!cancelled?{x:e.clientX,y:e.clientY}:null;mapTouchPointers.delete(e.pointerId);if(mapTouchPointers.size<2)mapPinchDistance=0;if(mapTouchPointers.size===0){mapPinchActive=false;mapTouchTap=null;}if(tap){analytics.track('map_interaction',{map_area:'main',pointer_x:Math.round(tap.x),pointer_y:Math.round(tap.y)});handleMapPointer(tap.x,tap.y);}}\n  canvas.addEventListener('pointerup',e=>finishMapTouch(e,false));\n  canvas.addEventListener('pointercancel',e=>finishMapTouch(e,true));"""
s=replace_once(s,old,new,'map pointer handlers')
p.write_text(s)

# ---------- Native iOS WKWebView test harness ----------
root=Path('ios/ArcticResearch')
app=root/'ArcticResearch'
proj=root/'ArcticResearch.xcodeproj'
assets=app/'Assets.xcassets'
appicon=assets/'AppIcon.appiconset'
appicon.mkdir(parents=True,exist_ok=True)
proj.mkdir(parents=True,exist_ok=True)

(app/'ArcticResearchApp.swift').write_text('''import SwiftUI\n\n@main\nstruct ArcticResearchApp: App {\n    var body: some Scene {\n        WindowGroup {\n            ContentView()\n                .statusBarHidden(true)\n        }\n    }\n}\n''')

(app/'ContentView.swift').write_text('''import SwiftUI\nimport WebKit\n\nstruct ContentView: View {\n    var body: some View {\n        GameWebView()\n            .ignoresSafeArea()\n            .background(Color(red: 0.03, green: 0.18, blue: 0.29))\n    }\n}\n\nstruct GameWebView: UIViewRepresentable {\n    static let gameURL = URL(string: "https://ivansav99.github.io/Arctic-Research-Simulator/?app=ios")!\n\n    func makeCoordinator() -> Coordinator { Coordinator() }\n\n    func makeUIView(context: Context) -> WKWebView {\n        let configuration = WKWebViewConfiguration()\n        configuration.websiteDataStore = .default()\n        configuration.defaultWebpagePreferences.preferredContentMode = .mobile\n\n        let controller = WKUserContentController()\n        controller.addUserScript(WKUserScript(\n            source: "document.documentElement.classList.add('ios-native-shell');",\n            injectionTime: .atDocumentStart,\n            forMainFrameOnly: true\n        ))\n        configuration.userContentController = controller\n\n        let webView = WKWebView(frame: .zero, configuration: configuration)\n        webView.navigationDelegate = context.coordinator\n        webView.isOpaque = true\n        webView.backgroundColor = UIColor(red: 0.03, green: 0.18, blue: 0.29, alpha: 1)\n        webView.scrollView.backgroundColor = webView.backgroundColor\n        webView.scrollView.contentInsetAdjustmentBehavior = .never\n        webView.scrollView.bounces = false\n        webView.allowsBackForwardNavigationGestures = false\n        if #available(iOS 16.4, *) { webView.isInspectable = true }\n\n        let request = URLRequest(url: Self.gameURL, cachePolicy: .reloadRevalidatingCacheData, timeoutInterval: 30)\n        webView.load(request)\n        return webView\n    }\n\n    func updateUIView(_ webView: WKWebView, context: Context) {}\n\n    final class Coordinator: NSObject, WKNavigationDelegate {\n        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {\n            guard let url = navigationAction.request.url else { decisionHandler(.cancel); return }\n            if let host = url.host, host != GameWebView.gameURL.host, navigationAction.navigationType == .linkActivated {\n                UIApplication.shared.open(url)\n                decisionHandler(.cancel)\n                return\n            }\n            decisionHandler(.allow)\n        }\n    }\n}\n''')

(assets/'Contents.json').write_text('''{\n  "info" : { "author" : "xcode", "version" : 1 }\n}\n''')
(appicon/'Contents.json').write_text('''{\n  "images" : [\n    { "idiom" : "universal", "platform" : "ios", "size" : "1024x1024" }\n  ],\n  "info" : { "author" : "xcode", "version" : 1 }\n}\n''')

projfile=r'''// !$*UTF8*$!
{
	archiveVersion = 1;
	classes = {};
	objectVersion = 60;
	objects = {

/* Begin PBXBuildFile section */
		A10000000000000000000001 /* ArcticResearchApp.swift in Sources */ = {isa = PBXBuildFile; fileRef = A20000000000000000000001 /* ArcticResearchApp.swift */; };
		A10000000000000000000002 /* ContentView.swift in Sources */ = {isa = PBXBuildFile; fileRef = A20000000000000000000002 /* ContentView.swift */; };
		A10000000000000000000003 /* Assets.xcassets in Resources */ = {isa = PBXBuildFile; fileRef = A20000000000000000000003 /* Assets.xcassets */; };
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
		A20000000000000000000001 /* ArcticResearchApp.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = ArcticResearchApp.swift; sourceTree = "<group>"; };
		A20000000000000000000002 /* ContentView.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = ContentView.swift; sourceTree = "<group>"; };
		A20000000000000000000003 /* Assets.xcassets */ = {isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; };
		A20000000000000000000004 /* ArcticResearch.app */ = {isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = ArcticResearch.app; sourceTree = BUILT_PRODUCTS_DIR; };
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
		A30000000000000000000001 /* Frameworks */ = {isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = (); runOnlyForDeploymentPostprocessing = 0; };
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
		A40000000000000000000001 = {isa = PBXGroup; children = (A40000000000000000000002 /* ArcticResearch */, A40000000000000000000003 /* Products */); sourceTree = "<group>"; };
		A40000000000000000000002 /* ArcticResearch */ = {isa = PBXGroup; children = (A20000000000000000000001 /* ArcticResearchApp.swift */, A20000000000000000000002 /* ContentView.swift */, A20000000000000000000003 /* Assets.xcassets */); path = ArcticResearch; sourceTree = "<group>"; };
		A40000000000000000000003 /* Products */ = {isa = PBXGroup; children = (A20000000000000000000004 /* ArcticResearch.app */); name = Products; sourceTree = "<group>"; };
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
		A50000000000000000000001 /* ArcticResearch */ = {isa = PBXNativeTarget; buildConfigurationList = A90000000000000000000002 /* Build configuration list for PBXNativeTarget */; buildPhases = (A70000000000000000000001 /* Sources */, A30000000000000000000001 /* Frameworks */, A80000000000000000000001 /* Resources */); buildRules = (); dependencies = (); name = ArcticResearch; productName = ArcticResearch; productReference = A20000000000000000000004 /* ArcticResearch.app */; productType = "com.apple.product-type.application"; };
/* End PBXNativeTarget section */

/* Begin PBXProject section */
		A60000000000000000000001 /* Project object */ = {isa = PBXProject; attributes = {BuildIndependentTargetsInParallel = 1; LastSwiftUpdateCheck = 2600; LastUpgradeCheck = 2600; TargetAttributes = {A50000000000000000000001 = {CreatedOnToolsVersion = 26.0;};};}; buildConfigurationList = A90000000000000000000001 /* Build configuration list for PBXProject */; compatibilityVersion = "Xcode 15.0"; developmentRegion = en; hasScannedForEncodings = 0; knownRegions = (en, Base); mainGroup = A40000000000000000000001; productRefGroup = A40000000000000000000003 /* Products */; projectDirPath = ""; projectRoot = ""; targets = (A50000000000000000000001 /* ArcticResearch */); };
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
		A80000000000000000000001 /* Resources */ = {isa = PBXResourcesBuildPhase; buildActionMask = 2147483647; files = (A10000000000000000000003 /* Assets.xcassets in Resources */); runOnlyForDeploymentPostprocessing = 0; };
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
		A70000000000000000000001 /* Sources */ = {isa = PBXSourcesBuildPhase; buildActionMask = 2147483647; files = (A10000000000000000000001 /* ArcticResearchApp.swift in Sources */, A10000000000000000000002 /* ContentView.swift in Sources */); runOnlyForDeploymentPostprocessing = 0; };
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
		B10000000000000000000001 /* Debug */ = {isa = XCBuildConfiguration; buildSettings = {ALWAYS_SEARCH_USER_PATHS = NO; CLANG_ENABLE_MODULES = YES; COPY_PHASE_STRIP = NO; DEBUG_INFORMATION_FORMAT = dwarf; ENABLE_TESTABILITY = YES; GCC_C_LANGUAGE_STANDARD = gnu17; IPHONEOS_DEPLOYMENT_TARGET = 17.0; ONLY_ACTIVE_ARCH = YES; SDKROOT = iphoneos; SWIFT_ACTIVE_COMPILATION_CONDITIONS = "DEBUG $(inherited)"; SWIFT_OPTIMIZATION_LEVEL = "-Onone";}; name = Debug; };
		B10000000000000000000002 /* Release */ = {isa = XCBuildConfiguration; buildSettings = {ALWAYS_SEARCH_USER_PATHS = NO; CLANG_ENABLE_MODULES = YES; COPY_PHASE_STRIP = NO; DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym"; GCC_C_LANGUAGE_STANDARD = gnu17; IPHONEOS_DEPLOYMENT_TARGET = 17.0; SDKROOT = iphoneos; SWIFT_COMPILATION_MODE = wholemodule; VALIDATE_PRODUCT = YES;}; name = Release; };
		B20000000000000000000001 /* Debug */ = {isa = XCBuildConfiguration; buildSettings = {ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon; CODE_SIGN_STYLE = Automatic; CURRENT_PROJECT_VERSION = 1; DEVELOPMENT_ASSET_PATHS = ""; ENABLE_PREVIEWS = YES; GENERATE_INFOPLIST_FILE = YES; INFOPLIST_KEY_CFBundleDisplayName = "Arctic Research"; INFOPLIST_KEY_LSApplicationCategoryType = "public.app-category.games"; INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES; INFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES; INFOPLIST_KEY_UILaunchScreen_Generation = YES; INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight"; IPHONEOS_DEPLOYMENT_TARGET = 17.0; MARKETING_VERSION = 0.1; PRODUCT_BUNDLE_IDENTIFIER = com.ivansavelyev.ArcticResearchSimulator; PRODUCT_NAME = "$(TARGET_NAME)"; SWIFT_EMIT_LOC_STRINGS = YES; SWIFT_VERSION = 5.0; TARGETED_DEVICE_FAMILY = "1,2";}; name = Debug; };
		B20000000000000000000002 /* Release */ = {isa = XCBuildConfiguration; buildSettings = {ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon; CODE_SIGN_STYLE = Automatic; CURRENT_PROJECT_VERSION = 1; ENABLE_PREVIEWS = YES; GENERATE_INFOPLIST_FILE = YES; INFOPLIST_KEY_CFBundleDisplayName = "Arctic Research"; INFOPLIST_KEY_LSApplicationCategoryType = "public.app-category.games"; INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES; INFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES; INFOPLIST_KEY_UILaunchScreen_Generation = YES; INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight"; IPHONEOS_DEPLOYMENT_TARGET = 17.0; MARKETING_VERSION = 0.1; PRODUCT_BUNDLE_IDENTIFIER = com.ivansavelyev.ArcticResearchSimulator; PRODUCT_NAME = "$(TARGET_NAME)"; SWIFT_EMIT_LOC_STRINGS = YES; SWIFT_VERSION = 5.0; TARGETED_DEVICE_FAMILY = "1,2";}; name = Release; };
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
		A90000000000000000000001 /* Build configuration list for PBXProject */ = {isa = XCConfigurationList; buildConfigurations = (B10000000000000000000001 /* Debug */, B10000000000000000000002 /* Release */); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release; };
		A90000000000000000000002 /* Build configuration list for PBXNativeTarget */ = {isa = XCConfigurationList; buildConfigurations = (B20000000000000000000001 /* Debug */, B20000000000000000000002 /* Release */); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release; };
/* End XCConfigurationList section */
	};
	rootObject = A60000000000000000000001 /* Project object */;
}
'''
(proj/'project.pbxproj').write_text(projfile)

(root/'README.md').write_text('''# Arctic Research iOS Test App\n\nThis is a lightweight native SwiftUI/WKWebView test harness for the live Arctic Research Simulator build.\n\n## Why it loads the live game\nThe test app points at the GitHub Pages production URL so normal GitHub game updates appear in the iPhone app without rebuilding the native project every iteration. This is intentional for rapid UI/gameplay testing.\n\n## Run on an iPhone\n1. Install/open Xcode on the Mac.\n2. Open `ArcticResearch.xcodeproj`.\n3. Select the `ArcticResearch` target and choose your Apple Development Team under Signing & Capabilities.\n4. Connect the iPhone, choose it as the run destination, and press Run.\n5. If iOS asks, enable Developer Mode / trust the development certificate.\n\nThe bundle identifier is currently `com.ivansavelyev.ArcticResearchSimulator`; change it in Xcode if your signing account requires a different unique identifier.\n\n## Production direction\nThis wrapper is for device testing. Before App Store submission we can add the native StoreKit bridge, haptics, native app icon/launch treatment, and decide whether the production build should bundle a tested web snapshot rather than load the live development site.\n''')

print('mobile HUD, PWA metadata, pinch zoom, and iOS project staged')
