# Single‑Repo Push Access via Deploy Key (SSH) — No Global SSH Config

This guide lets **one remote PC** push to **one public GitHub repo** with **least privilege**, without editing `~/.ssh/config`.  
You’ll generate the key on a **trusted Linux machine**, add the public key as a **Deploy key (write)** in GitHub there, and then move only the **private key** to the remote PC. The repo will use:
```
git config core.sshCommand "ssh -i ~/.ssh/<repo>-deploy"
```

> Replace `<owner>` and `<repo>` with your repository coordinates.

---

## Need
- Allow exactly one remote computer to **push** to a specific **public GitHub repository**.
- The credential must **not** grant permissions on any other repo or the organization.

---

## Procedure

### 1) On the **trusted Linux machine** — create a dedicated SSH key pair
```bash
ssh-keygen -t ed25519 -C "deploy-key for <owner>/<repo>" -f ~/.ssh/<repo>-deploy
# Produces:
#   ~/.ssh/<repo>-deploy      (private key)
#   ~/.ssh/<repo>-deploy.pub  (public key)
```

### 2) On **GitHub** (still on the trusted machine) — add the **public key** as a Deploy key
- Go to: **Repository → Settings → Deploy keys → Add deploy key**
- Title: `deploy key for <owner>/<repo>`
- Paste the contents of `~/.ssh/<repo>-deploy.pub`
- Check **Allow write access** → **Add key**

### 3) Move **only the private key** to the **remote PC**
Use a disk‑on‑key (USB). Since FAT filesystems don’t preserve permissions:
- On the **remote PC**:
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
mv /media/<USB>/<repo>-deploy ~/.ssh/<repo>-deploy
chmod 600 ~/.ssh/<repo>-deploy
# (Do NOT copy the .pub file to the remote PC; it isn't required.)
```

### 4) In the local clone on the **remote PC** — set remote + per‑repo SSH command
Inside the repo directory:
```bash
git remote set-url origin git@github.com:<owner>/<repo>.git

# Force this repo to use the dedicated key, without editing ~/.ssh/config
git config core.sshCommand "ssh -i ~/.ssh/<repo>-deploy -o IdentitiesOnly=yes"
```
> `IdentitiesOnly=yes` ensures SSH won’t try other keys that might cause auth failures.

### 5) (Optional) Prime known_hosts for GitHub on the remote PC
```bash
ssh -T git@github.com -o IdentitiesOnly=yes -i ~/.ssh/<repo>-deploy || true
# Accept GitHub's host key fingerprint when prompted
```

### 6) Push test
```bash
git push
```
If the deploy key was added with **Allow write access**, the push should succeed.

---

## Notes, Rotation & Revocation
- **Scope**: Deploy keys are **scoped to a single repository**. They do not grant org‑wide or cross‑repo access.
- **Revoke**: Remove the key at **Repository → Settings → Deploy keys**.
- **Rotate**: Repeat steps 1–3 with a new pair; add the new public key, remove the old one.
- **Backups**: Avoid copying the private key elsewhere; if lost, generate a new pair.

---

## Troubleshooting
- `Permission denied (publickey)` → Verify:
  - `git config core.sshCommand` is set in **this repo** and points to `~/.ssh/<repo>-deploy`.
  - File perms: `chmod 700 ~/.ssh` and `chmod 600 ~/.ssh/<repo>-deploy`.
  - The public key was added as a **Deploy key with write access**.
- Host key prompt every time → Ensure `~/.ssh` is `700` and that you completed step 5 once.
- Multiple keys interfering → Keep `-o IdentitiesOnly=yes` in `core.sshCommand`.

---

## Security Defaults Used Here
- **ed25519** key type (modern, short, secure).
- **Per‑repo** SSH command ensures the key is used **only** for this repository.
- No global SSH config changes; no PATs; no extra permissions.

## Credit

This guide was written by ChatGPT-5. 

I (the human) specified the requirments and did some light editing
