# Fixed Hoenn campaign roster — Stage F

`hoenn-expanded-f1`: 51 fixed land slots across 22 maps. All randomizers OFF
uses these native tables. Species randomization permutes this roster through
v0.5.0; its timed slots and all original local species remain available.
Levels, rates, slot weights, water/fishing/rocks, scripted gifts/tutorials and
Normal trainer rosters are preserved. Hard/Custom retain the tested D/E rules.
No claim that every Gen 1–9 species is catchable or that a campaign is completed.

`tools/campaign_f.json` is the placement specification; the engine JSON is in
`patches/pokeemerald-expansion/0001-port.patch`. The source audit reverses only
listed species substitutions and requires the exact Stage E canonical baseline.
The native land-table inventory finds 155 distinct National Dex species across all nine generations in 124 compiled headers (land tables only).
The linked ARM-data audit verifies actual header slot/species/level, a usable
legal level-up attack and indexed front/back/icon/palette. GDB reads data only.

| Area | Slot (zero based) | Pokémon | Dex | Level | Phase |
| --- | ---: | --- | ---: | --- | --- |
| ROUTE101 | 3 | LECHONK | 915 | 3 | campaign |
| ROUTE101 | 10 | BIDOOF | 399 | 3 | campaign |
| ROUTE102 | 6 | SHINX | 403 | 3 | campaign |
| ROUTE102 | 8 | FIDOUGH | 926 | 4 | campaign |
| ROUTE104 | 0 | STARLY | 396 | 4 | campaign |
| ROUTE104 | 9 | FLETCHLING | 661 | 4 | campaign |
| PETALBURG_WOODS | 0 | GRUBBIN | 736 | 5 | campaign |
| PETALBURG_WOODS | 6 | SEWADDLE | 540 | 6 | campaign |
| ROUTE116 | 8 | ROOKIDEE | 821 | 7 | campaign |
| ROUTE116 | 9 | YAMPER | 835 | 8 | campaign |
| ROUTE116 | 11 | NACLI | 932 | 8 | campaign |
| ROUTE110 | 2 | PAWMI | 921 | 12 | campaign |
| ROUTE110 | 6 | TOXEL | 848 | 13 | campaign |
| ROUTE110 | 9 | WATTREL | 940 | 12 | campaign |
| ROUTE117 | 2 | BUDEW | 406 | 14 | campaign |
| ROUTE117 | 8 | SMOLIV | 928 | 14 | campaign |
| ROUTE117 | 9 | CUTIEFLY | 742 | 14 | campaign |
| ROUTE112 | 3 | LITLEO | 667 | 14 | campaign |
| ROUTE112 | 8 | ROLYCOLY | 837 | 16 | campaign |
| FIERY_PATH | 6 | SALANDIT | 757 | 16 | campaign |
| FIERY_PATH | 8 | CHARCADET | 935 | 14 | campaign |
| ROUTE113 | 4 | SNOM | 872 | 14 | campaign |
| ROUTE113 | 8 | SNOVER | 459 | 16 | campaign |
| METEOR_FALLS_1F_1R | 1 | NOIBAT | 714 | 17 | campaign |
| METEOR_FALLS_1F_1R | 8 | CARBINK | 703 | 19 | campaign |
| ROUTE111 | 6 | SANDILE | 551 | 19 | campaign |
| ROUTE111 | 7 | SILICOBRA | 843 | 19 | campaign |
| ROUTE111 | 10 | RELLOR | 953 | 22 | campaign |
| ROUTE114 | 2 | SKIDDO | 672 | 17 | campaign |
| ROUTE114 | 6 | DEERLING | 585 | 16 | campaign |
| ROUTE118 | 7 | BUIZEL | 418 | 25 | campaign |
| ROUTE118 | 9 | KILOWATTREL | 941 | 26 | campaign |
| ROUTE119 | 4 | FOMANTIS | 753 | 27 | campaign |
| ROUTE119 | 9 | GOOMY | 704 | 26 | campaign |
| ROUTE120 | 2 | IMPIDIMP | 859 | 27 | campaign |
| ROUTE120 | 7 | HATENNA | 856 | 27 | campaign |
| ROUTE121 | 4 | MURKROW | 198 | 28 | campaign |
| ROUTE121 | 10 | DREEPY | 885 | 28 | campaign |
| ROUTE123 | 4 | SKWOVET | 819 | 28 | campaign |
| ROUTE123 | 6 | MORELULL | 755 | 28 | campaign |
| MT_PYRE_1F | 4 | LITWICK | 607 | 29 | campaign |
| MT_PYRE_1F | 8 | GREAVARD | 971 | 29 | campaign |
| MT_PYRE_1F | 10 | MIMIKYU | 778 | 29 | campaign |
| SHOAL_CAVE_LOW_TIDE_INNER_ROOM | 4 | BERGMITE | 712 | 30 | campaign |
| SHOAL_CAVE_LOW_TIDE_INNER_ROOM | 11 | CETODDLE | 974 | 32 | campaign |
| VICTORY_ROAD_1F | 6 | RIOLU | 447 | 38 | campaign |
| VICTORY_ROAD_1F | 7 | FRIGIBAX | 996 | 38 | campaign |
| VICTORY_ROAD_1F | 10 | DEINO | 633 | 36 | campaign |
| DESERT_UNDERPASS | 2 | GIBLE | 443 | 40 | postgame |
| DESERT_UNDERPASS | 6 | DRILBUR | 529 | 38 | postgame |
| DESERT_UNDERPASS | 10 | DURALUDON | 884 | 44 | postgame |

## Progression and postgame evidence

Only wild species and the content-rules identifier change in engine sources
relative to E. No progression scripts, HM checks, event flags, rewards, badges,
starter gifts, trainers, rematches or facilities are edited. Keeping each original
local species also preserves the inherited supply of field-move learners.
This is source evidence, not a reachability proof or a playthrough.

Production difficulty tests exercise all badge caps, League/champion and postgame
boundaries, daycare/candies and representative trainer/partner composition.
The existing optional-rule tests cover protected progression items. DEVICE_TESTS.md
lists the actual-console progression route and postgame cases; every F row is pending.

Simple device proof without randomization: Route 101 slot 3 is Lechonk (#915)
at level 3, with 10% of ordinary land-slot selections. Encounter occurrence remains
random; this is not a promise of one encounter every ten steps. The pre-existing
upstream timed rules use different slots, so this placement survives all clock phases.
