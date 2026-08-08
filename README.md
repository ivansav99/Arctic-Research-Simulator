# Arctic Research — Expedition Prototype

This folder is the independent research-management edition of the Arctic navigation game. The earlier version in the parent folder remains untouched.

## Launch

Open `index.html` in a modern browser. No build step, server, sign-in, or internet connection is required; all game art and data are stored locally.

## First expedition

1. Choose one of six Chief Scientist avatars and a starting specialization. “You” are a permanent, salary-free member of the team and cannot be hired, replaced, or dismissed.
2. Open Longyearbyen port. F/V Isfjord begins equipped with a hull echosounder, three berths, and three light-equipment slots.
3. Review up to two local research-grant offers. Starter grants concentrate in Svalbard’s fjords and nearby research stations, and the grant market takes seven game days to refresh.
4. Click a research marker or its direction card. A distant site becomes a navigation destination and opens only when the vessel reaches operating range.
5. Complete each station’s compact live checklist. Multi-point transects must be visited in order; returning to port before finishing resets that section.
6. Explore tight channels and fjords for unadvertised opportunities, collect wildlife observations, buy instruments, recruit a team, and build a publication record.

## Observation and exploration

- A wildlife individual or school with a glowing gold ring is worth exactly `+2 DATA`. The ring disappears after the first observation, and the same individual cannot be scored again during that expedition.
- Wildlife briefings show the data award explicitly and still include the locally cached field-guide photograph and facts.
- Fjords, narrow channels, river mouths, ice edges, open water, and weather events can generate spontaneous research opportunities. A readiness checklist shows the required vessel, scientists, equipment, lab supplies, and enough food and fuel to finish and return.
- The Arctic now has named traffic: fishing vessels, Svalbard cruise ships, private sailing vessels, Iñupiat whaling umiaks near Utqiaġvik, and working research vessels. Each has a distinct map symbol and a clickable vessel profile. A more capable research ship may give a one-time emergency top-up to a junior expedition.
- The minimap’s geographic extent follows the main-map zoom: the starter view focuses tightly on Svalbard, while larger vessels progressively unlock a wider Arctic overview.

## Expedition systems

- The vessel itself has no daily charge. Scientists draw daily salaries; fuel, food, lab supplies, instruments, and expendable platforms are charged explicitly.
- `RESUPPLY ALL` fills every store the expedition can afford. Fuel or food below 20% raises a persistent flashing alert. Leaving port below 50% opens a departure review. A failed expedition returns to the last port with each depleted store restored to at least 25%.
- Fishing vessel, fishing trawler, coastal, global, icebreaker, and nuclear-icebreaker classes provide 3, 5, 10, 20, 30, and 40 scientist berths. Larger ships unlock progressively wider chart overviews, more deck slots, deeper handling systems, and stricter senior-scientist command gates.
- Grant capacity equals the number of scientists currently aboard, including the Chief Scientist. Deployment/recovery work continues to occupy a grant slot while instruments collect data.
- Longyearbyen sells progressively unlocked conventional vessels. Murmansk sells only the nuclear icebreaker, and it is the only port where that ship appears. Russian scientists appear only in Russian hiring pools.
- Buying a vessel trades in the current hull and all installed equipment for 50% of purchase price. The crew transfers automatically; if a smaller vessel lacks berths, the newest non-player hires remain ashore.
- The basic icebreaker has one helideck; the nuclear icebreaker has two. Long-range drones and research helicopters unlock aerial, atmospheric, sea-ice, wildlife, and air-dropped ocean-profile work while extending useful sensor range in fog.
- Every information or research window pauses vessel motion, current drift, supplies, wildlife, weather, and the calendar. Research animation continues and then holds the complete checklist and results until `OKAY` is pressed.

## Instruments and missions

The equipment catalog lists installed systems first, followed only by items that physically fit the current vessel. An unaffordable or crew-inoperable item has a disabled purchase control and red price. Opening one item’s illustrated specifications automatically closes the previous item. Installed equipment can be sold for half its purchase price unless it is deployed at sea.

Every purchasable system has field work associated with it. The catalog includes:

- Portable water-quality sondes, field cameras, service tools, small ROVs, sea-ice augers/corers, shallow sediment samplers, and expendable XBT, sonobuoy, radiosonde, and drifter packs.
- 1200, 600, 300, and 75 kHz ADCP systems spanning shallow fjords through deep-ocean profiling, plus a scientific EK80 echosounder for fish and plankton acoustics.
- A-frames, medium and heavy winches, CTD rosettes, work-class ROVs, box corers, acoustic arrays, research radar, profiling aerostats, drones, helicopters, floats, ice-tethered profilers, and composite deep moorings.
- Local kelp-forest ROV surveys, coastal field-team delivery, shallow-water sampling, harbor bathymetry, ADCP sections, EK80 acoustic transects, coring, coastal mooring service, and progressively larger Arctic sections.

Long-term stations use staged deployment and recovery. Their data and sponsor payment remain sealed until successful recovery, which may be weeks, months, or a year later. Expendable drifting platforms return telemetry after an autonomous collection period.

## Research progression

Graduate students can operate light systems, postdocs can lead medium systems, and professors are needed for heavy work. A postdoc or professor is required before buying the coastal vessel; two professors unlock the global vessel, with larger command teams required for icebreakers.

Crew careers advance aboard the expedition. A graduate student becomes a postdoc after two published papers and ten specialty missions. A postdoc becomes a professor after ten published papers and fifty specialty missions; clearance and salary update automatically.

