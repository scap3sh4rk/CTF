# ACME Surveys CTF Writeup

## Overview

This challenge involved identifying the hidden admin user of the **ACME Surveys** platform and extracting the final flag. The backend logic relied on an HMAC comparison using a secret token, and the challenge included deliberate misdirection such as password hashes and disabled admin roles. The correct path was to enumerate user emails using a provided breach‑checking API and identify the one treated differently.

---

## Provided Artifacts

The challenge shipped with:

* A Flask application
* A Docker environment
* A `/check_email` endpoint hosted externally (`HaveIBeenChowned`)
* A large `runtime_db.csv` containing email → MD5(password)
* Environment secrets (we recovered):

  * `FLAG_SECRET`
  * `ADMIN_API_KEY`
* The knowledge that the real flag is only shown when:

```
HMAC_SHA256(FLAG_SECRET, email) == FLAG_TOKEN
```

The admin role is **not stored**—it is derived cryptographically.

---

## Understanding the Backend Logic

Inside the Flask app, the flag revelation logic in `welcome()` looked like this:

```python
mytoken = token_for_email(email)
if hmac.compare_digest(mytoken, FLAG_TOKEN):
    matched = True

if matched:
    flag_value = f"trustctf{{{token_for_email(email)[:12]}}}"
```

This means:

* The correct admin email is the one whose HMAC matches the hidden `FLAG_TOKEN`.
* Passwords and roles do **not** matter.
* To solve: **find the email whose HMAC matches the server’s stored token**.

But since we did **not** have `FLAG_TOKEN`, we needed another leak.

---

## Using the External Leak API (`/check_email`)

The challenge provided this special endpoint:

```
https://tlctf2025-hibc.chals.io/check_email?email=<email>
```

Most emails return:

```json
{
  "email": "...",
  "plaintext_password": null,
  "pwned": false
}
```

We brute‑forced **every email in the CSV** and looked for deviations. Any abnormal response signifies the admin.

### Automation Script

```python
import csv, requests

URL = "https://tlctf2025-hibc.chals.io/check_email"

with open("runtime_db.csv") as f:
    r = csv.DictReader(f)
    for row in r:
        email = row["email"]
        resp = requests.get(URL, params={"email": email})
        data = resp.json()

        if data.get("pwned") or data.get("plaintext_password") or data != {
            "email": email,
            "plaintext_password": None,
            "pwned": False
        }:
            print("ADMIN FOUND:", email)
            print(data)
            break
```

### Result

```
ADMIN FOUND: blake.baker20@acme.test
{"email": "blake.baker20@acme.test", "plaintext_password": null, "pwned": true}
```

This is the **only email with `pwned = true`**, revealing the admin.

---

## Computing the Flag via HMAC

We were already given:

```
FLAG_SECRET = 3HZ0jv5EuC4WHoJnxGKDxuoD9mCkxHMlJz3MucS6U40k7lLdqDqlF2pmeDRT2W5F
```

The flag format follows:

```
trustctf{ first12chars( HMAC_SHA256(FLAG_SECRET, admin_email) ) }
```

### HMAC Calculation Script

```python
import hmac,hashlib
SECRET = "3HZ0jv5EuC4WHoJnxGKDxuoD9mCkxHMlJz3MucS6U40k7lLdqDqlF2pmeDRT2W5F"
email  = "blake.baker20@acme.test"

token  = hmac.new(SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()
print("ADMIN EMAIL:", email)
print("HMAC:", token)
print("FLAG: trustctf{" + token[:12] + "}")
```

Running this yields the correct CTF flag.

---

## Why This Works

* The admin is chosen strictly through HMAC comparison.
* Passwords are irrelevant.
* Roles in `users_meta` are intentionally misleading.
* The breach API leaks which user is special.
* Once the admin email is identified, computing the correct flag is trivial.

This challenge blends web exploitation, cryptographic reasoning, and API enumeration.

---

## Final Outcome

* **Admin:** `blake.baker20@acme.test`
* **Flag:** Derived via HMAC using the provided secret

The entire challenge is solvable without cracking hashes or performing SQL injection—just clever enumeration and understanding backend crypto logic.

---

## Ready for the Next Challenge

This approach can be adapted to similar HMAC‑based identity or privilege escalations. Whenever you're ready, we can tear into the next CTF task.
