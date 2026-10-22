# Run configuration save format (Stages B/C/D)

Schema 1 is native-expansion-only and stores critical run state in the same
flash-sector transaction as progress. It is separate from the port's global
graphical/QoL settings. No sidecar, event flag, game variable or external index
is used. All generated test buffers are synthetic; no private save is committed.

## Allocation audit

Pinned engine: `dfb0f84374230f4d462191601179b742f9f077df` with this repository's
expansion patch and native build defines. `FREE_EXTRA_SEEN_FLAGS_SAVEBLOCK1`
is FALSE. Its unused `SaveBlock1.filler1[0x34]`, former extra-seen-flag padding,
is renamed `customRunConfig` only under PORT_BRIDGE. Search found no reader or
writer of this padding. Compile-time assertions require that reservation and
these exact native layouts; changing engine/save configuration must re-audit.

| Structure/field | Native size or offset |
| --- | ---: |
| SaveBlock1 | 15,536 bytes |
| SaveBlock2 | 3,884 bytes |
| SaveBlock3 | 1 byte |
| Run record in SaveBlock1 | offset `0x988`, size `0x34` (52) |
| Event flags in SaveBlock1 | offset `0x1270`, unchanged |
| Variables in SaveBlock1 | offset `0x139C`, unchanged |

No flag/variable is allocated. Existing expansion item Exp Share uses flag
`0x20`; Mega progression occupies `0x21–0x2B`; Kanto ferry uses `0x2C`.
These remain untouched. Ordinary variables are `0x4000–0x40FF` (temporaries
`0x4000–0x400F`), specials start at `0x8000`. `B_VAR_DIFFICULTY` remains 0;
the PORT_BRIDGE script setter is inert. Native trainer difficulty reads the validated save record, while new-game commit still runs after destructive initialization. Unused SaveBlock2 padding is not
extended or consumed, and no native save-sector checksum length changes.

## Wire format

Bytes are explicitly little-endian; no compiler struct layout is serialized.
CRC32 is the standard reflected polynomial `0xEDB88320`, initial/final XOR
`0xFFFFFFFF`, over bytes 0–47. The independent record CRC detects errors even
if a native sector checksum happens to match.

| Offset | Bytes | Meaning / current Stage D value |
| --- | ---: | --- |
| 0 | 4 | Magic `E3RC` (`0x43523345`) |
| 4 | 2 | Schema version 1 |
| 6 | 2 | Record length 52 |
| 8 | 4 | Unsigned seed, 0–4294967295 |
| 12 | 4 | Randomizer bits: starters 1, wild 2, trainers 4; Standard 0 |
| 16 | 4 | Difficulty bits: forced Set 1, no trainer bag healing/PP/revives 2, no trainer bag boosts 4, prepared bosses 8 |
| 20 | 4 | Content-rules ID `0x00030001` (C Normal: `0x00020001`; fixed B: `0x00010001`) |
| 24 | 4 | Independent run ID generated on setup entry |
| 28 | 4 | Trainer ID binding, read after new-save initialization |
| 32 | 2 | Algorithm 0 Standard; 1 seeded core Randomized |
| 34 | 2 | Generation bitmask bits 0–8; default `0x01FF`, nonempty |
| 36 | 1 | Mode 0 Standard; 1 Randomized core implemented |
| 37 | 1 | Difficulty 0 Normal; 1 Hard; 2 Custom |
| 38 | 1 | Cap policy 0 off; 1 hard; 2 soft (battle EXP only) |
| 39 | 1 | AI policy 0 native; 1 tactical without hidden-knowledge flags |
| 40 | 4 | Balance bits: no-legendaries 1, similar-BST 2; default 0 |
| 44 | 4 | Reserved, must be 0 |
| 48 | 4 | CRC32 |

Rules ID `0x00030001` identifies Stage D difficulty/template policy plus C's
unchanged indexed species pool and keyed randomizer algorithm. New D runs use
this ID; because content rules enter stream keys, seed 42 alone does **not**
reproduce C's starter/encounter mapping in a new D run. C Normal records retain
their recorded rules/key when decoded, so reads cannot silently reroll them.
No save namespace migration or cross-build campaign compatibility is promised.

Normal requires all difficulty fields zero. Hard requires cap 1, AI 1 and all
four supported difficulty bits (15). Custom accepts cap 0–2, AI 0–1 and any
subset of bits 1/2/4/8. Unknown fields or contradictory preset values fail
closed. Legacy B/C records permit only Normal with zero difficulty fields.
There is no EXP multiplier field activated in D; EV caps remain inherited/off.
Randomized still requires algorithm 1, a nonzero subset of starters/wild/trainers,
a nonempty generation mask and supported balance bits. Abilities (8), field
items (16), held items (32) and other unimplemented options remain rejected.
Standard still requires algorithm 0, no random/balance bits, all generations.

