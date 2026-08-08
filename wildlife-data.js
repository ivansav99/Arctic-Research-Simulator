(() => {
  'use strict';

  const entry = (displayName, scientificName, group, photo, page, facts, options={}) => ({
    displayName,
    scientificName,
    group,
    photo: `assets/wildlife/${photo}`,
    source: `https://en.wikipedia.org/wiki/${page}`,
    credit: 'Photo and species reference: Wikipedia / Wikimedia Commons',
    facts,
    ...options
  });

  window.ARCTIC_WILDLIFE_CATALOG = Object.freeze({
    'BOWHEAD': entry('Bowhead whale', 'Balaena mysticetus', 'Arctic Whales', 'bowhead.jpg', 'Bowhead_whale', [
      'This baleen whale has no dorsal fin, an adaptation that helps it travel beneath sea ice.',
      'Bowheads use an enormous arched skull to break breathing holes through ice.',
      'Some individuals can live for more than two centuries.'
    ]),
    'BELUGA': entry('Beluga whale', 'Delphinapterus leucas', 'Arctic Whales', 'beluga.jpg', 'Beluga_whale', [
      'Adults are white and lack a dorsal fin, helping them move through ice-covered water.',
      'Belugas are highly vocal and are sometimes called the canaries of the sea.',
      'Their neck vertebrae are not fused, allowing them to turn their heads.'
    ], {photoFit:'contain', photoTone:'dark'}),
    'HUMPBACK': entry('Humpback whale', 'Megaptera novaeangliae', 'Arctic Whales', 'humpback.jpg', 'Humpback_whale', [
      'Many humpbacks migrate between high-latitude feeding grounds and warmer breeding waters.',
      'They feed on krill and schooling fish, sometimes using coordinated bubble nets.',
      'Males produce long, structured songs.'
    ], {photoFit:'contain'}),
    'GRAY WHALE': entry('Gray whale', 'Eschrichtius robustus', 'Arctic Whales', 'gray-whale.jpg', 'Gray_whale', [
      'Gray whales are primarily North Pacific visitors to the Arctic.',
      'They often roll on their sides and suction small animals from seafloor sediment.',
      'Their annual coastal migrations are among the longest made by mammals.'
    ]),
    'NARWHAL': entry('Narwhal', 'Monodon monoceros', 'Arctic Whales', 'narwhal.jpg', 'Narwhal', [
      'The famous tusk is an elongated tooth, most commonly found in males.',
      'Narwhals make deep dives beneath Arctic ice to catch fish and squid.',
      'They are concentrated mainly in the Atlantic sector of the high Arctic.'
    ]),

    'RINGED SEAL': entry('Ringed seal', 'Pusa hispida', 'Arctic Pinniped Survey', 'ringed-seal.jpg', 'Ringed_seal', [
      'The ringed seal is the smallest and most ice-associated Arctic seal.',
      'It maintains breathing holes by scraping them with the claws on its foreflippers.',
      'Pups are born in snow lairs constructed above the sea ice.'
    ]),
    'BEARDED SEAL': entry('Bearded seal', 'Erignathus barbatus', 'Arctic Pinniped Survey', 'bearded-seal.jpg', 'Bearded_seal', [
      'Its long whiskers help locate clams and other animals on the seafloor.',
      'Bearded seals are among the largest northern seals.',
      'Adult males produce elaborate underwater calls during the breeding season.'
    ]),
    'SPOTTED SEAL': entry('Spotted seal', 'Phoca largha', 'Arctic Pinniped Survey', 'spotted-seal.jpg', 'Spotted_seal', [
      'Spotted seals live mainly in the North Pacific and adjacent Arctic seas.',
      'They breed on seasonal sea ice and move toward coasts after breakup.',
      'Their diet includes schooling fish, squid and crustaceans.'
    ]),
    'RIBBON SEAL': entry('Ribbon seal', 'Histriophoca fasciata', 'Arctic Pinniped Survey', 'ribbon-seal.jpg', 'Ribbon_seal', [
      'Adults have striking pale bands around the neck, flippers and hips.',
      'They breed and molt on drifting pack ice in the North Pacific sector.',
      'Ribbon seals spend much of the year far offshore.'
    ]),
    'HARP SEAL': entry('Harp seal', 'Pagophilus groenlandicus', 'Arctic Pinniped Survey', 'harp-seal.jpg', 'Harp_seal', [
      'Harp seals make long seasonal migrations through the North Atlantic and Arctic.',
      'Newborn pups begin with a white coat before molting.',
      'Adults develop a dark harp-shaped marking across the back.'
    ]),
    'HOODED SEAL': entry('Hooded seal', 'Cystophora cristata', 'Arctic Pinniped Survey', 'hooded-seal.jpg', 'Hooded_seal', [
      'Adult males can inflate a large nasal hood during displays.',
      'Hooded seals breed on pack ice in the North Atlantic.',
      'They are powerful divers that forage far below the surface.'
    ]),
    'WALRUS': {
      displayName: 'Walrus',
      scientificName: 'Odobenus rosmarus',
      group: 'Arctic Pinniped Survey',
      photo: 'assets/wildlife/walrus.jpg',
      source: 'https://www.fws.gov/media/pacific-walrus-cape-peirce',
      credit: 'Public-domain photograph: U.S. Fish & Wildlife Service',
      facts: [
        'Walruses rest in social groups on shorelines and drifting ice between feeding trips.',
        'Their tusks are enlarged canine teeth used in display and for hauling out of the water.',
        'Sensitive whiskers help them locate clams and other seafloor prey in dim Arctic water.'
      ]
    },

    'POLAR BEAR': entry('Polar bear', 'Ursus maritimus', 'Tundra & Ice Mammals', 'polar-bear.jpg', 'Polar_bear', [
      'Polar bears depend on sea ice as a platform for hunting seals.',
      'Their black skin and dense, water-repellent coat help retain heat.',
      'Broad, partly webbed paws make them strong long-distance swimmers.'
    ]),
    'ARCTIC FOX': entry('Arctic fox', 'Vulpes lagopus', 'Tundra & Ice Mammals', 'arctic-fox.jpg', 'Arctic_fox', [
      'Many Arctic foxes change from a brown summer coat to white winter fur.',
      'They cache surplus food and can locate prey beneath snow.',
      'Some tundra den systems have been used for many generations.'
    ]),
    'CARIBOU': entry('Caribou', 'Rangifer tarandus', 'Tundra & Ice Mammals', 'caribou.jpg', 'Reindeer', [
      'Caribou and reindeer are the same species; caribou is the usual North American name.',
      'Many herds migrate great distances between calving and winter ranges.',
      'Both females and males can grow antlers.'
    ]),
    'REINDEER': entry('Reindeer', 'Rangifer tarandus', 'Tundra & Ice Mammals', 'reindeer.jpg', 'Reindeer', [
      'Eurasian populations include both wild and domesticated herds.',
      'Wide hooves spread on soft ground and help dig through snow for food.',
      'Lichens are especially important during winter.'
    ]),
    'SVALBARD REINDEER': entry('Svalbard reindeer', 'Rangifer tarandus platyrhynchus', 'Tundra & Ice Mammals', 'svalbard-reindeer.jpg', 'Svalbard_reindeer', [
      'This compact, short-legged subspecies occurs only in Svalbard.',
      'It stores conspicuous fat reserves before winter.',
      'Unlike many continental caribou, it makes relatively short seasonal movements.'
    ]),

    'SNOWY OWL': entry('Snowy owl', 'Bubo scandiacus', 'Arctic Summer Birds', 'snowy-owl.jpg', 'Snowy_owl', [
      'Snowy owls breed on open tundra and often follow fluctuations in lemming abundance.',
      'They readily hunt during the continuous daylight of Arctic summer.',
      'Females are generally larger and more heavily barred than adult males.'
    ]),
    'KING EIDER': entry('King eider', 'Somateria spectabilis', 'Arctic Summer Birds', 'king-eider.jpg', 'King_eider', [
      'King eiders nest on high-Arctic tundra near lakes or coasts.',
      'At sea they dive for mollusks, crustaceans and other bottom animals.',
      'Large flocks gather in productive molting and wintering areas near sea ice.'
    ]),
    'COMMON EIDER': entry('Common eider', 'Somateria mollissima', 'Arctic Summer Birds', 'common-eider.jpg', 'Common_eider', [
      'Female eiders line their nests with exceptionally warm down.',
      'They feed heavily on mussels and other shellfish in coastal water.',
      'Dense breeding colonies occur on many Arctic islands and shores.'
    ]),
    'ARCTIC TERN': entry('Arctic tern', 'Sterna paradisaea', 'Arctic Summer Birds', 'arctic-tern.jpg', 'Arctic_tern', [
      'Arctic terns migrate between northern breeding grounds and southern-ocean waters.',
      'Their annual journey is among the longest migrations of any animal.',
      'They plunge-dive for small fish near the water surface.'
    ]),
    'BARNACLE GOOSE': entry('Barnacle goose', 'Branta leucopsis', 'Arctic Summer Birds', 'barnacle-goose.jpg', 'Barnacle_goose', [
      'Barnacle geese breed on Arctic islands and coasts.',
      'Many populations migrate to northwestern Europe for winter.',
      'They graze on grasses, sedges and other low vegetation.'
    ]),
    'PINK-FOOTED GOOSE': entry('Pink-footed goose', 'Anser brachyrhynchus', 'Arctic Summer Birds', 'pink-footed-goose.jpg', 'Pink-footed_goose', [
      'This goose breeds in Greenland, Iceland and Svalbard.',
      'Most spend winter in northwestern Europe.',
      'They are strongly migratory and feed mainly on plant material.'
    ]),
    'BRENT GOOSE': entry('Brent goose', 'Branta bernicla', 'Arctic Summer Birds', 'brent-goose.jpg', 'Brant_(goose)', [
      'Brent geese breed on tundra around the high Arctic.',
      'They are smaller and darker than most geese.',
      'Eelgrass and other coastal vegetation are important winter foods.'
    ]),
    'SNOW GOOSE': entry('Snow goose', 'Anser caerulescens', 'Arctic Summer Birds', 'snow-goose.jpg', 'Snow_goose', [
      'Snow geese occur in both white and blue color morphs.',
      'They breed across Arctic North America.',
      'Migrating flocks can contain many thousands of birds.'
    ]),
    'THICK-BILLED MURRE': entry('Thick-billed murre', 'Uria lomvia', 'Arctic Summer Birds', 'thick-billed-murre.jpg', 'Thick-billed_murre', [
      'These seabirds nest in crowded colonies on narrow cliff ledges.',
      'They use their wings to pursue fish and invertebrates underwater.',
      'Parents carry a single fish crosswise in the bill to feed their chick.'
    ]),

    'ARCTIC COD': entry('Arctic cod', 'Boreogadus saida', 'Arctic Fish Survey', 'arctic-cod.jpg', 'Boreogadus', [
      'This game label refers to Boreogadus saida, also called polar cod.',
      'It is closely associated with cold water and sea ice.',
      'It is a crucial prey species for Arctic seabirds, seals, whales and larger fish.'
    ]),
    'SAFFRON COD': entry('Saffron cod', 'Eleginus gracilis', 'Arctic Fish Survey', 'saffron-cod.jpg', 'Saffron_cod', [
      'Saffron cod inhabit shallow North Pacific and Arctic coastal waters.',
      'They can tolerate brackish estuaries and river mouths.',
      'They support both regional fisheries and marine food webs.'
    ]),
    'CAPELIN': entry('Capelin', 'Mallotus villosus', 'Arctic Fish Survey', 'capelin.jpg', 'Capelin', [
      'Capelin are small schooling forage fish that feed mainly on plankton.',
      'They transfer energy to cod, seabirds, seals and whales.',
      'Dense spawning gatherings can occur near shore.'
    ], {photoFit:'contain'}),
    'PACIFIC HERRING': entry('Pacific herring', 'Clupea pallasii', 'Arctic Fish Survey', 'pacific-herring.jpg', 'Pacific_herring', [
      'Pacific herring form large coastal schools.',
      'Their adhesive eggs are deposited on vegetation and other shallow surfaces.',
      'They are important prey for fish, birds and marine mammals.'
    ]),
    'ATLANTIC HERRING': entry('Atlantic herring', 'Clupea harengus', 'Arctic Fish Survey', 'atlantic-herring.jpg', 'Atlantic_herring', [
      'Atlantic herring form large pelagic schools and feed mainly on plankton.',
      'Different populations have distinct migrations and spawning seasons.',
      'They are a major link between plankton and larger predators.'
    ], {photoFit:'contain'}),
    'SAND LANCE': entry('Sand lance', 'Ammodytidae', 'Arctic Fish Survey', 'sand-lance.jpg', 'Sand_lance', [
      'Sand lance is a group name for slender schooling forage fishes.',
      'They burrow into sandy sediment when resting or avoiding predators.',
      'They are important food for seabirds, larger fish and marine mammals.'
    ]),
    'GREENLAND HALIBUT': entry('Greenland halibut', 'Reinhardtius hippoglossoides', 'Arctic Fish Survey', 'greenland-halibut.jpg', 'Greenland_halibut', [
      'This cold-water flatfish inhabits deep northern seas.',
      'It is an active midwater predator as well as a bottom-associated fish.',
      'Greenland halibut supports valuable Arctic fisheries.'
    ], {photoFit:'contain'}),
    'NORTHEAST ARCTIC COD': entry('Northeast Arctic cod', 'Gadus morhua', 'Arctic Fish Survey', 'northeast-arctic-cod.jpg', 'Atlantic_cod', [
      'This is a migratory stock of Atlantic cod rather than a separate species.',
      'It feeds in the Barents Sea and migrates toward northern Norway to spawn.',
      'Spawning migrants are commonly known as skrei.'
    ])
  });
})();
