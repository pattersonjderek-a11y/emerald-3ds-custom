# Stage C rules: seeded core species randomizer

## Stage D difficulty (current)

New records use content rules `0x00030001`, schema 1 and algorithm 1. The species
pool and randomizer mixing algorithm are unchanged, but new content IDs enter
keys; new D seeds can differ from C. Existing C Normal record keys are preserved
by decoding their original rules. No automatic save import is provided.

| Rule | Normal | Hard | Custom |
| --- | --- | --- | --- |
| Cap | Off | Hard progression ceiling | Off / hard / soft |
| Style | Player choice | Set, including actual battle prompt and Options display | Choice / Set |
| Trainer bag healing, revival, status and PP recovery | Allowed | Blocked | Independent toggle |
| Trainer bag stat boosts, Focus Energy, Mist | Allowed | Blocked | Independent toggle |
| AI | Native baseline | Tactical | Native / tactical |
| Bosses | Native templates | Prepared variants | Native / prepared |
| EXP | Inherited | Unchanged below cap | Same; multipliers unavailable |

Hard and Custom apply independently to Standard/Randomized. Settings are saved
once and cannot change during play. LEFT/RIGHT at confirmation shows the explicit
rule summary; START in play opens Run Settings, A toggles the read-only rule page.
The existing player style preference is preserved while forced Set is active.

Caps use the **first missing badge**, not badge count. Before Roxanne 15; Brawly
19; Wattson 24; Flannery 29; Norman 31; Winona 33; Tate/Liza 42; Juan 46; all
four Elite Four members and Champion 58. The whole League uses one cap, including
retries. First Champion status lifts it to 100, including rematches/postgame.
These match native main-campaign ace levels, without boosting every trainer.
Hard clamps battle EXP after all existing bonuses and caps Rare/EXP Candies and
daycare. Already over-cap gifts are neither delevelled nor erased; they gain no
new EXP until the cap passes them. Soft only scales **battle** EXP at/above the
progression threshold by 1/4, 1/8, 1/16, 1/32, then 1/64. It allows higher levels,
candies and daycare; there is no reduced EXP below the threshold. No EV cap or
extra grind penalty is added. Caps/obey rules are distinct: catches are allowed.

Restrictions are checked in native item validation before consumption/turn use.
They affect player bag medicine/X-items in ordinary campaign trainer battles,
including doubles. Wild medicine, ball throwing, held-item effects, overworld
healing, catch/intro tutorials, key items and scripted actions retain native
behavior. NPC bag items remain their native template items. Link/recorded,
Frontier, Trainer Hill, Secret Base and e-reader battles retain native item/AI
policy. Scripted allies keep their original team/AI; no extra omniscience.

Tactical AI adds CHECK_BAD_MOVE, TRY_TO_FAINT, CHECK_VIABILITY, HP_AWARE,
SMART_SWITCHING, SMART_MON_CHOICES, PP_STALL_PREVENTION and RANDOMIZE_SWITCHIN.
It removes full or separate ability/item/move OMNISCIENCE, switch/move/incoming
prediction, assumptions and KNOW_OPPONENT_PARTY inherited from a template.
Double-battle flags still come from the native dispatcher. Native battle RNG
still drives AI decisions; seeded identity does not promise identical actions.

There were no Hard entries in the integration. D adds 49 native Difficulty: Hard
variants covering all eight Gym Leaders and rematches, Elite Four, Champion,
Archie and Maxie. Their 238 party entries retain levels, size, doubles/singles,
identity/rewards, and existing special/gimmick items. IVs become 31 in all stats,
EVs 64 in each stat (384 total); empty held-item slots gain Oran below level 20,
Sitrus otherwise. Fixed Roxanne's second Geodude becomes Aron with Metal Claw,
Mud-Slap, Rock Tomb and Harden; Brawly's Meditite uses Confusion instead of Focus
Punch. Other fixed bosses retain their curated moves and roster composition.
Trainers without a prepared entry safely use their native template. Prepared
variants retain native AI flags; the saved tactical toggle adds stronger policy
in the real dispatcher, so Custom prepared bosses plus native AI remain independent.

