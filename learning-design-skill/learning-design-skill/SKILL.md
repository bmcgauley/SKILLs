---
name: learning-design
description: Comprehensive learning design skill for creating effective educational experiences following instructional design principles. This skill should be used when developing learning objectives, designing assessment strategies, creating engagement techniques, structuring learning pathways, or implementing pedagogical frameworks. Transforms educational content into effective learning experiences that achieve measurable outcomes.
license: Complete terms in LICENSE.txt
---

# Learning Design for Educational Content

This skill provides comprehensive workflows for designing effective learning experiences that achieve measurable educational outcomes. It applies instructional design principles, cognitive load theory, and evidence-based pedagogical strategies to transform content into engaging and effective learning materials.

## Purpose

Learning design ensures educational content achieves its intended outcomes through systematic application of pedagogical principles. This skill addresses the challenge of transforming subject matter expertise into structured learning experiences that accommodate different learning styles and achievement levels.

## When to Use This Skill

**Primary Applications:**
- Developing SMART learning objectives using Bloom's Taxonomy
- Creating aligned assessment strategies
- Designing engagement techniques for diverse learners
- Structuring learning pathways with scaffolding
- Implementing Universal Design for Learning (UDL)
- Building formative and summative assessments
- Managing cognitive load in instructional materials

## Core Workflows

### 1. Define Learning Objectives

Transform content scope into measurable learning objectives using Bloom's Taxonomy.

**Process:**
1. Analyze content scope and identify core concepts
2. Select appropriate Bloom's level for each concept
3. Write objectives using action verb framework
4. Validate objectives are SMART (Specific, Measurable, Achievable, Relevant, Time-bound)

**Script Support:** Use `scripts/generate_objectives.py` to generate objectives from topic lists

**Templates:** See `assets/objectives_template.xlsx` for objective-assessment alignment matrix

**Reference:** Detailed Bloom's verb lists and examples in `references/blooms_taxonomy_guide.md`

### 2. Design Assessment Strategy

Create assessment instruments aligned with learning objectives.

**Process:**
1. Map each objective to appropriate assessment type
2. Select assessment methods matching cognitive levels
3. Design rubrics with clear performance criteria
4. Plan assessment timeline (diagnostic, formative, summative)

**Script Support:** Use `scripts/create_rubric.py` to generate customizable rubrics

**Templates:** Assessment templates available in `assets/assessment_templates/`

**Reference:** Complete assessment design guide in `references/assessment_strategies.md`

### 3. Create Engagement Strategies

Apply ARCS Motivation Model and active learning principles.

**Process:**
1. Design attention-grabbing hooks and varied activities
2. Establish relevance through real-world connections
3. Build confidence with scaffolded practice
4. Ensure satisfaction through achievement recognition

**Script Support:** Use `scripts/engagement_planner.py` to generate activity suggestions

**Templates:** Engagement activity cards in `assets/engagement_activities/`

**Reference:** ARCS implementation guide in `references/arcs_model.md`

### 4. Structure Learning Pathways

Design sequential learning experiences with prerequisite mapping.

**Process:**
1. Identify concept dependencies and prerequisites
2. Apply scaffolding (I Do, We Do, You Do)
3. Design branching paths for differentiation
4. Implement cognitive load management strategies

**Script Support:** Use `scripts/pathway_mapper.py` to visualize learning sequences

**Templates:** Pathway planning templates in `assets/pathway_templates/`

**Reference:** Cognitive load theory application in `references/cognitive_load_management.md`

### 5. Implement Universal Design

Create inclusive learning experiences accessible to all learners.

**Process:**
1. Provide multiple means of representation
2. Offer multiple means of engagement
3. Enable multiple means of action/expression
4. Implement accessibility features

**Script Support:** Use `scripts/accessibility_checker.py` to validate compliance

**Templates:** UDL planning matrix in `assets/udl_framework.xlsx`

**Reference:** Complete UDL guidelines in `references/universal_design_learning.md`

## Bundled Resources

### Scripts (`/scripts`)
- `generate_objectives.py` - Generate learning objectives from topics
- `create_rubric.py` - Build assessment rubrics
- `engagement_planner.py` - Suggest engagement activities
- `pathway_mapper.py` - Visualize learning sequences
- `accessibility_checker.py` - Validate UDL compliance
- `cognitive_load_calculator.py` - Estimate and balance cognitive load

### References (`/references`)
- `blooms_taxonomy_guide.md` - Complete verb lists and examples by level
- `assessment_strategies.md` - Detailed assessment design guidance
- `arcs_model.md` - ARCS motivation model implementation
- `cognitive_load_management.md` - Managing intrinsic, extraneous, and germane load
- `universal_design_learning.md` - UDL principles and guidelines
- `learning_styles.md` - Accommodating diverse learning preferences
- `scaffolding_techniques.md` - Progressive support strategies

### Assets (`/assets`)
- `objectives_template.xlsx` - Learning objective builder spreadsheet
- `assessment_templates/` - Quiz, test, project rubric templates
- `engagement_activities/` - Activity cards and instructions
- `pathway_templates/` - Learning sequence planners
- `udl_framework.xlsx` - UDL implementation checklist
- `lesson_plan_template.docx` - Standard lesson planning format
- `storyboard_templates/` - Visual planning templates

## Best Practices

1. **Start with Objectives:** Always define measurable outcomes before designing content
2. **Align Everything:** Ensure objectives, content, activities, and assessments align
3. **Design for Diversity:** Assume learners have varied backgrounds and abilities
4. **Chunk Content:** Break complex topics into manageable pieces
5. **Provide Practice:** Include immediate application opportunities
6. **Give Feedback:** Ensure timely, specific, actionable feedback
7. **Iterate Based on Data:** Use assessment results to improve design

## Common Pitfalls to Avoid

- Writing vague, unmeasurable objectives
- Misaligning assessments with taught content
- Cognitive overload from too much information
- Ignoring prerequisite knowledge gaps
- One-size-fits-all approaches
- Delayed or missing feedback loops
- Decorative rather than instructional multimedia

## Integration with Other Skills

- **With Content Outlining:** Objectives inform content structure
- **With Scriptwriting:** Engagement strategies guide script development
- **With Quality Assurance:** Assessment data validates learning effectiveness
- **With Project Management:** Learning milestones align with project schedule

## Quick Start

1. Review your content scope in `references/blooms_taxonomy_guide.md`
2. Run `scripts/generate_objectives.py` with your topic list
3. Use `assets/objectives_template.xlsx` to align objectives with assessments
4. Apply `scripts/engagement_planner.py` for activity suggestions
5. Validate with `scripts/accessibility_checker.py`

## Validation Checklist

- [ ] All content has measurable learning objectives
- [ ] Assessments directly measure stated objectives
- [ ] Multiple engagement strategies included
- [ ] Prerequisites clearly identified
- [ ] Cognitive load is managed
- [ ] Accessibility requirements met
- [ ] Feedback mechanisms in place

---

Citation: Based on instructional design principles from PMBOK® Guide Seventh Edition (PMI, 2021), Agile Practice Guide (PMI, 2017), and The Standard for Organizational Project Management (PMI, 2018).
