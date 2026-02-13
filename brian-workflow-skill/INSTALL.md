# Installation & Quick Start

## Download Your Skill

**[brian-dev-workflow.skill](brian-dev-workflow.skill)** - Click to download

## Install in Claude

1. Go to [claude.ai](https://claude.ai)
2. Click your profile → **Settings**
3. Navigate to **Skills** section
4. Click **Add Skill**
5. Upload `brian-dev-workflow.skill`
6. Done! The skill activates automatically

## How It Works

The skill triggers whenever you:
- Ask about Next.js, React, TypeScript, or Supabase
- Request help with features, debugging, or architecture
- Mention testing, CI/CD, or project setup
- Need web development assistance

## Quick Examples

### Starting a New Project
```
You: "Let's start a new Next.js project for my music artist website"

Claude: [Uses spec-kit workflow]
- Clones spec-kit template
- Creates spec.md, plan.md, tasks.md
- Asks clarifying questions about requirements
- Sets up proper Git workflow
```

### Adding a Feature
```
You: "Add a newsletter signup form with email validation"

Claude: [Follows research-first approach]
- Checks for relevant MCPs/skills
- Researches React Hook Form + Zod patterns
- Creates feature branch
- Writes component with strict TypeScript
- Writes unit and integration tests
- Validates all quality gates
- Provides PR-ready code
```

### Debugging
```
You: "The Supabase auth isn't working correctly"

Claude: [Research-driven debugging]
- Checks latest Supabase auth documentation
- Reviews error handling patterns
- Suggests fixes with TypeScript safety
- Includes test cases for the fix
```

## What You'll Notice

**Before the skill:**
- Generic Next.js advice
- May skip testing
- No spec/planning focus
- Casual Git workflow

**With the skill:**
- Exact version-specific patterns (Next.js 15.5.6, React 19.2.0)
- Always includes tests
- Starts with spec-kit
- Enforces feature branches + PRs
- Research before coding
- Strict TypeScript validation

## Skill Structure

```
SKILL.md (main workflow)
├── Project Initialization (spec-kit)
├── Feature Development (4-phase process)
├── Research Phase (MCPs, docs, patterns)
└── Decision Trees (guides workflow choices)

references/
├── tech-versions.md (Next.js 15, React 19, Supabase patterns)
├── testing-guide.md (Vitest, Playwright, Testing Library)
└── standards.md (TypeScript strict rules, code patterns)
```

## Customization

Want to update the skill?

1. Edit files in the skill directory
2. Re-package: `python package_skill.py brian-dev-workflow ./output`
3. Re-upload to Claude

Common customizations:
- Update `tech-versions.md` when you upgrade packages
- Add patterns to `standards.md` for your team conventions
- Extend `testing-guide.md` with your specific test cases

## Tips for Best Results

1. **Be specific**: "Add Stripe checkout" vs "help with payments"
2. **Reference your specs**: Mention spec.md or plan.md when relevant
3. **Ask for validation**: "Will this pass CI?" triggers quality checks
4. **Request research**: "Find latest Next.js pattern for..." triggers research
5. **Mention testing**: Claude will automatically include comprehensive tests

## Support

Questions or issues? The skill follows the exact workflow you specified:
- Spec-driven with spec-kit
- Research-first (MCPs, skills, docs)
- Feature branches only
- Strict TypeScript
- Comprehensive testing
- CI validation before commit

---

**You're all set! Start building with senior-level rigor.** 🎸
