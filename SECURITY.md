# 🔒 Security Guide

## Overview

This project displays public transport information, but the configuration file contains **sensitive personal information** that reveals your home location. This guide explains security considerations and best practices.

## ⚠️ What's Sensitive?

### `config/config.json` - **CRITICAL**
This file reveals:
- **Your home address** (via station locations and walking times)
- **Your daily routine** (which stations you use)
- **When you're away** (if display is off/offline)

**NEVER:**
- ❌ Commit `config.json` to git
- ❌ Share it publicly
- ❌ Post screenshots containing station names
- ❌ Leave it world-readable on your Pi

## 🛡️ Security Measures Implemented

### 1. Git Protection

`.gitignore` excludes:
```
config/config.json
config/*.backup
config/*.bak
```

**Verify it's not tracked:**
```bash
git status config/config.json
# Should show: "Untracked" or nothing
```

### 2. File Permissions

The install script automatically sets:
```bash
chmod 600 config/config.json  # Only you can read/write
chmod 700 config/              # Only you can access directory
```

**Verify on Pi:**
```bash
ls -la config/config.json
# Should show: -rw------- (600)
```

### 3. Deploy Script Protection

`deploy_to_pi.sh` excludes `config.json` by default. You must configure it manually on the Pi.

### 4. Example Config Safety

`config.example.json` uses fake station IDs that won't reveal your location.

## 🔐 Best Practices

### On Development Machine (Mac/Linux)

1. **Never commit config.json:**
   ```bash
   # Before committing, verify:
   git status | grep config.json
   # Should show nothing or "Untracked"
   ```

2. **Secure local file:**
   ```bash
   chmod 600 config/config.json
   ```

3. **Use environment-specific configs:**
   ```bash
   # Keep separate configs
   config.json           # Your real config (gitignored)
   config.example.json   # Safe example (committed)
   ```

### On Raspberry Pi

1. **Secure file permissions after setup:**
   ```bash
   chmod 600 ~/bvg_abfahrt/config/config.json
   chmod 700 ~/bvg_abfahrt/config/
   ```

2. **Restrict SSH access:**
   ```bash
   # Disable password auth, use SSH keys only
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart ssh
   ```

3. **Enable firewall:**
   ```bash
   sudo apt-get install ufw
   sudo ufw allow 22/tcp  # SSH only
   sudo ufw enable
   ```

4. **Keep system updated:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

5. **Change default password:**
   ```bash
   passwd  # Change from default 'raspberry'
   ```

### Network Security

1. **Use WPA3 WiFi** if available
2. **Disable Pi's remote access** if not needed
3. **Consider VPN** for remote management from outside your network
4. **Don't expose Pi directly to internet** (no port forwarding)

## 🚨 What If Config.json Was Exposed?

If you accidentally committed or shared your config:

1. **Remove from git history immediately:**
   ```bash
   # Remove from history (destructive!)
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch config/config.json" \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push
   git push origin --force --all
   ```

2. **Change your routine temporarily** (use different stations)

3. **Update config with different stations** if you're concerned

4. **Be aware:** Someone could correlate station + walking time to narrow down your location to a few blocks

## 🔍 Additional Security Considerations

### API Keys (if added later)

If you add any API keys:
```bash
# Use environment variables
export BVG_API_KEY="your-key"

# Or .env file (add to .gitignore!)
echo "BVG_API_KEY=your-key" > .env
```

### Display Security

The display itself reveals:
- ✅ **Public info only** (departure times are public)
- ⚠️ **Station names visible** if someone sees your screen
- ⚠️ **Could reveal you're away** if display is off

**Mitigation:**
- Mount display where visitors can't easily see station names
- Consider generic title instead of station names
- Add "privacy mode" that hides station names

### Network Traffic

- ✅ API uses HTTPS (encrypted)
- ✅ No sensitive data sent to BVG API
- ⚠️ DNS queries reveal you're checking specific stations

**Low risk:** BVG API doesn't require authentication, queries are similar to millions of users.

### Log Files

Service logs contain station names:
```bash
# Logs are local only, but be aware when sharing
sudo journalctl -u bvg-display.service
```

**When seeking help:** Redact station names from logs before sharing.

## ✅ Security Checklist

### Initial Setup
- [ ] `config.json` is in `.gitignore`
- [ ] File permissions set to 600
- [ ] Config directory permissions set to 700
- [ ] Example config doesn't contain real data
- [ ] Changed default Pi password

### Before Sharing/Commits
- [ ] `git status` doesn't show `config.json`
- [ ] Screenshots don't reveal station names
- [ ] Logs are redacted if sharing
- [ ] No backup files committed (`.backup`, `.bak`)

### Raspberry Pi
- [ ] SSH key authentication enabled
- [ ] Password authentication disabled
- [ ] UFW firewall enabled
- [ ] System updated
- [ ] Config files secured (600/700)
- [ ] Pi not exposed to internet

### Regular Maintenance
- [ ] Update Pi monthly: `sudo apt-get update && sudo apt-get upgrade`
- [ ] Check git status before commits
- [ ] Review who has SSH access
- [ ] Verify file permissions haven't changed

## 🆘 Questions?

**Q: Is it safe to share my station IDs publicly?**  
A: Station IDs alone are public data, but combined with walking times, they reveal your approximate location. Avoid sharing both together.

**Q: Can someone track me through this display?**  
A: No. The display only receives public data, doesn't send your location anywhere.

**Q: Should I encrypt config.json?**  
A: File permissions (600) are sufficient for local security. Encryption adds complexity without much benefit for this use case.

**Q: What about the WiFi icon showing my connection status?**  
A: This only shows if the app has internet, not whether you're home. Low risk.

**Q: Is the BVG API call traceable to me?**  
A: Technically yes (via IP), but you're one of millions making similar queries. Very low risk.

## 📚 Additional Resources

- [Raspberry Pi Security](https://www.raspberrypi.org/documentation/configuration/security.md)
- [Git: Removing Sensitive Data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [SSH Key Authentication](https://www.ssh.com/academy/ssh/key)

---

**Remember:** Security is about layers. No single measure is perfect, but combined they provide strong protection for your personal information.

Stay safe! 🔒
