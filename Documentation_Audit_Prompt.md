# Comprehensive Documentation Audit & Optimization Prompt

## Context & Objectives

You are tasked with conducting a comprehensive audit and optimization of this project's documentation structure. This analysis should implement research-backed best practices for separating user-facing documentation (README.md) from AI-assistant guidance (CLAUDE.md), optimizing for both human usability and AI interaction efficiency.

**Primary Goals:**
1. Analyze current documentation structure and identify optimization opportunities
2. Recommend content separation between README.md and CLAUDE.md based on audience needs
3. Provide actionable implementation steps for documentation improvements
4. Ensure token-efficient AI interactions while maintaining comprehensive human documentation

## Analysis Framework

### Phase 1: Current State Assessment

**Inventory existing documentation files:**
- List all .md files in the repository
- Identify documentation scattered across other file types (comments, docstrings, etc.)
- Assess current README.md structure and content depth
- Check for existing CLAUDE.md or similar AI guidance files

**Content Analysis:**
- Categorize existing content by target audience (humans vs AI assistants)
- Identify redundant or outdated information
- Assess information architecture and discoverability
- Evaluate technical depth and accessibility levels

### Phase 2: Audience-Specific Content Categorization

#### README.md Content (Human-Focused)
**Essential Elements:**
- Project overview and value proposition (2-3 sentences maximum)
- Quick start guide with minimal viable setup
- Installation instructions (standard commands only)
- Basic usage examples (1-2 primary use cases)
- Contributing guidelines (link to detailed docs if complex)
- License and contact information

**Content Characteristics:**
- Marketing-oriented language that sells the project's value
- Assumes minimal technical context
- Progressive disclosure (basic → advanced)
- Visual elements (badges, screenshots, diagrams)
- Community-focused (contribution, support, acknowledgments)

#### CLAUDE.md Content (AI Assistant-Focused)
**Technical Architecture:**
- Detailed technology stack with version requirements
- Service architecture and component relationships
- Database schemas and data flow patterns
- API endpoint specifications and authentication methods
- Configuration management and environment setup

**Development Workflows:**
- Complete command reference with all available options
- Development environment setup (including edge cases)
- Testing strategies and quality gates
- Deployment procedures and rollback plans
- Debugging guides and troubleshooting steps

**AI-Specific Guidance:**
- Codebase navigation patterns and entry points
- Agent routing maps and specialized responsibilities
- Context about project history and architectural decisions
- Integration patterns with external services
- Performance optimization strategies and monitoring

**Content Characteristics:**
- Assumes high technical competency
- Comprehensive reference material
- Implementation details and edge cases
- Historical context and architectural decisions
- Tool-specific commands and configurations

### Phase 3: Content Migration Strategy

#### Migration Decision Framework
For each piece of content, evaluate:

1. **Primary Audience**: Who needs this information most?
   - General users → README.md
   - Developers/contributors → README.md or separate docs/
   - AI assistants → CLAUDE.md

2. **Complexity Level**: How technical is the content?
   - Basic/introductory → README.md
   - Intermediate → README.md with links to detailed docs
   - Advanced/comprehensive → CLAUDE.md

3. **Update Frequency**: How often does this change?
   - Stable/marketing content → README.md
   - Evolving technical details → CLAUDE.md

4. **Token Efficiency**: For AI interactions
   - Frequently referenced → CLAUDE.md
   - Rarely needed by AI → separate documentation files

#### Recommended File Structure
```
project/
├── README.md                 # Human-focused, marketing-oriented
├── CLAUDE.md                 # AI assistant comprehensive guide
├── docs/
│   ├── INSTALLATION.md       # Detailed setup instructions
│   ├── API_REFERENCE.md      # Complete API documentation
│   ├── CONTRIBUTING.md       # Contributor guidelines
│   ├── DEPLOYMENT.md         # Production deployment guide
│   └── TROUBLESHOOTING.md    # Common issues and solutions
└── .github/
    └── ISSUE_TEMPLATE.md     # Standardized issue reporting
```

## Implementation Recommendations

### Step 1: Content Audit and Mapping
1. **Create a content inventory spreadsheet** with columns:
   - Current location
   - Content type/topic
   - Target audience
   - Complexity level
   - Recommended destination
   - Migration priority

2. **Assess information gaps:**
   - Missing onboarding information for new users
   - Incomplete technical references for developers
   - Absent AI assistant guidance for complex operations

### Step 2: README.md Optimization
**Structure Template:**
```markdown
# Project Name
[Compelling one-line description]

## Quick Start
[3-5 commands to get running]

## Installation
[Standard installation method only]

## Basic Usage
[1-2 essential examples]

## Documentation
- [Installation Guide](docs/INSTALLATION.md) - Detailed setup
- [API Reference](docs/API_REFERENCE.md) - Complete API docs
- [Contributing](docs/CONTRIBUTING.md) - How to contribute

## License
[License information]
```

**Optimization Principles:**
- Keep total length under 200 lines for mobile readability
- Use progressive disclosure (basic info with links to details)
- Include compelling visuals (demos, architecture diagrams)
- Write for time-pressed users who want quick evaluation

