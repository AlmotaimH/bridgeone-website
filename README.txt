BRIDGEONE WEBSITE — HOW TO LAUNCH
==================================

What's in this folder
- index.html     Home page (English / French / Arabic switch)
- insights.html  Blog / Insights page with topic filter
- article.html   First article: "5 signs your business is ready to expand"
- privacy.html   Privacy policy (template — have it reviewed)
- styles.css     All design and animations
- main.js        Animations, menu, forms, language switch
- i18n.js        All translated text (edit wording here)
- assets/        Logo, favicon, social share image

1) BEFORE LAUNCH — fill in your details
- Phone number added: +1 (647) 335-5647
- i18n.js: "[City]" / "[City, Province]", client stories, testimonials
  (only publish REAL client quotes, with their permission)
- index.html: replace https://calendly.com/ with your own booking link
- Confirm info@bridge-one.ca is the right email (index.html, main.js, privacy.html)

2) MAKE THE CONTACT FORM DELIVER TO YOUR INBOX (free)
- Create a free account at formspree.io, make a new form, copy its URL
- In main.js, replace https://formspree.io/f/YOUR_FORM_ID with that URL
- Until then, the form opens the visitor's email app addressed to you

3) PUT IT ONLINE (pick one)
A. Netlify (free, easiest)
   - Go to app.netlify.com/drop and drag this whole folder in
   - Site settings > Domain management > add bridge-one.ca
   - Netlify shows DNS records; add them in GoDaddy > My Products > DNS
   - HTTPS is switched on automatically
B. GoDaddy Web Hosting (cPanel) — not the Website Builder
   - Upload everything to the public_html folder with File Manager
   Note: GoDaddy's Website Builder / Airo cannot run custom code like this.

4) AFTER LAUNCH
- Add the site to Google Search Console and Google Analytics
- Create a Google Business Profile and LinkedIn company page; link them
- Publish one new article a month (copy article.html as the template)
