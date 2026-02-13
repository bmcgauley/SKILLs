# Defect Report Template

## Defect Information

**Defect ID:** [Auto-generated or Manual ID]  
**Date Found:** [YYYY-MM-DD]  
**Time Found:** [HH:MM]  
**Found By:** [Name/ID]  
**Project/Module:** [Project or Module Name]  
**Build/Version:** [Version Number]  
**Environment:** [Development/Testing/Staging/Production]

## Classification

**Severity:**
- [ ] Critical (System crash, data loss, security breach)
- [ ] Major (Major functionality broken, no workaround)
- [ ] Moderate (Functionality impaired, workaround exists)  
- [ ] Minor (Cosmetic, UI issues)
- [ ] Trivial (Suggestions, enhancements)

**Priority:**
- [ ] Immediate (Fix within 24 hours)
- [ ] High (Fix in current iteration)
- [ ] Medium (Fix in next iteration)
- [ ] Low (Fix when time permits)

**Type:**
- [ ] Functional
- [ ] Performance
- [ ] Security
- [ ] Usability
- [ ] Compatibility
- [ ] Documentation
- [ ] Localization
- [ ] Configuration

## Defect Description

### Summary
[One-line summary of the defect - be specific and concise]

### Detailed Description
[Detailed explanation of what is wrong, including context and impact]

### Steps to Reproduce
1. [First step]
2. [Second step]
3. [Continue with numbered steps]
4. [Final step that produces the defect]

**Frequency:** [Always / Sometimes / Random]  
**Reproducibility Rate:** [100% / 75% / 50% / 25% / Cannot reproduce]

### Expected Result
[What should happen according to requirements/specifications]

### Actual Result  
[What actually happens]

### Impact Analysis
- **User Impact:** [How this affects end users]
- **Business Impact:** [Business consequences if not fixed]
- **Workaround Available:** [Yes/No - If yes, describe]

## Technical Details

### Error Messages
```
[Copy exact error messages, stack traces, or logs]
```

### Test Data
- **Input Data Used:** [Specific data that triggered the defect]
- **Database State:** [Relevant database conditions]
- **Configuration:** [Relevant system/application settings]

### System Information
- **Operating System:** [OS and version]
- **Browser:** [Browser and version if applicable]
- **Device:** [Device type if mobile/tablet]
- **Network:** [Network conditions if relevant]
- **Memory/CPU:** [Resource state if performance-related]

## Attachments

- [ ] Screenshots ([filename])
- [ ] Video Recording ([filename])
- [ ] Log Files ([filename])
- [ ] Test Data Files ([filename])
- [ ] Core Dumps ([filename])

## Assignment and Tracking

**Assigned To:** [Developer/Team Name]  
**Assigned Date:** [YYYY-MM-DD]  
**Target Resolution Date:** [YYYY-MM-DD]  
**Actual Resolution Date:** [YYYY-MM-DD]

**Status:**
- [ ] New
- [ ] Open
- [ ] Assigned
- [ ] In Progress
- [ ] Fixed
- [ ] Ready for Test
- [ ] Testing
- [ ] Verified
- [ ] Closed
- [ ] Reopened
- [ ] Deferred
- [ ] Rejected

## Root Cause Analysis

### Root Cause
[Identify the fundamental cause of the defect]

### Root Cause Category
- [ ] Requirements Gap
- [ ] Design Issue
- [ ] Coding Error
- [ ] Configuration Issue
- [ ] Environment Issue
- [ ] Data Issue
- [ ] Integration Issue
- [ ] Human Error
- [ ] Process Gap

### Preventive Actions
[What can be done to prevent similar defects in future]

## Resolution

### Resolution Type
- [ ] Code Change
- [ ] Configuration Change
- [ ] Documentation Update
- [ ] Data Fix
- [ ] Environment Fix
- [ ] Not a Defect
- [ ] Duplicate
- [ ] Cannot Reproduce
- [ ] Works as Designed
- [ ] Deferred to Future Release

### Resolution Description
[Detailed description of how the defect was fixed]

### Files Changed
```
[List of files modified with version/commit info]
- File1.java (commit: abc123)
- File2.xml (commit: def456)
```

### Unit Tests Added/Modified
- [ ] New unit tests created
- [ ] Existing tests updated
- [ ] No test changes required

**Test Details:**
[Description of test coverage added]

## Testing and Verification

### Test Cases to Execute
- [ ] [Test Case ID/Name 1]
- [ ] [Test Case ID/Name 2]
- [ ] [Test Case ID/Name 3]

### Regression Testing Required
- [ ] Full Regression
- [ ] Targeted Regression
- [ ] No Regression Needed

**Regression Scope:**
[Areas that need regression testing]

### Verification Steps
1. [Step to verify fix]
2. [Additional verification step]
3. [Final confirmation step]

### Verification Results
- **Verified By:** [Tester Name]
- **Verification Date:** [YYYY-MM-DD]
- **Build Verified:** [Build/Version Number]
- **Status:** [Pass/Fail]
- **Comments:** [Any additional notes]

## History

| Date | Action | By | Comments |
|------|--------|-----|----------|
| YYYY-MM-DD | Created | [Name] | Initial report |
| YYYY-MM-DD | Assigned | [Name] | Assigned to developer |
| YYYY-MM-DD | Status Changed | [Name] | In Progress |
| YYYY-MM-DD | Fixed | [Name] | Code fix applied |
| YYYY-MM-DD | Verified | [Name] | Fix confirmed |

## Metrics

**Time to Resolution:** [Hours/Days]  
**Effort Spent:** [Person-hours]  
**Number of Reopens:** [Count]  
**Related Defects:** [List of related defect IDs]

## Lessons Learned

### What Went Well
[Positive aspects of defect resolution]

### What Could Be Improved
[Areas for process improvement]

### Knowledge Base Entry
- [ ] Created
- [ ] Not Needed

**KB Article ID:** [If applicable]

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Reporter | | | |
| Developer | | | |
| Tester | | | |
| Manager | | | |

---

## Quick Reference - Severity Guidelines

### Critical
- System crash or hang
- Data loss or corruption
- Security vulnerability exposed
- Complete feature failure
- No workaround available

### Major  
- Major functionality not working
- Significant performance degradation
- Workaround difficult or complex
- Affects many users

### Moderate
- Feature partially working
- Workaround available
- Moderate performance issue
- Affects some users

### Minor
- Cosmetic issues
- Minor UI problems
- Spelling/grammar errors
- Minor inconvenience

### Trivial
- Suggestions for improvement
- Nice-to-have features
- Very minor issues

## Quick Reference - Priority Guidelines

### Immediate (P1)
- Fix within 24 hours
- Blocking critical business function
- Affecting production
- Security vulnerability

### High (P2)
- Fix in current sprint/iteration
- Significant business impact
- Blocking testing
- Customer-reported issue

### Medium (P3)
- Fix in next sprint/iteration
- Moderate business impact
- Has workaround
- Internal issue

### Low (P4)
- Fix when time permits
- Low business impact
- Cosmetic issue
- Enhancement request

---

*Note: Customize this template based on your organization's specific needs and processes*
