# Run configuration save format (Stages B/C)

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
NewGameInitData still selects native Normal. Unused SaveBlock2 padding is not
extended or consumed, and no native save-sector checksum length changes.

## Wire format

Bytes are explicitly little-endian; no compiler struct layout is serialized.
CRC32 is the standard reflected polynomial `0xEDB88320`, initial/final XOR
`0xFFFFFFFF`, over bytes 0–47. The independent record CRC detects errors even
if a native sector checksum happens to match.

| Offset | Bytes | Meaning / current Stage C value |
| --- | ---: | --- |
| 0 | 4 | Magic `E3RC` (`0x43523345`) |
| 4 | 2 | Schema version 1 |
| 6 | 2 | Record length 52 |
| 8 | 4 | Unsigned seed, 0–4294967295 |
| 12 | 4 | Randomizer bits: starters 1, wild 2, trainers 4; Standard 0 |
| 16 | 4 | Difficulty option bits; all 0 |
| 20 | 4 | Content-rules ID `0x00020001` (legacy fixed B: `0x00010001`) |
| 24 | 4 | Independent run ID generated on setup entry |
| 28 | 4 | Trainer ID binding, read after new-save initialization |
| 32 | 2 | Algorithm 0 Standard; 1 seeded core Randomized |
| 34 | 2 | Generation bitmask bits 0–8; default `0x01FF`, nonempty |
| 36 | 1 | Mode 0 Standard; 1 Randomized core implemented |
| 37 | 1 | Difficulty 0 Normal; 1 Hard / 2 Custom reserved/unavailable |
| 38 | 1 | Cap policy 0: inherited native behavior |
| 39 | 1 | AI policy 0: inherited native behavior |
| 40 | 4 | Balance bits: no-legendaries 1, similar-BST 2; default 0 |
| 44 | 4 | Reserved, must be 0 |
| 48 | 4 | CRC32 |

Rules ID `0x00020001` identifies Stage C's indexed safe species pool, keyed
algorithm and exclusions documented in RULES.md. Randomized requires algorithm
1, a nonzero subset of core option bits 1/2/4, a nonempty nine-generation mask,
and only supported balance bits 1/2. Abilities (8), field items (16), held items
(32), Hard/Custom, difficulty options, cap/AI policies and unknown bits are rejected.
Standard uses algorithm 0, no random/balance bits and all generations; it accepts
both current content rules and fixed-only Stage B rules `0x00010001`. A rules
identifier is not a general content migration mechanism. There is no automatic
import from B's SD directory and no promise that B can load C records.

Schema 1/length 52 and the exact allocation/checksum remain unchanged in C.
Native startup/Continue/save validation also checks the actual eligible pool
(`CR_POOL`: NO VALID SPECIES POOL), including three distinct level-5 starters
when starters or trainers are enabled (rival continuity), and a viable level-1 pool. Rejection preserves bytes and output
configuration. Never reinterpret an unsupported randomized record as Standard.
No event flags or variables were added. `VAR_STARTER_MON` continues its native
chosen-index role for the rival, rather than storing new run settings.

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