### Step 3: CLAUDE.md Creation/Enhancement
**Structure Template:**
```markdown
# CLAUDE.md - AI Assistant Guidance

## Project Overview
[Technical architecture and key technologies]

## Development Environment
[Complete setup with all dependencies and edge cases]

## Command Reference
[All available commands with full options]

## Architecture Guide
[Service relationships, data flows, integration patterns]

## AI Agent Configuration
[Specialized agent routing and responsibilities]

## Debugging & Troubleshooting
[Common issues, logging patterns, diagnostic commands]
```

**Content Principles:**
- Assume high technical competency
- Include comprehensive command references
- Provide architectural context for decision-making
- Include historical context and rationale for design decisions

### Step 4: Supporting Documentation Files
**Create specialized documentation for:**
- **INSTALLATION.md**: Comprehensive setup for all environments
- **API_REFERENCE.md**: Complete endpoint documentation
- **CONTRIBUTING.md**: Detailed contributor onboarding
- **DEPLOYMENT.md**: Production deployment procedures
- **TROUBLESHOOTING.md**: Common issues and diagnostic steps

## Quality Validation Steps

### Content Quality Checklist
- [ ] **Audience Alignment**: Each file serves its intended audience effectively
- [ ] **Information Architecture**: Logical flow and easy navigation
- [ ] **Completeness**: No critical information gaps
- [ ] **Accuracy**: All technical details are current and correct
- [ ] **Consistency**: Terminology and formatting standards maintained

### User Experience Validation
- [ ] **New User Journey**: Can someone new to the project get started in <5 minutes?
- [ ] **Developer Onboarding**: Can a new contributor understand the architecture quickly?
- [ ] **AI Assistant Effectiveness**: Does CLAUDE.md provide sufficient context for complex tasks?

### Technical Validation
- [ ] **Link Verification**: All internal and external links work correctly
- [ ] **Code Example Testing**: All code snippets execute successfully
- [ ] **Version Alignment**: Documentation matches current codebase state
- [ ] **Token Optimization**: CLAUDE.md provides maximum context per token

## Success Metrics

**Quantitative Measures:**
- README.md length: Target <200 lines for optimal mobile experience
- Time to first success: New users should achieve basic functionality in <5 minutes
- Documentation coverage: 100% of public APIs documented
- Link health: 0% broken internal documentation links

**Qualitative Measures:**
- User feedback on onboarding experience
- Contributor time-to-productivity improvements
- AI assistant task completion accuracy
- Reduction in repetitive support questions

## Implementation Timeline

**Phase 1 (Week 1): Analysis & Planning**
- Complete content audit and mapping
- Identify critical information gaps
- Create migration plan with priorities

**Phase 2 (Week 2): Core Documentation**
- Optimize README.md for user experience
- Create/enhance CLAUDE.md for AI assistance
- Establish supporting documentation structure

**Phase 3 (Week 3): Specialized Documentation**
- Create detailed installation and API documentation
- Develop comprehensive troubleshooting guides
- Implement contributor onboarding materials

**Phase 4 (Week 4): Validation & Refinement**
- Test user journeys and developer onboarding
- Validate AI assistant effectiveness
- Gather feedback and implement improvements

## Additional Considerations

### Critical File Preservation Rules

**NEVER move or relocate these files - they must remain in place to function:**

1. **Sub-Agent System Files**: `.claude/agents/*.md`
   - These files contain AI agent definitions that must stay in `.claude/agents/` directory
   - May be read and referenced in documentation
   - **DO NOT MOVE** - moving breaks the sub-agent functionality
   - Reference their capabilities in `docs/DEVELOPMENT.md` instead

2. **Project Planning Files**: `project_plan/` directory contents
   - Contains project management and planning documents
   - May be read for context and reference
   - **DO NOT MOVE** - maintain existing project structure
   - Leave as-is even during documentation reorganization

3. **Implementation Pattern**:
   ```markdown
   # Correct approach in DEVELOPMENT.md:
   The project uses 40+ specialized sub-agents defined in `.claude/agents/` directory.
   These agents provide [describe capabilities] - see agent files for detailed specifications.

   # WRONG - do not relocate agent files:
   # ❌ Moving .claude/agents/agent-name.md to docs/agents/
   ```

### Multi-Project Workspaces
- Create workspace-level documentation strategy
- Establish consistency standards across projects
- Implement cross-project reference patterns

### Maintenance Strategy
- Schedule quarterly documentation reviews
- Implement automated link checking
- Establish content ownership and update responsibilities

### Advanced Features
- Consider interactive documentation tools
- Implement automated API documentation generation
- Create video tutorials for complex workflows

---

## Execution Instructions

1. **Run this audit immediately** upon encountering any new project
2. **Adapt the framework** to project-specific needs and constraints
3. **Prioritize quick wins** that provide immediate value to users and AI assistants
4. **Document decisions** about content placement for future reference
5. **Validate with real users** to ensure documentation serves intended audiences effectively

This framework ensures your documentation structure serves both human users seeking quick onboarding and AI assistants requiring comprehensive technical context for complex development tasks.
