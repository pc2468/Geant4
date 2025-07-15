# Geant4 Manual Dataset Fix

Sometimes Geant4 loves to ruin your day by failing to download its datasets during `make -j12`.  
Here’s how to outsmart it by doing the work manually — old-school style.

---

## Manual Fix Steps

**1️⃣ Download the datasets manually**  
- Find every required dataset file (.tar.gz).  
- Put them all in a folder — call it `datasets` or `manual_fix`.

**2️⃣ Extract but don’t delete**  
- Extract all `.tar.gz` files in that folder.  
- **Keep** the original `.tar.gz` files — you’ll need them again.

**3️⃣ Place extracted folders in the build data directory**  
- Go to `geant4-v[version]-build/data/`  
- Copy all the extracted dataset folders here.

**4️⃣ Tweak the externals**  
- Move up one level to `geant4-v[version]-build/`  
- Go into the `externals` folder.  
- Each dataset has its own folder — go inside each one, then into its `src` subfolder.

**5️⃣ Replace the broken tarballs**  
- Inside each `src` folder, you’ll see a `.tar.gz` file that failed to download.  
- **Replace** it with the correct `.tar.gz` file from your manual stash.  
- Names must match exactly — Geant4 checks hashes, not vibes.

---

## Done!

If you did all this, Geant4 should stop complaining, and your build should finish without dataset drama.

Happy simulating!
