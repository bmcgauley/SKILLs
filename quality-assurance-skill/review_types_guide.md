# Review Types and Techniques Guide

## Overview

Reviews are systematic examinations of work products to identify defects, improve quality, and share knowledge. Different review types serve different purposes and offer varying levels of formality and rigor.

## Review Types Comparison

| Type | Formality | Participants | Duration | Defect Finding | Knowledge Transfer |
|------|-----------|--------------|----------|----------------|-------------------|
| Informal Review | Low | 2-3 people | 30-60 min | Low-Medium | Medium |
| Walkthrough | Low-Medium | 3-7 people | 1-2 hours | Medium | High |
| Technical Review | Medium-High | 3-5 experts | 2-4 hours | High | Medium |
| Inspection | High | 3-6 people | 2-4 hours | Very High | Low-Medium |

## Detailed Review Types

### 1. Informal Review

**Purpose:** Quick feedback and error detection

**Characteristics:**
- No formal process
- No meeting required
- Minimal documentation
- Peer-to-peer review

**Process:**
1. Author requests review
2. Reviewer examines work product
3. Feedback provided (verbal or written)
4. Author addresses feedback

**When to Use:**
- Early drafts
- Small changes
- Low-risk items
- Time constraints

**Benefits:**
- Fast turnaround
- Low overhead
- Flexible approach
- Immediate feedback

### 2. Walkthrough

**Purpose:** Knowledge transfer and feedback

**Characteristics:**
- Led by author
- Educational focus
- Informal atmosphere
- Scenario-based review

**Process:**
1. Author schedules walkthrough
2. Distributes materials (optional)
3. Presents work product
4. Participants ask questions
5. Scribe notes issues
6. Author addresses feedback

**Roles:**
- **Author:** Leads walkthrough
- **Participants:** Ask questions, provide feedback
- **Scribe:** Documents issues (optional)

**When to Use:**
- New team members
- Complex designs
- Knowledge sharing needed
- Alternative approaches exploration

### 3. Technical Review

**Purpose:** Evaluate technical correctness

**Characteristics:**
- Technical focus
- Expert participants
- Documented findings
- Decision-making

**Process:**
1. Review planned and scheduled
2. Materials distributed in advance
3. Participants review independently
4. Meeting to discuss findings
5. Technical decisions made
6. Action items assigned

**Roles:**
- **Moderator:** Facilitates meeting
- **Technical Experts:** Evaluate correctness
- **Author:** Answers questions
- **Recorder:** Documents decisions

**When to Use:**
- Architecture decisions
- Technical specifications
- Algorithm selection
- Performance optimization

### 4. Inspection (Formal Review)

**Purpose:** Find maximum defects systematically

**Characteristics:**
- Highly formal process
- Defined roles
- Metrics collected
- Follow-up required

**Process:**
1. **Planning:** Schedule, assign roles
2. **Overview:** Optional education session
3. **Preparation:** Individual review
4. **Meeting:** Discuss defects
5. **Rework:** Fix identified issues
6. **Follow-up:** Verify corrections

**Roles:**
- **Moderator:** Trained facilitator
- **Author:** Creator of work product
- **Inspector:** Finds defects
- **Reader:** Presents work product
- **Recorder:** Documents defects

**When to Use:**
- Critical components
- High-risk areas
- Regulatory requirements
- Quality gates

## Review Preparation

### For Reviewers

**Before the Review:**
- Understand review objectives
- Review requirements/standards
- Allocate sufficient time
- Prepare questions/comments
- Use checklists if available

**Review Checklist Example:**
- [ ] Requirements coverage
- [ ] Design consistency
- [ ] Coding standards
- [ ] Error handling
- [ ] Performance considerations
- [ ] Security aspects
- [ ] Documentation completeness

### For Authors

**Before the Review:**
- Ensure work product is ready
- Provide context documentation
- Identify specific concerns
- Distribute materials early
- Set clear objectives

**Material Preparation:**
- Clean, formatted documents
- Line numbers for reference
- Highlighted changes (if applicable)
- Supporting documentation
- Review objectives statement

## Review Techniques

### 1. Checklist-Based

**Description:** Use predefined checklists to guide review

**Benefits:**
- Consistent coverage
- Reduced missed items
- Efficient process
- Knowledge capture

**Example Checklist Items:**
- Functional correctness
- Input validation
- Resource management
- Exception handling
- Logging adequacy

### 2. Scenario-Based

**Description:** Review through use case scenarios

**Benefits:**
- User perspective
- End-to-end validation
- Integration issues detection
- Requirement validation

**Example Scenarios:**
- Normal flow
- Alternative flows
- Exception cases
- Boundary conditions
- Performance scenarios

### 3. Perspective-Based

**Description:** Different reviewers adopt different perspectives

**Perspectives:**
- User perspective
- Tester perspective
- Maintainer perspective
- Operations perspective
- Security perspective

**Benefits:**
- Comprehensive coverage
- Diverse defect types
- Reduced overlap
- Specialized expertise

### 4. Risk-Based

**Description:** Focus on high-risk areas

**Process:**
1. Identify risk areas
2. Allocate review effort
3. Apply rigorous techniques
4. Document risk mitigation

**Benefits:**
- Efficient resource use
- Critical defect focus
- Prioritized effort
- Risk reduction

