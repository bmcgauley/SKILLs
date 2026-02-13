# Learning Design Skill - Complete Package

## Overview

This is a comprehensive Learning Design skill that transforms educational content into effective learning experiences. It includes automated scripts, reference guides, and templates to support instructional design following established pedagogical principles.

## Directory Structure

```
learning-design-skill/
├── SKILL.md              # Main skill documentation
├── scripts/              # Automation tools
│   ├── generate_objectives.py     # Create SMART objectives using Bloom's
│   ├── create_rubric.py          # Generate assessment rubrics
│   ├── engagement_planner.py     # Plan ARCS-based activities
│   └── pathway_mapper.py         # Visualize learning sequences
├── references/           # Detailed guides
│   ├── blooms_taxonomy_guide.md  # Complete Bloom's reference
│   └── arcs_model.md             # ARCS motivation model guide
└── assets/              # Templates and resources
    └── objectives_template.md    # Learning objectives template
```

## Quick Start Guide

### 1. Generate Learning Objectives

```bash
python scripts/generate_objectives.py "Introduction to Python" "Variables" "Functions" "Loops" -p -o markdown
```

Options:
- `-p`: Apply cognitive progression through Bloom's levels
- `-o`: Output format (text, json, markdown, csv)
- `-f`: Read topics from file
- `-l`: Use specific Bloom's level

### 2. Create Assessment Rubrics

```bash
python scripts/create_rubric.py presentation -o markdown
```

Supported types:
- essay
- presentation 
- project
- lab_report
- discussion
- custom (with your own criteria)

### 3. Plan Engagement Activities

```bash
python scripts/engagement_planner.py "Machine Learning" -d 45 -g small -o markdown
```

Options:
- `-d`: Duration in minutes
- `-g`: Group size (individual, small, large)
- `-obj`: Specific learning objective
- `-o`: Output format

### 4. Map Learning Pathways

```bash
python scripts/pathway_mapper.py --demo -o mermaid
```

Options:
- `--demo`: Generate demo pathway
- `-f`: Load from JSON file
- `-o`: Output format (json, markdown, text, mermaid)

## Using the References

### Bloom's Taxonomy Guide
Located at `references/blooms_taxonomy_guide.md`

Provides:
- Complete verb lists for each cognitive level
- Question stems and assessment examples
- Progressive learning design strategies
- Common pitfalls to avoid

### ARCS Model Guide
Located at `references/arcs_model.md`

Covers:
- Attention, Relevance, Confidence, Satisfaction strategies
- Implementation examples for each component
- Troubleshooting guide for motivation issues
- Integration with other instructional models

## Using the Templates

### Learning Objectives Template
Located at `assets/objectives_template.md`

Includes:
- Objectives alignment matrix
- SMART objective breakdown
- Prerequisite mapping
- Cognitive load analysis
- Differentiation planning
- Assessment rubric summary

## Integration with Other Skills

This skill works seamlessly with:
- **Content Outlining:** Objectives inform content structure
- **Scriptwriting:** Engagement strategies guide script development  
- **Quality Assurance:** Assessment data validates effectiveness
- **Project Management:** Learning milestones align with schedule

## Example Workflow

1. **Define Objectives:**
   ```bash
   python scripts/generate_objectives.py -f topics.txt -p -o markdown > objectives.md
   ```

2. **Create Rubrics:**
   ```bash
   python scripts/create_rubric.py project -o markdown > rubric.md
   ```

3. **Plan Activities:**
   ```bash
   python scripts/engagement_planner.py "Project Management" -d 60 -o markdown > activities.md
   ```

4. **Map Pathway:**
   ```bash
   python scripts/pathway_mapper.py -f pathway.json -o mermaid > pathway.md
   ```

## Customization

All scripts accept custom inputs and can be modified for specific needs:

- Edit verb lists in `generate_objectives.py`
- Add assignment types in `create_rubric.py`
- Customize activities in `engagement_planner.py`
- Define pathways in JSON for `pathway_mapper.py`

## Best Practices

1. **Start with clear objectives** before designing content
2. **Align assessments** with stated objectives
3. **Use variety** in engagement techniques
4. **Map prerequisites** to avoid knowledge gaps
5. **Apply scaffolding** to build confidence
6. **Consider cognitive load** at each stage
7. **Validate with learners** through pilot testing

## Troubleshooting

### Scripts not running?
- Ensure Python 3.6+ is installed
- Check file permissions (may need `chmod +x`)
- Install required libraries if needed

### Need more examples?
- Check the reference guides for detailed examples
- Run scripts with `--help` for all options
- Use `--demo` flags where available

### Want to extend functionality?
- Scripts are modular and well-documented
- Add new functions to existing scripts
- Create new scripts following the same pattern

## Citations

This skill is based on established instructional design principles from:
- PMBOK® Guide Seventh Edition (PMI, 2021)
- Agile Practice Guide (PMI, 2017)
- Anderson & Krathwohl's Revised Bloom's Taxonomy (2001)
- Keller's ARCS Model of Motivational Design (2010)

## Support

For questions or improvements, consider:
- Reviewing the detailed SKILL.md documentation
- Checking reference guides for theoretical background
- Modifying scripts to meet specific needs
- Creating additional templates in the assets folder

---

*This skill is designed to be universally applicable while maintaining alignment with project management and instructional design best practices.*