Schema remains 1 / 52 bytes, trainer binding and internal CRC unchanged, with
no new native save fields or checksum boundary. Existing C software rejects D
records because of their content ID, rather than silently ignoring Hard rules.
Critical settings remain in the same two-slot native save transaction; no
sidecar recovery procedure is needed. Cancellation/new-game/reset/Continue and
native checksum fallback are exercised against production code. Runtime D
storage is separate from C at `/3ds/emerald3ds-custom-stage-d/`.

## Lifecycle and failures

Setup edits only a RAM draft. A strict decimal seed editor accepts the full
u32 range, rejects overflow and discards an unaccepted edit on B. Automatic
seed generation occurs on setup entry or explicit regeneration, not redraw,
Continue, opening Run Settings or serialization. The setup adapter uses the
existing native RNG only to propose a seed/run ID; Stage C deterministic
species/party decisions use their own saved-seed algorithm, independent of that RNG.

Confirmation freezes the draft. After Birch/name selection, CB2_NewGame
requires that confirmed draft. NewGameInitData clears SaveBlock1/3, creates
the trainer ID and resets native systems; its final operation commits the
record to SaveBlock1 RAM and consumes the draft. Gameplay starts only if the
result decodes correctly. The ordinary first save persists it with progress.
No disk write occurs merely on confirmation, cancellation or new-game start.
The existing on-card save remains until the player explicitly saves the new
run. Continue never commits a draft or rerolls. Graphical settings never
modify the record. The in-game Run Settings page is read-only. Physical START opens it through
the production dual-screen start adapter; the classic menu also has a row.

Unknown schema/length/algorithm/reserved bytes, wrong content rules, unavailable
options, binding mismatch, invalid CRC or unusable native pool are rejected. Output rules and stored
bytes remain unchanged. Continue displays a reason and blocks before map/time
updates; ordinary/Hall-of-Fame/link save entry points return failure before
writing. Restore a complete backed-up save and matching clock files, or use
the matching supported build; do not zero the record, edit its CRC, silently
reseed or downgrade its rules. Back up the full application directory first.
There is no automatic migration of unknown versions.

An entirely zero or entirely erased (FF) reservation denotes an explicit legacy
fixed run: Standard/Normal, seed **not recorded**. It remains unchanged and
is never rewritten with an invented seed. This is safe for legacy fixed Stage A
saves, because no earlier randomized saves exist under this specification.
There is no automatic cross-namespace import or backwards-compatibility promise
for future randomized saves; new rules must preserve fail-closed behavior.

## Native transaction and recovery

Each 4096-byte sector holds 3968 progress bytes, 116 SaveBlock3 bytes and a
12-byte footer. SaveBlock2 is sector ID 0; SaveBlock1 IDs 1–4; PC storage IDs
5–13. The whole run record fits within SaveBlock1's first sector (ID 1).
The existing checksum folds a sum of u32 words into u16. The reservation is
inside that existing checksum range. Two rotating 14-sector slots hold complete
progress, signature, sector IDs and save counter. The existing loader selects
the newest valid complete slot and falls back to the older complete slot on
native-sector damage. We do not modify that transaction protocol.

ASan/UBSan tests execute the production codec/menu, native adapter, complete
NewGameInitData, serializer/checksum/slot loader and Continue/save guards with
synthetic buffers. They verify round trips, all single-bit record mutations,
version/rules/binding failures, legacy handling, cancellation, reset, unchanged
rejected data, and older-slot fallback. Native compilation asserts the actual
ARM structure sizes/offsets. Hardware SD/FAT power loss, boot/UI rendering and
restart recovery remain device tests; a host slot fixture does not establish
physical-media atomicity. Keep backups before testing and avoid intentional
power interruption until a dedicated recovery rehearsal is authorized.

## Post-C visual upgrade

The visual-fix branch retains schema 1, the same 52-byte native allocation,
algorithm 1/content rules `00020001` and the C runtime namespace. The complete
linked randomizer pool is compared with baseline C, not merely its counts.
No new flag, variable, setting, save field or import path is allocated. The
existing production save/guard/recovery fixtures are rerun. Updating the
embedded app/metadata after a complete directory backup is intended to continue
existing C saves without rerolling; physical-console update acceptance remains
pending. Original C package/source and Dropbox file are preserved for rollback.
