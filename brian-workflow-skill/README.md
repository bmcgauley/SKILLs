# Brian's Development Workflow Skill

A senior-level development workflow skill for Next.js 15 + React 19 + Supabase projects.

## What It Does

Enforces your complete development workflow:
- ✅ **Spec-driven development** with spec-kit
- ✅ **Research-first approach** (checks MCPs/skills, validates docs)
- ✅ **Feature branch workflow** (never pushes to main)
- ✅ **Strict TypeScript** (no `any` types)
- ✅ **Comprehensive testing** (Vitest, Playwright, Testing Library)
- ✅ **CI validation** before commits
- ✅ **Task tracking** synced with GitHub Issues

## Installation

1. Download `brian-dev-workflow.skill`
2. In Claude.ai: Settings → Skills → Add Skill
3. Upload the `.skill` file

## When It Triggers

Automatically activates when you mention:
- Next.js, React, TypeScript, Supabase
- New features, debugging, architecture
- Testing, CI/CD, project setup
- Any web development work

## What's Inside

**SKILL.md** - Main workflow with decision trees:
- Project initialization with spec-kit
- 4-phase feature development process
- Research requirements before coding
- Quality assurance checklist
- Git workflow and PR process

**Reference Files:**
- `tech-versions.md` - Current stack versions and patterns
- `testing-guide.md` - Test examples (unit, component, E2E)
- `standards.md` - TypeScript rules and code patterns

## Example Usage

**You:** "Help me add user authentication"

**Claude:** 
1. Checks available MCPs/skills
2. Researches latest Supabase auth patterns
3. Creates feature branch
4. Writes implementation with strict TypeScript
5. Writes comprehensive tests
6. Validates locally before commit
7. Creates PR description

**You:** "Start a new Next.js project"

**Claude:**
1. Clones spec-kit
2. Generates spec.md
3. Asks clarifying questions
4. Creates plan.md and tasks.md
5. Sets up project structure
6. Initializes Git workflow

## Key Benefits

- **No assumptions**: Always validates against current docs
- **Quality gates**: Ensures tests pass, TypeScript strict, CI succeeds
- **Proper process**: Feature branches, PRs, task tracking
- **Senior mindset**: Methodical, thorough, efficient

## Files

```
brian-dev-workflow/
├── SKILL.md                     # Main workflow
└── references/
    ├── tech-versions.md         # Stack versions & patterns
    ├── testing-guide.md         # Test examples
    └── standards.md             # Coding standards
```

---

**Ready to code with rigorous quality standards!** 🚀
