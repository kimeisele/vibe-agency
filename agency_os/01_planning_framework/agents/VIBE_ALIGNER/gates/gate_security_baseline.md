# Validation Gate: Security Baseline

## Rule
Project plan must include basic security measures - no obvious security gaps that would put user data at risk.

---

## Minimum Security Requirements

### 1. Authentication & Authorization
- ✅ Passwords hashed (bcrypt, argon2, scrypt) - NEVER plaintext
- ✅ HTTPS enforced (no HTTP in production)
- ✅ Session management secure (HttpOnly cookies, JWT with expiry)
- ✅ Password reset flow secure (token-based, time-limited)
- ❌ No authentication for sensitive data
- ❌ Storing passwords in plaintext or MD5/SHA1 (insecure)
- ❌ No session expiry (sessions never expire)

### 2. Data Protection
- ✅ Sensitive data encrypted at rest (if applicable: SSN, credit cards, health data)
- ✅ Database not publicly accessible (firewall rules)
- ✅ Environment variables for secrets (not hardcoded)
- ✅ No API keys in git repo
- ❌ Database exposed to public internet (0.0.0.0 access)
- ❌ API keys committed to git
- ❌ Sensitive data in logs or error messages

### 3. Input Validation
- ✅ All user inputs validated and sanitized
- ✅ SQL injection prevention (use parameterized queries/ORM)
- ✅ XSS prevention (escape HTML, use Content Security Policy)
- ✅ CSRF protection (for state-changing requests)
- ❌ Raw SQL with string concatenation (SQL injection risk)
- ❌ innerHTML with user input (XSS risk)
- ❌ No rate limiting (brute force attacks)

### 4. API Security
- ✅ API authentication (JWT, API keys, OAuth)
- ✅ Rate limiting (prevent abuse)
- ✅ CORS configured (not open to all origins)
- ❌ No API authentication (anyone can call API)
- ❌ No rate limiting (DDoS risk)
- ❌ CORS = * in production (security risk)

### 5. Dependencies Security
- ✅ Regular dependency updates (npm audit, safety)
- ✅ No known critical CVEs in dependencies
- ❌ Using dependencies with known critical vulnerabilities
- ❌ No plan to update dependencies (security rot)

### 6. Compliance (if applicable)
- ✅ GDPR compliance (for EU users): data deletion, consent, privacy policy
- ✅ PCI-DSS compliance (if storing credit cards - use Stripe instead!)
- ✅ HIPAA compliance (if health data - requires special hosting)
- ❌ Collecting EU user data without GDPR compliance
- ❌ Storing credit card numbers (use Stripe/payment gateway!)

---

## Critical Security Checks

### 🔴 Critical (Must Fix - Blocks Launch)

1. **Plaintext Passwords**
   - Never store passwords in plaintext
   - Use bcrypt (>10 rounds), argon2, or scrypt
   - Action: Add password hashing

2. **Public Database Access**
   - Database should NOT be accessible from public internet
   - Use firewall rules, private networks
   - Action: Configure firewall, restrict access

3. **No HTTPS**
   - All production traffic must use HTTPS
   - HTTP exposes sensitive data (passwords, tokens)
   - Action: Enable HTTPS (Vercel/Netlify do this automatically)

4. **API Keys in Code**
   - Never commit API keys, secrets to git
   - Use environment variables (.env files)
   - Action: Remove from git, use .env

5. **SQL Injection Vulnerability**
   - Never concatenate user input into SQL queries
   - Use parameterized queries (Prisma, Django ORM do this)
   - Action: Use ORM or prepared statements

6. **Storing Credit Card Data**
   - NEVER store credit card numbers yourself (PCI-DSS nightmare)
   - Use Stripe, PayPal, etc. (they handle storage)
   - Action: Remove card storage, use payment gateway

### 🟡 High Priority (Should Fix Before Launch)

1. **No Rate Limiting**
   - APIs should limit requests (e.g., 100/hour per user)
   - Prevents brute force, DDoS
   - Action: Add rate limiting (express-rate-limit, Django Ratelimit)

2. **CORS Open to All**
   - CORS = * allows any website to call your API
   - Restrict to your frontend domain
   - Action: Configure CORS properly

3. **No Input Validation**
   - Validate all user inputs (type, length, format)
   - Prevents injection attacks, crashes
   - Action: Add validation (Zod, Joi, class-validator)

4. **No CSRF Protection**
   - State-changing requests need CSRF tokens
   - Prevents cross-site request forgery
   - Action: Enable CSRF protection (Next.js/Django do this)

5. **Sensitive Data in Logs**
   - Don't log passwords, tokens, credit cards
   - Logs often stored insecurely or synced to third parties
   - Action: Filter sensitive data from logs

### 🟢 Medium Priority (Good Practice)

1. **No Security Headers**
   - Add Content-Security-Policy, X-Frame-Options, etc.
   - Prevents XSS, clickjacking
   - Action: Add security headers (helmet.js, Django middleware)