Composition: choose prepared/native template → preserve levels/party size and
seeded pool ordering → randomize eligible species → native legal ability/item/
level-up moves → prepared randomized bosses select damaging level-up moves by
power/accuracy, STAB and type coverage, retaining one available native status
move → validate usable moves. Hard never writes original species back. The
prepared-boss adapter is scoped to enemy generation; context clears before
scripted ally/player generation. Rival family and Mega/Primal compatibility
remain C's existing rules. Higher difficulty does not disable randomized bosses.

Runtime difficulty reads the CRC/binding/version-validated record without repeating
whole-pool selection on every Options/AI/cap read; Continue and menu preflight
still validate pool usability.

Production host fixtures and native linked-data audits verify the rules; actual
battle balance, original-XL performance and complete campaign testing remain
pending. Gen 1–9 data/art eligibility still differs from full follower coverage.

## Historical Stage C baseline rules

Implementation: `custom_random_core.c` and `custom_random.c` in the canonical
expansion patch; locked engine `dfb0f843`. Schema 1 / algorithm 1 / content rules
`0x00020001`. Same seed **and options, algorithm, rules and content** reproduce
selection. This is a native runtime randomizer; no external ROM patch is used.

## Setup and composition

Standard/Normal retains fixed native encounters, starters and trainer templates,
with inherited expansion/QoL behavior. Randomized/Normal defaults starters,
wild and enemy trainers ON. Each has an independent switch; at least one must
remain enabled. All nine generations default enabled; at least one is required.
No-legendaries and similar-strength default OFF (unrestricted valid pool).
In the historical C build, Hard/Custom difficulty, abilities, field/hidden-item randomization and held-item
randomization remain unavailable, including at serialization. Ordinary inherited
item rewards, graphical options and native difficulty remain unchanged.

Order: select the native trainer/template and levels → select eligible replacement
species → native level-up moves/ability/gender and compatible item → create party.
Future difficulty stages must keep this ordering and must not restore fixed boss
species after randomization. No boss roster is revealed in Run Settings.

## Algorithm and identities

All arithmetic is unsigned 32-bit. `Mix(x)` applies XOR-right-16, multiply
`0x7FEB352D`, XOR-right-15, multiply `0x846CA68B`, XOR-right-16. Begin with
`Mix(seed XOR stream)`, then successively `Mix(value XOR field)` for content
rules, algorithm, key A, key B, slot. Stream constants are STARTERS `0x53545254`,
WILD `0x57494C44`, TRAINERS `0x54524E52`, PARTY `0x50525459`.
Bounded draws add `0x9E3779B9`, mix and reject values below `(0-count)%count`
before modulo. Candidate enumeration is ascending internal species ID. No
process address, mutable global RNG or save trainer ID participates in keys.

| Selection | Key A | Key B | Slot |
| --- | --- | --- | --- |
| Starter | 0 | 0 | 0–2, with earlier choices excluded |
| Wild table | `(mapGroup << 16) OR mapNum` | `(timeOfDay << 8) OR method` | Original native table slot |
| Trainer replacement | Effective campaign trainer ID | 0 | Actual selected party slot |
| Trainer generation/pool shuffle | Effective campaign trainer ID | 0 | 0, PARTY stream |

Wild method order: land, water, rock smash, fishing, hidden. Native fishing-rod
slot ranges and native time-of-day table selection remain intact. All table
readers share one resolver; cache eviction/reload recomputes the same mapping.
Native global RNG still controls encounter occurrence, slot choice, personality,
shiny odds and battle actions. Those are not the seeded table identity promise.
Changing the trainer toggle does not change wild/starter mappings. Optional
future systems require separate streams.

## Eligibility and balance

Require enabled nonzero National Dex/base HP, native first ability, level-up
learnset with a usable damaging move, and indexed nonstub front/back/icon plus
normal/shiny palette payloads. Compressed palette sizes vary and need not be
32 bytes. Exclude eggs/empty IDs, Mega/Primal/Ultra Burst/Gigantamax/Tera/Totem
battle forms and nonbase nonregional alternate forms, including Galarian Zen
Darmanitan. Stable Alolan/Galarian/Hisuian/Paldean regional forms are eligible
when their native data/assets pass. Cosmetic/signature alternate forms wait for
explicit dependency coverage; base forms keep native ability/form behavior.

