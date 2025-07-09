# Domain Configuration - coraai.tech

## Current Setup
- **Registrar:** Namecheap
- **Expiration:** Feb 1, 2027
- **DNS Provider:** Cloudflare (nameservers: ed.ns.cloudflare.com, surina.ns.cloudflare.com)
- **Domain Privacy:** Active until Feb 1, 2026
- **Cloudflare Plan:** Free

## Current DNS Records (NEEDS UPDATE)
- **A Record:** coraai.tech → 159.89.94.181 (OLD IP - needs change!)
- **CNAME:** www → coraai.tech (good)
- **MX Records:** Email forwarding configured
- **Proxy Status:** Enabled (orange cloud)

## Required Changes
1. **Update A record:**
   - Change from: 159.89.94.181
   - Change to: 159.203.183.48
   
### Steps in Cloudflare:
1. Go to DNS Records
2. Edit the A record for coraai.tech
3. Change IP to: 159.203.183.48
4. Keep proxy enabled (orange cloud)
5. Save

## Options:
1. **Use Cloudflare** (current) - Update DNS at Cloudflare dashboard
2. **Switch to Namecheap DNS** - Change nameservers back to Namecheap defaults
3. **Use DigitalOcean DNS** - Point nameservers to DigitalOcean

## Note
Personal contact info has been noted but not stored in files.