## Review Meeting Management

### Effective Meeting Practices

**Do's:**
- Start and end on time
- Focus on defects, not solutions
- Maintain respectful atmosphere
- Document all findings
- Avoid personal criticism
- Stay on topic

**Don'ts:**
- Problem solve during meeting
- Evaluate personnel
- Discuss style preferences
- Make it personal
- Skip documentation
- Rush through items

### Meeting Agenda Template

```
Review Meeting Agenda
Date: [Date]
Time: [Start - End]
Location: [Room/Virtual]

1. Opening (5 min)
   - Objectives
   - Ground rules
   - Role assignments

2. Review Overview (10 min)
   - Scope confirmation
   - Key areas of focus
   - Review approach

3. Defect Discussion (60-90 min)
   - Page-by-page review
   - Defect logging
   - Severity assignment

4. Summary (10 min)
   - Defect count
   - Major issues
   - Action items

5. Next Steps (5 min)
   - Rework timeline
   - Follow-up meeting
   - Exit criteria
```

## Defect Classification

### Severity Levels

**Critical Defects:**
- Incorrect functionality
- Missing requirements
- Architecture flaws
- Security vulnerabilities

**Major Defects:**
- Logic errors
- Performance issues
- Integration problems
- Standards violations

**Minor Defects:**
- Documentation errors
- Naming conventions
- Code formatting
- Optimization opportunities

### Defect Categories

**Logic Defects:**
- Algorithm errors
- Boundary issues
- Control flow problems

**Data Defects:**
- Initialization errors
- Type mismatches
- Data corruption

**Interface Defects:**
- Parameter errors
- Protocol violations
- Integration issues

**Documentation Defects:**
- Missing comments
- Incorrect descriptions
- Outdated information

## Review Metrics

### Efficiency Metrics

**Review Rate:**
```
Pages/Hour or Lines of Code/Hour
Target: 3-5 pages/hour for documents
        100-200 LOC/hour for code
```

**Defect Density:**
```
Defects Found / Size Reviewed
Target: 5-10 defects per page
        0.5-1 defect per 100 LOC
```

**Preparation Rate:**
```
Preparation Time / Review Time
Target: 1:1 ratio
```

### Effectiveness Metrics

**Defect Detection Rate:**
```
Review Defects / Total Defects × 100
Target: > 60%
```

**Review Yield:**
```
Major Defects Found / Review Hours
Target: > 0.5 major defects/hour
```

**Defect Escape Rate:**
```
Post-Review Defects / Total Defects × 100
Target: < 20%
```

## Review Tools

### Manual Review Tools
- Printed materials with markup
- Shared documents with comments
- Review forms and checklists
- Sticky notes for issues

### Automated Review Tools

**Code Review:**
- GitHub Pull Requests
- Gerrit Code Review
- Crucible
- Review Board

**Document Review:**
- Microsoft Word Track Changes
- Google Docs Suggestions
- Adobe Acrobat Comments
- Confluence inline comments

**Static Analysis:**
- SonarQube
- Coverity
- FindBugs
- ESLint

## Best Practices

### 1. Review Culture
- Make reviews routine
- Focus on improvement
- Celebrate found defects
- Share lessons learned

### 2. Review Scope
- Limit to 200-400 LOC
- Review for 60-90 minutes max
- Take breaks for longer sessions
- Don't review too much at once

### 3. Review Timing
- Review early and often
- Before major milestones
- After significant changes
- Before integration

### 4. Review Follow-up
- Verify corrections
- Update checklists
- Share findings
- Process improvement

## Common Review Pitfalls

### 1. Ineffective Reviews
**Problem:** Reviews find few defects
**Solution:** Better preparation, checklists, training

### 2. Hostile Environment
**Problem:** Defensive authors, aggressive reviewers
**Solution:** Ground rules, focus on product not person

### 3. Solution Focus
**Problem:** Spending time solving problems
**Solution:** Log defects, solve offline

### 4. Incomplete Follow-up
**Problem:** Defects not properly addressed
**Solution:** Verification step, tracking system

### 5. Review Fatigue
**Problem:** Decreasing effectiveness over time
**Solution:** Shorter sessions, regular breaks

## Review ROI

### Cost-Benefit Analysis

**Review Costs:**
- Preparation time
- Meeting time
- Rework time
- Administrative overhead

**Review Benefits:**
- Early defect detection (10x-100x savings)
- Knowledge transfer
- Standard enforcement
- Risk reduction

**Typical ROI:**
- Every hour in review saves 4-8 hours in testing
- Every defect found in review saves $100-1000
- 20-30% reduction in total defects

## Quick Reference Checklist

### Planning a Review
- [ ] Define objectives
- [ ] Select review type
- [ ] Choose participants
- [ ] Schedule meeting
- [ ] Distribute materials
- [ ] Provide checklists

### Conducting a Review
- [ ] Start on time
- [ ] Review objectives
- [ ] Assign roles
- [ ] Follow process
- [ ] Document findings
- [ ] Agree on actions

### After the Review
- [ ] Distribute minutes
- [ ] Track corrections
- [ ] Verify fixes
- [ ] Update metrics
- [ ] Lessons learned
- [ ] Process improvement

---

*Citation: Based on IEEE 1028-2008 Standard for Software Reviews and Audits*
