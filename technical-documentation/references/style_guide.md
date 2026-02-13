# Technical Documentation Style Guide

## Writing Principles

### Clarity Above All
Technical documentation must be unambiguous. Every sentence should have one clear interpretation.

**Good:** "Click the Submit button to save your changes."  
**Bad:** "When you're done, submit it."

### Conciseness Without Sacrifice
Remove unnecessary words, but never at the expense of clarity.

**Good:** "Configure the server before deployment."  
**Bad:** "You will need to configure the server before you deploy."  
**Also Bad:** "Configure server." (Too terse, lacks context)

### Consistency Throughout
Use the same terms, formats, and structures throughout your documentation.

- If you call it "dashboard" in one place, don't call it "control panel" elsewhere
- If you use numbered steps in one procedure, use them in all procedures
- If you bold UI elements, bold them consistently

## Voice and Tone

### Active Voice
Use active voice for instructions and descriptions.

**Active:** "The system validates the input."  
**Passive:** "The input is validated by the system."

**Exception:** Use passive voice when the actor is unknown or irrelevant:  
"The log file is created automatically." (We don't care what creates it)

### Second Person
Address the reader directly as "you."

**Good:** "You can configure the settings..."  
**Bad:** "Users can configure the settings..."  
**Bad:** "One can configure the settings..."

### Present Tense
Describe current states and behaviors in present tense.

**Good:** "The API returns a JSON response."  
**Bad:** "The API will return a JSON response."

**Exception:** Use future tense for results of actions:  
"Click Save. The system will process your request."

### Professional but Approachable
- Avoid overly formal language
- Don't use slang or colloquialisms
- Be friendly without being casual

**Good:** "This error usually means your API key has expired."  
**Bad:** "This error typically indicates that the API key has exceeded its validity period." (Too formal)  
**Bad:** "Oops! Your API key went kaput!" (Too casual)

## Formatting Conventions

### Headings

#### Hierarchy Rules
- Use sentence case (capitalize only first word and proper nouns)
- Don't skip heading levels (h1 → h2 → h3, not h1 → h3)
- Keep headings concise (under 60 characters)
- Make headings descriptive and searchable

#### Examples
```markdown
# Installation guide              ✓ Sentence case
## System requirements           ✓ Clear hierarchy
### Operating system support     ✓ Specific and searchable

# Installation Guide             ✗ Title case
### Operating System Support     ✗ Skipped h2
## Requirements For Running The Application On Your System  ✗ Too long
```

### Lists

#### Bullet Points
Use for:
- Unordered information
- Options where order doesn't matter
- Feature lists
- Requirements

#### Numbered Lists
Use for:
- Sequential steps
- Procedures
- Ranked items
- Items referenced elsewhere

#### List Formatting
- Start each item with a capital letter
- End with a period only if the item is a complete sentence
- Keep items parallel in structure
- Indent nested lists by 2 spaces

### Code Formatting

#### Inline Code
Use backticks for:
- Commands: `npm install`
- File names: `config.yaml`
- Function names: `getUserById()`
- Values: `true`, `false`, `null`
- Short code snippets: `const x = 42;`

#### Code Blocks
Always specify the language for syntax highlighting:

````markdown
```python
def hello_world():
    print("Hello, World!")
```

```bash
curl -X GET https://api.example.com/users
```

```json
{
  "name": "John Doe",
  "age": 30
}
```
````

### Tables

#### When to Use Tables
- Comparing features or options
- Listing parameters or configurations
- Showing compatibility matrices
- Presenting structured data

#### Table Best Practices
```markdown
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier |
| `name` | string | Yes | Display name |
| `email` | string | No | Contact email |
```

- Use backticks for code elements in tables
- Align columns for readability in source
- Keep descriptions concise
- Include units where applicable

### Emphasis

#### Bold
Use **bold** for:
- UI elements: **File** menu
- Important warnings
- Key terms on first use

#### Italics
Use *italics* for:
- Emphasis within sentences
- Book/document titles
- Introducing new terms

#### Avoid
- Underlining (confused with links)
- ALL CAPS (except for constants)
- Multiple emphasis types together

## Special Elements

### Notes and Warnings

#### Hierarchy of Notices

**Note:** Additional helpful information  
**Tip:** Best practice or useful shortcut  
**Important:** Critical information for success  
**Warning:** Potential problem or mistake  
**Danger:** Risk of data loss or security issue  

#### Formatting
```markdown
> **Note:** This feature requires version 2.0 or later.

> **Warning:** This action cannot be undone.

> **Danger:** Improper configuration may expose sensitive data.
```

### Links

#### Descriptive Link Text
**Good:** [View the configuration guide](link)  
**Bad:** [Click here](link) for configuration  
**Bad:** The guide is available [here](link)

#### Link Best Practices
- Link text should make sense out of context
- Avoid linking entire sentences
- Check links regularly for accuracy
- Use relative links for internal documentation
- Use HTTPS for external links

### Images and Diagrams

#### Alt Text Requirements
Every image must have descriptive alt text:

```markdown
![Architecture diagram showing microservices communication](architecture.png)
```

#### Image Guidelines
- Use SVG for diagrams (scalable)
- Use PNG for screenshots
- Annotate screenshots with callouts
- Keep file sizes optimized
- Update images when UI changes

## Language Guidelines

### Word Choice

#### Preferred Terms
| Instead of | Use |
|------------|-----|
| utilize | use |
| implement | set up, install, add |
| leverage | use |
| via | through, using |
| prior to | before |
| subsequent to | after |
| in order to | to |
| a number of | several, many |
| the majority of | most |

#### Technical Terms
- Define acronyms on first use: "API (Application Programming Interface)"
- Link to glossary for complex terms
- Avoid jargon when possible
- Use industry-standard terminology

### Sentence Structure

#### Keep It Simple
- Average 15-20 words per sentence
- Maximum 25 words for complex ideas
- One idea per sentence
- Vary sentence length for rhythm

#### Parallel Construction
When listing items, maintain parallel structure:

**Good:**
- Installing the software
- Configuring the settings
- Testing the connection

**Bad:**
- Install the software
- Configuration of settings
- To test the connection

### Common Mistakes to Avoid

#### Anthropomorphization
Don't give human qualities to software:

**Bad:** "The server wants to connect..."  
**Good:** "The server attempts to connect..."

#### Future Features
Don't document features that don't exist:

**Bad:** "This feature will be available in the next release."  
**Good:** "This feature is planned for version 2.1." (only if confirmed)

#### Ambiguous Pronouns
Clarify what "it," "this," or "that" refers to:

**Bad:** "After configuring it, restart it."  
**Good:** "After configuring the server, restart the service."

## API Documentation Specifics

### Endpoint Documentation
Always include:
1. HTTP method and path
2. Purpose (one sentence)
3. Authentication requirements
4. Parameters (all)
5. Request body (if applicable)
6. Success response
7. Error responses
8. Example request
9. Example response

### Parameter Descriptions
Format: `name` (type, required/optional): Description

Example:
- `userId` (string, required): Unique identifier for the user
- `limit` (integer, optional): Maximum number of results to return. Default: 10

### Error Documentation
Include:
- Error code
- HTTP status
- Error message format
- Possible causes
- Resolution steps

## Version-Specific Guidelines

### Documenting Versions
- Always specify which version the documentation covers
- Note version requirements for features
- Mark deprecated features clearly
- Provide migration guides for breaking changes

### Version Notation
```markdown
> **Version:** 2.1.0 and later

> **Deprecated:** This endpoint is deprecated as of v3.0. Use `/v2/users` instead.

> **Breaking Change:** As of v2.0, this method returns an array instead of an object.
```

## Accessibility Guidelines

### Screen Reader Compatibility
- Use semantic HTML/Markdown
- Provide alt text for all images
- Don't rely on color alone
- Use descriptive headings
- Maintain logical reading order

### International Considerations
- Use standard date formats (ISO 8601)
- Specify time zones
- Avoid idioms and cultural references
- Consider translation requirements
- Use Unicode for special characters

## Quality Checklist

Before publishing, verify:

### Content
- [ ] Technically accurate
- [ ] Complete (no TODOs)
- [ ] Tested procedures work
- [ ] Examples are correct
- [ ] Links are valid

### Style
- [ ] Active voice used
- [ ] Consistent terminology
- [ ] Proper formatting
- [ ] Clear headings
- [ ] No spelling errors
- [ ] No grammar errors

### Structure
- [ ] Logical organization
- [ ] Proper heading hierarchy
- [ ] Working navigation
- [ ] Search-friendly titles
- [ ] Cross-references work

### Accessibility
- [ ] Alt text present
- [ ] Readable by screen readers
- [ ] Color not sole indicator
- [ ] Keyboard navigable
- [ ] Mobile responsive

## Maintenance Guidelines

### Regular Reviews
- **Weekly:** Fix reported issues
- **Monthly:** Update for new features
- **Quarterly:** Full accuracy review
- **Annually:** Structural reorganization

### Feedback Integration
1. Monitor support tickets
2. Track page analytics
3. Conduct user surveys
4. Test with new users
5. Iterate based on feedback

## Tools and Resources

### Recommended Tools
- **Markdown editors:** VSCode, Typora
- **Diagram tools:** draw.io, Mermaid
- **Screenshot tools:** Snagit, ShareX
- **Link checkers:** linkchecker, broken-link-checker
- **Spell checkers:** cspell, aspell

### Style References
- Microsoft Style Guide
- Google Developer Documentation Style Guide
- Chicago Manual of Style (for general writing)
- Read the Docs documentation guide

### Templates
Use provided templates for:
- API endpoints
- Troubleshooting guides
- Installation instructions
- Configuration references
- Migration guides

Remember: Good documentation is never finished, only improved.