2. **No Dependency Scanning**
   - Run `npm audit` or `safety` regularly
   - Fix critical vulnerabilities
   - Action: Add CI step for security scans

3. **Weak Password Policy**
   - Require 8+ characters, no common passwords
   - Action: Add password strength validation

4. **No Account Lockout**
   - Lock accounts after N failed login attempts
   - Prevents brute force
   - Action: Add lockout logic (5 attempts = 15min lockout)

---

## OWASP Top 10 Checklist

Reference: https://owasp.org/www-project-top-ten/

1. ✅ Broken Access Control - Users can only access their own data
2. ✅ Cryptographic Failures - Sensitive data encrypted, HTTPS enforced
3. ✅ Injection - SQL/NoSQL injection prevented (use ORM)
4. ✅ Insecure Design - Secure-by-default architecture
5. ✅ Security Misconfiguration - Production configs secure (debug=False)
6. ✅ Vulnerable and Outdated Components - Dependencies up-to-date
7. ✅ Identification and Authentication Failures - Strong auth, no weak passwords
8. ✅ Software and Data Integrity Failures - Verify external code, no unsigned updates
9. ✅ Security Logging and Monitoring Failures - Log security events, monitor for attacks
10. ✅ Server-Side Request Forgery (SSRF) - Validate/sanitize URLs user can trigger

---

## Validation Process

1. Check authentication method (is it secure?)
2. Check password storage (hashed or plaintext?)
3. Check database access (publicly accessible?)
4. Check API security (authenticated? rate-limited?)
5. Check for known security antipatterns (SQL injection, XSS)
6. Check dependencies for known CVEs
7. Check HTTPS enforced in production

---

## Pass Criteria

- ✅ All Critical security issues resolved
- ✅ HTTPS enforced in production
- ✅ Passwords properly hashed
- ✅ Database not publicly accessible
- ✅ API has authentication + rate limiting
- ✅ No hardcoded secrets in code
- ✅ Input validation present
- ✅ No storing of credit cards (using payment gateway)

---

## Failure Conditions

- ❌ Plaintext password storage (CRITICAL)
- ❌ No HTTPS in production (CRITICAL)
- ❌ Database exposed to public internet (CRITICAL)
- ❌ SQL injection vulnerability (CRITICAL)
- ❌ Storing credit card numbers (CRITICAL - PCI-DSS violation)
- ❌ API keys committed to git (HIGH)
- ❌ No API authentication (HIGH)

---

## Error Message Template

```
GATE FAILED: Security Baseline Not Met

Critical security issues detected: {count}

Issues:
{list_of_issues}

Impact: {impact_description}

Why this is a problem:
{explanation}

Required fixes:
1. {fix_1}
2. {fix_2}
3. {fix_3}

Resources:
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Security checklist: {relevant_link}

Action: Address all critical security issues before proceeding
```

**Example:**
```
GATE FAILED: Security Baseline Not Met

Critical security issues detected: 3

Issues:
1. ❌ Passwords stored in plaintext (CRITICAL)
2. ❌ No HTTPS in production (CRITICAL)
3. 🟡 No rate limiting on API (HIGH)

Impact:
- User passwords exposed if database breached
- All traffic (passwords, tokens) visible over network
- API vulnerable to brute force attacks

Why this is a problem:
Plaintext passwords are the #1 security vulnerability.
If your database is breached, all user passwords are immediately compromised.
Attackers can then try these passwords on other services (credential stuffing).

No HTTPS means all traffic is unencrypted. Passwords, session tokens,
and sensitive data can be intercepted by anyone on the network (WiFi, ISP).

No rate limiting allows attackers to brute force passwords, spam APIs,
or DDoS your service with unlimited requests.

Required fixes:
1. Add password hashing:
   - Install: bcrypt (npm install bcrypt)
   - Hash on registration: bcrypt.hash(password, 10)
   - Verify on login: bcrypt.compare(password, hash)

2. Enable HTTPS:
   - If using Vercel/Netlify: Automatic ✅
   - If using Railway/Fly.io: Automatic ✅
   - If using custom server: Use Let's Encrypt SSL certificate

3. Add rate limiting:
   - Install: express-rate-limit
   - Limit: 100 requests/hour per IP
   - Apply to: Login, API endpoints

Resources:
- Password hashing: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- HTTPS guide: https://letsencrypt.org/getting-started/
- Rate limiting: https://www.npmjs.com/package/express-rate-limit

Action: Address all critical security issues before proceeding
```

---

## Purpose

Prevents launching insecure applications that put user data at risk. Ensures basic security hygiene.

---

## Exemptions

- Prototype/demo (not handling real user data) - security can be basic
- User explicitly acknowledges risks (documents security debt)
- Internal tool (not public-facing, trusted users only)

---

## Security Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheets: https://cheatsheetseries.owasp.org/
- Mozilla Web Security: https://infosec.mozilla.org/guidelines/web_security
- Security Headers: https://securityheaders.com/
- npm audit: https://docs.npmjs.com/cli/v8/commands/npm-audit