National Dex boundaries determine original generations; regional forms belong
to their introduction generation (Alola 7, Galar/Hisui 8, Paldea 9). No-legendaries
excludes restricted/sublegendary/mythical and Ultra Beast flags. Similar strength
uses the original species' BST, inclusive 80–120%. If no candidate meets that
band, relax **only** BST, preserving generation, legendary, distinctness and
safety restrictions. Empty pools return failure; startup/Continue preflight
rejects unusable configurations without rewriting the save.

Every selected species must have a usable level-up damaging move at the minimum
encounter/trainer/starter level. Snore, Dream Eater, Last Resort, Explosion and
Self-Destruct do not satisfy the guaranteed attack check. Native generated moves
are retained when usable; otherwise add an available legal level-up attack in
slot 1. No universal move is taught. This safety filter means a Gen 9 pool entry
is not necessarily selectable at every early level.

## Starters, wild identity and trainers

Three distinct starter choices are selected at level 5. The shared native getter
feeds displayed species/name/cry and the actual gift. The gift's moves are checked.
The original level-2 intro battle and Wally tutorial remain their scripted species.
Wild rates, levels and slot probabilities are unchanged. Visible overworld mons
receive the resolved table species before creation; battle consumes their existing
species/personality/shiny state and does not randomize again. Timed replacement
species lists are bypassed when wild randomization is active so they cannot
replace the mapped species; native time-of-day table choice still works.

Campaign trainer IDs include Gym Leaders, Elite Four, Champion, rival and
rematch templates; these are not broadly excluded. Preserve selected size/level,
IV/EV/nature intent, including the native two-opponent party-size handling. Clear
old custom moves/nickname, use species-appropriate native level-up moves, native
first ability and random gender. Clear template-only Tera/Gigantamax factors.
Trainer-generation and pool-selection RNG is local and saved-seed keyed.

Ordinary held items remain. Species-specific plates/memories/drives/Z crystals,
masks/orbs and signature stat items are removed when incompatible with changed
species. For Mega/Primal item templates, preferentially pick an eligible base
species with a native compatible form item and substitute that item. If the
user's filters exclude all compatible candidates, use the ordinary pool and
remove the unusable item. This compatibility adjustment is not item randomization.
Existing Mega battle mechanics still require console verification.

The native rival class's original Hoenn starter-family slot uses the player's
chosen index + 1 modulo 3, consistently through rematches. Advance the replacement
by the original template's evolution stage only through ordinary eligible level
evolutions available by that battle's level. Respect pool assets, generation,
legendary filter and usable moves. Otherwise retain its prior form. Item, trade
and other conditional evolutions are not forced. This also works with starters
ON and trainers OFF; other rival party members stay fixed in that configuration.
With trainers ON and starters OFF, the player keeps fixed starters while the rival
uses the corresponding stable seeded family, respecting the generation filter.
Rival rematches do not choose a new family from their different trainer IDs.

## Protected/inherited cases and evidence limits

Scripted gifts/eggs, special static encounters, roamers, outbreaks and Feebas
remain inherited, as do Wally/tutorial species and scripted partner generation.
Link/recorded battles, Frontier, Trainer Hill, Secret Base and noncampaign IDs
are excluded from campaign trainer randomization; Pike/Pyramid encounter arrays
are separate. Future support must add explicit hooks and tests. Ordinary land,
water, fishing, rocks, hidden and visible table encounters use the core mapping.

Production core/native adapters execute under host ASan/UBSan with synthetic
engine fixtures; the linked ARM species/graphics pool is independently audited.
A passing native compile is not a console battle test. Actual sprites, cries,
visible transitions, doubles, partners, bosses and Mega behavior remain PENDING
in DEVICE_TESTS.md. The complete follower/cry/evolution/ability coverage audit is
Stage E; eligible data is not a claim of a complete Gen 1–9 campaign or artwork.
