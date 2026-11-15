# Stage F private test package

This is a new, isolated Hoenn campaign test build for Derek's original 3DS XL.
It includes Emerald 3DS v0.5.0, the Gen 1–9 expansion, Stage D difficulty,
Stage E optional rules, and the fixed roster in STAGE_F_CAMPAIGN.md.
Physical-console boot/performance, Champion and postgame results are pending.
Keep the Stage E ZIP and its existing installation unchanged.

## First installation on your laptop

1. Back up the SD card's existing Emerald folders to the laptop.
2. Extract `Emerald3DS-Custom-StageF-private.zip` on the laptop.
3. Copy its `3ds` folder to the SD root. This adds only
   `3ds/emerald3ds-custom-stage-f-v050/`. Do not copy old saves, settings,
   clock/tracker files, ROMs or firmware into F. The matching pack is included.
4. Eject the SD card, return it to the console, open Homebrew Launcher and
   launch **Emerald 3DS Custom Stage F v0.5.0**. Use your existing DSP setup.
5. For the first run leave species/ability/item randomizers OFF and choose
   Normal difficulty. Route 101 now has wild Lechonk (#915), a Gen 9 Pokémon,
   at level 3 (10% land slot). Catch it and check summary/follower/PC/save/restart.
6. Follow the Stage F section of DEVICE_TESTS.md and report failures with the
   model, map, toggles, source receipt, logs and expected/observed behavior.

The app is an engine-only `.3dsx` paired with `emerald3ds.pak`; keep these two
files and `CUSTOM_INSTALL.json` together. An unrelated official/upstream pack
does not match this custom engine. The original public web builder is not this
custom data-build workflow. No CIA/forwarder is included.

## Checked installation and future F updates

The extracted ZIP also contains a portable installer using Python 3.11+ and
only the standard library. It has no compiler or Pillow dependency. From the
extracted folder, open a terminal and first verify without changing the card:

```sh
python3 installer/install_custom.py --verify
```

On Windows use `py -3` in place of `python3`. The implementation and fault
fixtures run on Linux; Windows/macOS commands and real SD-driver behavior
still require laptop/device verification. Install/update by selecting the
actual SD root (replace the example path with yours):

```sh
python3 installer/install_custom.py --sd /Volumes/SDCARD
```

Windows example: `py -3 installer/install_custom.py --sd E:/`.
The installer checks the file hashes, actual executable RomFS ABI, pack ABI,
ROM-profile identifier and every pack payload CRC before installing. It refuses
old-stage folders, mismatched rules and loose development-data overrides.

For an existing compatible F installation it stages a copy of the complete
folder, including the save, global `settings.txt` (the seed and randomizer
switches), clock, Nuzlocke state, logs and existing backups. It retains the
entire old folder at `3ds/.emerald3ds-custom-stage-f-v050.backup-<token>/`.
The terminal prints that exact backup path. This backup is hidden; show hidden
files on the laptop or open the printed path. Do not delete the backup until the
updated game has loaded, saved and restarted correctly. The installer never
converts an E save or changes the game's difficulty-record layout.

Do not manually overwrite an existing F installation for an update: the
checked installer provides the backup and engine/data pairing guarantees.
Do not run the installer and recovery concurrently, or use the card in the
console while it is mounted for installation.

## Interrupted update or rollback

If the card disconnects, the installer reports an error, or installation is
interrupted, reconnect it and run this **before launching the game**:

```sh
python3 installer/install_custom.py --recover --sd /Volumes/SDCARD
```

Recovery uses the persistent transaction journal to restore the complete old
folder after either directory-rename boundary; a failed first install is removed.
Then retry the verified installation. If the journal is damaged or the backup
is missing, recovery stops and preserves the files for inspection; keep the card
and report the error. Host fault injection covers these boundaries; actual FAT
power loss and physical SD behavior still need console/laptop rehearsal.

For rollback after a successful update: back up the current F folder to the
laptop first, then move it out of `3ds/` and restore the complete printed backup
folder under `3ds/emerald3ds-custom-stage-f-v050/`. Restore progress, settings,
clock and tracker together. Do not combine an old executable with the new pack
or restore only the save. This returns to the backup's progress.

## Building matching data privately from source

The reproducible developer pipeline is `tools/stage_f.sh build|test|fresh|package`
inside the frozen SDK/Python image described in BUILD.md. `custom_payload.py
recipe` records a hash-only manifest of locally generated pinned-source data,
then `build` reconstructs the pack from those exact files and pairs it with the
corresponding engine. It downloads no ROM/save/firmware and contains no literal
asset pool. Output packs/test ZIPs stay under ignored `work/`.

This validates a **local source-build recipe**, not a retail-ROM-only recipe.
Gen 4–9 expansion art/content is not present in the supported clean Emerald ROM.
A public end-user package reconstructed solely from that ROM remains blocked
on a separate attributed/validated expanded-asset supply and extraction recipe.
Do not relax the upstream literal-content audit or publish this private pack/ZIP.
