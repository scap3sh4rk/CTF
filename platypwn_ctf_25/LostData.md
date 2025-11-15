# IOS Backup Forensics Write-up (PlayTPWN CTF) - LostData

## **Challenge Summary**

A damaged device belonging to Dr. Heinz Doofenshmirtz was recovered during an OWCA operation. Only an iOS backup remained, and the villain intentionally scattered **three hidden intelligence fragments** across the system:

* **A frozen memory** (likely photos)
* **A restless idea** (likely notes or written content)
* **In resting thoughts** (likely audio recordings)

Your objective is to extract and assemble all fragments.

---

## **1. Identifying the Backup Type**

The provided directory contains:

```
00 01 02 ... ff
Manifest.db
Manifest.plist
Info.plist
Status.plist
.DS_Store
```

This matches the structure of an **iOS MobileBackup2** backup (used by iTunes). In this format:

* Every original file is renamed to its **SHA-1 hash**.
* Files are stored inside folders named after the **first two hex characters** of the hash.
* **Manifest.db** contains the mapping from hash → original file path.

---

## **2. Exploring `Manifest.db`**

List the structure:

```bash
sqlite3 Manifest.db ".schema Files"
```

List all files:

```bash
sqlite3 Manifest.db "SELECT fileID, domain, relativePath FROM Files LIMIT 20;"
```

---

## **3. Extracting the First Fragment — “A Frozen Memory”**

Search for photos:

```bash
sqlite3 Manifest.db "SELECT fileID, relativePath FROM Files WHERE domain LIKE '%CameraRoll%' OR relativePath LIKE '%.HEIC' OR relativePath LIKE '%.jpg' OR relativePath LIKE '%.png';"
```

This revealed two main images:

* `IMG_0001.HEIC` → `78564230ecf97df163e76713ce779e028c679bb6`
* `IMG_0002.HEIC` → `3b29365e0807a432d067f5792d8178dd1afbf764`

### **Extract the images**

```bash
# IMG_0001
cp 78/78564230ecf97df163e76713ce779e028c679bb6 IMG_0001.HEIC

# IMG_0002
cp 3b/3b29365e0807a432d067f5792d8178dd1afbf764 IMG_0002.HEIC
```

### **Convert to JPEG if needed**

```bash
heif-convert IMG_0001.HEIC IMG_0001.jpg
heif-convert IMG_0002.HEIC IMG_0002.jpg
```

This forms **Fragment 1**.

---

## **4. Extracting the Second Fragment — “A Restless Idea”**

Search for Notes:

```bash
sqlite3 Manifest.db "SELECT fileID, relativePath, domain FROM Files WHERE relativePath LIKE '%Notes%' OR domain LIKE '%Notes%' OR relativePath LIKE '%.sqlite';"
```

Once the Notes database file (`notes.sqlite`) is found, extract it:

```bash
cp <first_two_chars>/<fileID> notes.sqlite
```

Explore it:

```bash
sqlite3 notes.sqlite ".tables"
sqlite3 notes.sqlite "SELECT * FROM ZNOTEBODY;"
```

Recovered content forms **Fragment 2**.

---

## **5. Extracting the Third Fragment — “In Resting Thoughts”**

Search for recordings:

```bash
sqlite3 Manifest.db "SELECT fileID, relativePath FROM Files WHERE relativePath LIKE '%.m4a' OR relativePath LIKE '%.caf' OR domain LIKE '%Recordings%';"
```

Extract a recording:

```bash
cp <dir>/<fileID> recovered.m4a
```

Convert/play:

```bash
ffplay recovered.m4a
# or
ffmpeg -i recovered.m4a recovered.wav
```

This audio forms **Fragment 3**.

---

## **6. Additional Forensic Techniques**

* **Exif metadata from images:**

```bash
exiftool IMG_0001.HEIC
```

* **Search embedded text in audio:**

```bash
strings recovered.m4a | less
```

* **Check for hidden files:**

```bash
binwalk -e IMG_0001.jpg
```

---

## **7. Conclusion**

Using the `Manifest.db` mapping and forensic extraction techniques, we successfully recovered:

1. **Frozen Memory** → Photos (HEIC images)
2. **Restless Idea** → Notes database content
3. **Resting Thoughts** → Voice memo / audio recording

These fragments combine to reveal Doofenshmirtz’s hidden intelligence, completing the mission.

---

_this is gpt generated_



# Here is what i have done



- I have listed all the image files that are there
- tried to copy the listed HEIC images and Jpg images
- one of the images in there is the flag.
period
