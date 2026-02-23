# Author Bio Block — Brian McGauley / Imaginarii

## Canonical Bio Text (Short — for blog posts)

> **Brian McGauley** is the founder of [Imaginarii](https://imagi-narii.com) and an AI consultant, web developer, and MBA candidate at Fresno State. A summa cum laude graduate with 20+ years of web development experience, he holds memberships in Phi Kappa Phi (ΦΚΦ) and Beta Gamma Sigma (ΒΓΣ) and specializes in AI implementation, automation, and creative-technical strategy. He's based in Fresno, CA, where he also produces electronic music under his own name.
> [Full bio →](https://brianmcgauley.com) | [Work with Brian →](https://imagi-narii.com/consulting)

---

## Squarespace HTML Block — Copy/Paste Ready

Add this as a **Code Block** (Insert > Code) at the bottom of every blog post in Squarespace, just above the footer/copyright area:

```html
<div style="border-top: 2px solid #e0e0e0; margin-top: 48px; padding-top: 32px; display: flex; gap: 20px; align-items: flex-start; font-family: inherit;">
  <img 
    src="https://images.squarespace-cdn.com/content/v1/6980073277241e21742b84fd/27cda427-01d1-4bd8-bf80-76795c811c29/1756833165579.png" 
    alt="Brian McGauley"
    style="width: 72px; height: 72px; border-radius: 50%; object-fit: cover; flex-shrink: 0;"
  />
  <div>
    <p style="margin: 0 0 4px 0; font-weight: 700; font-size: 1rem;">Brian McGauley</p>
    <p style="margin: 0 0 10px 0; font-size: 0.85rem; color: #666;">Founder, Imaginarii · AI Consultant · MBA Candidate, Fresno State</p>
    <p style="margin: 0 0 12px 0; font-size: 0.9rem; line-height: 1.6; color: #333;">
      Summa cum laude graduate (Business Admin / CIS), Phi Kappa Phi (ΦΚΦ), Beta Gamma Sigma (ΒΓΣ). 20+ years building for the web. Specializes in AI implementation, workflow automation, and business strategy for companies ready to actually use AI — not just talk about it. Based in Fresno, CA.
    </p>
    <p style="margin: 0; font-size: 0.85rem;">
      <a href="https://brianmcgauley.com" style="color: inherit; margin-right: 16px;">Full Bio →</a>
      <a href="https://imagi-narii.com/consulting" style="color: inherit; margin-right: 16px;">Work With Brian →</a>
      <a href="https://imagi-narii.com/blog" style="color: inherit;">More Posts →</a>
    </p>
  </div>
</div>
```

---

## Squarespace Placement Instructions

### Option A: Add to Every Post Manually (Recommended for now)

1. Open the blog post in Squarespace editor
2. Scroll to the very bottom of the post content
3. Click the **+** button to add a new content block
4. Select **Code** from the block types
5. Paste the HTML above
6. Click **Apply**
7. The bio will render below your post content, above comments/footer

**Note:** Make sure the image URL above is still valid. If the founder photo changes, update `src=` in the HTML.

### Option B: Squarespace Blog Post Footer Injection (Advanced — CSS/JS Injection)

If you want the bio to appear automatically on ALL blog posts without manually adding it:

1. Go to **Settings → Advanced → Code Injection**
2. In the **Footer** field, add:

```html
<script>
// Auto-inject author bio on all blog posts
document.addEventListener('DOMContentLoaded', function() {
  // Only run on blog post pages (Squarespace adds .BlogItem class to post pages)
  if (document.body.classList.contains('BlogItem-page') || 
      document.querySelector('.BlogItem')) {
    
    var bioHTML = `
      <div style="border-top: 2px solid #e0e0e0; margin: 48px auto; padding-top: 32px; max-width: 760px; display: flex; gap: 20px; align-items: flex-start; font-family: inherit;">
        <img src="https://images.squarespace-cdn.com/content/v1/6980073277241e21742b84fd/27cda427-01d1-4bd8-bf80-76795c811c29/1756833165579.png" alt="Brian McGauley" style="width: 72px; height: 72px; border-radius: 50%; object-fit: cover; flex-shrink: 0;" />
        <div>
          <p style="margin: 0 0 4px 0; font-weight: 700; font-size: 1rem;">Brian McGauley</p>
          <p style="margin: 0 0 10px 0; font-size: 0.85rem; color: #666;">Founder, Imaginarii · AI Consultant · MBA Candidate, Fresno State</p>
          <p style="margin: 0 0 12px 0; font-size: 0.9rem; line-height: 1.6; color: #333;">Summa cum laude graduate (Business Admin / CIS), Phi Kappa Phi (ΦΚΦ), Beta Gamma Sigma (ΒΓΣ). 20+ years building for the web. Specializes in AI implementation, workflow automation, and business strategy for companies ready to actually use AI — not just talk about it. Based in Fresno, CA.</p>
          <p style="margin: 0; font-size: 0.85rem;">
            <a href="https://brianmcgauley.com" style="color: inherit; margin-right: 16px;">Full Bio →</a>
            <a href="https://imagi-narii.com/consulting" style="color: inherit; margin-right: 16px;">Work With Brian →</a>
            <a href="https://imagi-narii.com/blog" style="color: inherit;">More Posts →</a>
          </p>
        </div>
      </div>`;
    
    // Find the blog post body and append
    var postBody = document.querySelector('.BlogItem-body') || 
                   document.querySelector('[data-content-field="body"]') ||
                   document.querySelector('.entry-content');
    
    if (postBody) {
      postBody.insertAdjacentHTML('afterend', bioHTML);
    }
  }
});
</script>
```

3. **Save** — the bio will now auto-append to every blog post page.

**Important:** Test on both desktop and mobile after adding. Squarespace class names can vary by template version. If the bio doesn't appear, use Option A (manual code block) until you can verify the correct CSS class name for your template.

---

## Alternative: Squarespace Blog Post Template (Cleanest Long-Term Solution)

Squarespace 7.1 supports **Blog Post Footers** via the Blog Settings panel:

1. Go to **Pages → [Your Blog] → Blog Settings (gear icon)**
2. Look for **Post Metadata** or **Author Display** settings
3. Enable **Show Author** — this will display the author's name and profile photo automatically on every post
4. Make sure your Author Profile is complete under **Settings → Author Profiles**

This is the cleanest solution but gives you less design control than the HTML block approach.

---

## Bio Variations

### Very Short (for social sharing cards or schema markup):
> Brian McGauley — AI consultant, MBA candidate, Fresno State. Founder of Imaginarii. 20+ years in web development.

### Medium (for guest posts or syndication):
> Brian McGauley is the founder of Imaginarii, an AI consulting and digital services firm based in Fresno, CA. A summa cum laude Business Administration graduate and current MBA candidate at Fresno State, he holds memberships in Phi Kappa Phi and Beta Gamma Sigma. He writes about AI implementation, business strategy, and the Central Valley's evolving tech landscape.

### Schema.org Structured Data (paste in Code Injection > Header for each post):
```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "author": {
    "@type": "Person",
    "name": "Brian McGauley",
    "url": "https://brianmcgauley.com",
    "jobTitle": "Founder, AI Consultant",
    "affiliation": {
      "@type": "Organization",
      "name": "Imaginarii",
      "url": "https://imagi-narii.com"
    },
    "alumniOf": {
      "@type": "CollegeOrUniversity",
      "name": "California State University, Fresno"
    }
  },
  "publisher": {
    "@type": "Organization",
    "name": "Imaginarii",
    "url": "https://imagi-narii.com"
  }
}
</script>
```