When all berths are full, choosing an eligible recruit activates `REPLACE` beside each non-player crew member. A replaced scientist remains in that port’s hiring pool for the rest of the call so an accidental replacement can be reversed.

The first risky paper attempt opens at 120 data. More data and stronger scientists improve acceptance and long-term citations. Starlink improves collaboration and shortens the submission cooldown. Accepted work is placed in an appropriate research journal in the field record; awards come from the sponsor, not the journal.

## Image sources

Research and equipment reference photographs are locally cached from official or program sources and retain their credit/source link inside the relevant card:

- NOAA Ocean Exploration: XBTs, CTD rosettes, ROV systems, and research vessels
- NOAA Fisheries: passive-acoustic arrays, sonobuoys, and aerial wildlife surveys
- NOAA Physical Sciences Laboratory and NOAA/NCEI: W-band radar and weather balloons
- NOAA Office of Response and Restoration: Arctic field, aircraft, aerostat, buoy, and vessel imagery
- NASA Earth Observatory: river-plume imagery
- Argo Program / Scripps Institution of Oceanography: profiling-float imagery

Face-free equipment illustrations, scientist portraits, and the sailing/umiak vessel art are original generated assets for this prototype. Wildlife photographs retain their attribution links in the field guide; the walrus photograph is a public-domain U.S. Fish & Wildlife Service image.


## Arctic terrain / bathymetry texture

The overview/minimap uses the GEBCO north-polar bed-topography image in WGS 84 / IBCAO Polar Stereographic (EPSG:3996). The close main chart no longer stretches that overview. At normal and close zoom it requests only the visible 128 km x 128 km terrain tiles as 1024 x 1024 PNGs (about 125 m requested pixel spacing), keeps a 32-tile least-recently-used cache, and falls back to the overview while a tile is loading. This gives the close chart much more detail without loading the entire Arctic raster at startup.

When the IBCAO/GEBCO terrain is available, its land/water boundary is the visible coastline; the older Natural Earth polygons are no longer painted on top. The game also attempts to derive a 512 x 512 land/water mask from each loaded terrain tile for collision and navigation checks (about 250 m mask spacing). If browser cross-origin security prevents pixel access to the WMS image, navigation temporarily falls back to the older polygon mask even though the visible coastline remains IBCAO/GEBCO.

The world coordinate conversion now uses the actual EPSG:3996 polar stereographic projection rather than the earlier constant-kilometres-per-degree approximation. Seasonal land tint is applied only to raster-derived land pixels: lower-latitude terrain is greener in summer, while high latitude, high-relief terrain and winter conditions progressively shift toward snow/white.

The original 847 MB `IBCAO_v4_2_13_400m_bedrock.tif` in the separate Arctic Map Drive folder is retained as the source reference. The Drive connector cannot transfer a file that large in one request, so the running game uses GEBCO's official Arctic WMS from the same IBCAO/GEBCO data family rather than bundling the source GeoTIFF. The legacy procedural bathymetry and Natural Earth coastline remain only as an offline/failure fallback. Terrain is for visualization/gameplay and not for navigation.


## Expedition 12 progression and research pass

- Field research sites use question-mark markers. Eligible field opportunities glow green; official accepted grants retain gold navigation guidance and minimap direction cues.
- Chief Scientist progression is now a hard gate: Postdoc requires 2 published papers and 100 citations; Professor requires 10 published papers and 1,000 citations. Postdocs cost 100 citations of senior-hiring capacity each; professors cost 1,000. Graduate-student hiring remains citation-unlimited.
- Postdoc status unlocks coastal-class research vessels and medium-duty equipment. Professor status unlocks global vessels, icebreakers, heavy equipment, highest-complexity programs, and professor-originated grant proposals while at sea.
- The larger F/V adds a wider 145% chart view. The starter F/V has three close-detail levels (180%, 230%, 280%); game-time progression scales inversely with chart zoom.
- Light-equipment options now include several plankton nets, a portable fluorometer, eDNA filtration gear, and an all-sky aurora camera. Expendables display and enforce per-item storage caps.
- Fjord research now strongly favors coastal/plankton programs; glacier and shore work is constrained to appropriate terrain, with Svalbard glacier anchors based on real glacier locations.
- Dark-season weather can produce aurora events and atmospheric research opportunities. Seasonal terrain overlay retains year-round high-elevation/glacier snow and strengthens snow cover into winter.
- Successful publications no longer impose a submission cooldown. Research-operation windows show all qualified scientists and equipment in use.

## Browser saves and analytics (Expedition 13)

The game now keeps one automatic save and three manual save slots in browser `localStorage`. Saves remain on the same browser/device and include both navigation state and the research-program state.

Google Analytics 4 instrumentation is built in but remains disabled until a GA4 Measurement ID is supplied. Set the ID in `index.html`:

```html
<meta name="ar-analytics-id" content="G-XXXXXXXXXX">
```

When configured, the game sends gameplay events such as game starts/loads/saves, session duration, menu and research UI actions, navigation interactions, port visits, grant activity, mission starts/completions, station completion, publications, scientist/equipment/vessel changes, wildlife observations, resupply actions, and game-over reasons. Events also carry current gameplay context (game date, vessel, resources, money, citations, data, crew/equipment/grant counts, completed missions, papers, wildlife observations, and active play time). No player name, email address, or real-world location is intentionally collected by the game code.
