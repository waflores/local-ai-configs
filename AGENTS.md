# Llama-Swap + Continue.dev Configuration Agents

## 🤖 Project Agents & Responsibilities

This document defines the agents (humans and AI) involved in this configuration journey, their roles, and how they collaborate.

## 👥 Human Agents

### Lead Developer (Will)

**Role:** Primary researcher and configuration architect

**Responsibilities:**

- Define project vision and goals
- Select appropriate models for specific use cases
- Configure llama-swap and continue.dev settings
- Benchmark and evaluate performance
- Document findings and iterate on configurations

**Key Skills:**

- Deep understanding of LLM inference
- Proficiency in Python, C, C++
- Experience with CUDA and Vulkan APIs
- Strong documentation practices

### Research Assistant

**Role:** Technical research and experimentation

**Responsibilities:**

- Investigate llama-swap configuration options
- Research continue.dev best practices
- Experiment with different model combinations
- Document technical deep-dives
- Provide recommendations for optimization

**Key Skills:**

- Research methodology
- Technical writing
- Performance analysis
- Configuration experimentation

## 🤖 AI Agents

### ⚠️ Rules of Engagement

**DO:**

- ✅ **Always document** every configuration change with clear reasoning
- ✅ **Prioritize data-driven decisions** - benchmark before committing to major changes
- ✅ **Communicate clearly** - explain technical trade-offs to the Lead Developer
- ✅ **Respect resource constraints** - never recommend configurations that exceed hardware limits
- ✅ **Track performance metrics** - collect data for every experiment
- ✅ **Learn from failures** - document what doesn't work and why
- ✅ **Stay within scope** - focus on llama-swap + continue.dev integration
- ✅ **Use quantization** - prefer Q4_K_M or Q5_K_M for balance between quality and size
- ✅ **Prefer CUDA over Vulkan** for active models (better performance)
- ✅ **Use Vulkan for swapped models** (free up VRAM for active models)

**DON'T:**

- ❌ **Don't make assumptions** about model compatibility without testing
- ❌ **Don't ignore error messages** - they often contain crucial clues
- ❌ **Don't over-optimize** early iterations - get basic functionality first
- ❌ **Don't recommend loading too many models** simultaneously (VRAM constraints)
- ❌ **Don't forget to document** benchmark results
- ❌ **Don't change multiple configuration variables** at once (hard to debug)
- ❌ **Don't ignore context window requirements** - some models need larger contexts
- ❌ **Don't use Q2_K or Q3_K** unless specifically needed (better quality with Q4_K_M)
- ❌ **Don't forget security** - never expose API keys or sensitive data
- ❌ **Don't skip iteration logs** - they're invaluable for future reference

### Configuration Analyst

**Role:** Analyze and recommend llama-swap configurations

**Capabilities:**

- Parse hardware specifications
- Recommend model loading strategies
- Analyze resource utilization patterns
- Suggest quantization optimizations

**Tools:**

- Hardware monitoring utilities
- llama-server diagnostics
- Resource usage analyzers

### Performance Benchmarking Agent

**Role:** Measure and compare model performance

**Capabilities:**

- Run speed tests for different models
- Measure swap operation timings
- Analyze memory usage patterns
- Generate performance reports

**Metrics Tracked:**

- Tokens per second
- Model load time
- Swap operation latency
- Memory footprint
- Context window efficiency

### Documentation Agent

**Role:** Maintain and update project documentation

**Capabilities:**

- Write technical deep-dives
- Create quick-start guides
- Document iteration logs
- Generate configuration examples

**Output Formats:**

- Markdown documentation
- Configuration templates
- Troubleshooting guides
- Best practices compilations

### Code Analysis Agent

**Role:** Analyze code generation quality

**Capabilities:**

- Evaluate generated code quality
- Check for syntax errors
- Verify best practices compliance
- Suggest improvements

**Evaluation Criteria:**

- Syntax correctness
- Code style adherence
- Security considerations
- Performance optimization

## 👥 Human Agent Guidelines

### Lead Developer Rules

**DO:**

- ✅ **Approve configuration changes** thoughtfully - consider long-term impact
- ✅ **Review benchmark results** before making major decisions
- ✅ **Balance performance with practicality** - don't over-optimize prematurely
- ✅ **Encourage experimentation** - allow research to explore new options
- ✅ **Make timely decisions** - don't let analysis paralysis stall progress
- ✅ **Document decisions** - explain the reasoning behind major choices

**DON'T:**

- ❌ **Don't change configurations** without understanding the rationale
- ❌ **Don't micromanage** - trust the research and benchmarking process
- ❌ **Don't ignore practical constraints** - keep hardware limits in mind
- ❌ **Don't make decisions** without reviewing benchmark data
- ❌ **Don't skip documentation** - decisions need to be recorded for future reference

### Research Assistant Rules

**DO:**

- ✅ **Explore multiple options** before recommending changes
- ✅ **Research thoroughly** - don't make assumptions about compatibility
- ✅ **Document findings** - even negative results are valuable
- ✅ **Provide benchmarks** - always include data with recommendations
- ✅ **Suggest alternatives** - offer fallback options when primary choice fails

**DON'T:**

- ❌ **Don't recommend** configurations without testing them first
- ❌ **Don't ignore** existing documentation - check what's already known
- ❌ **Don't overcomplicate** solutions - start simple, optimize later
- ❌ **Don't forget** to note resource implications of suggestions

### General Team Communication Rules

**DO:**

- ✅ **Be explicit** - always state your reasoning clearly
- ✅ **Ask questions** - don't hesitate to clarify requirements
- ✅ **Provide context** - explain why something matters
- ✅ **Be honest** - admit when you don't know something
- ✅ **Be concise** - get to the point quickly
- ✅ **Be thorough** - don't skip important details

**DON'T:**

- ❌ **Don't make assumptions** - always confirm requirements
- ❌ **Don't skip steps** - follow the process consistently
- ❌ **Don't ignore errors** - they often contain valuable information
- ❌ **Don't work in isolation** - communicate with the team
- ❌ **Don't forget to update** documentation after changes

## 🔄 Collaboration Workflow

### Configuration Iteration Cycle

```mermaid
┌─────────────────────────────────────────────────────────────┐
│                    Configuration Cycle                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. [Lead] Define requirements                               │
│     └─► Identify use case, models needed, performance goals │
│                                                             │
│  2. [Research] Analyze options                               │
│     └─► Research configurations, benchmark alternatives     │
│                                                             │
│  3. [Lead] Configure system                                  │
│     └─► Update llama-swap, continue.dev settings            │
│                                                             │
│  4. [Benchmark] Test performance                             │
│     └─► Run benchmarks, measure metrics                     │
│                                                             │
│  5. [Documentation] Record results                           │
│     └─► Update docs, write iteration log                    │
│                                                             │
│  6. [Review] Evaluate outcomes                               │
│     └─► Lead reviews, decides next steps                    │
│                                                             │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Decision Making Process

#### Level 1 - Quick Decisions (Immediate)

- Model selection for specific tasks
- Context window sizing
- Temperature settings
  **Agents:** Research + Lead approval

## Level 2 - Medium Decisions (Short-term)

- Model swapping strategies
- Resource allocation changes
- Quantization level adjustments
  **Agents:** Research + Benchmark + Lead approval

## Level 3 - Major Decisions (Long-term)

- Backend selection (llama.cpp vs vLLM)
- Architecture changes
- Significant resource reallocation
  **Agents:** All agents + Lead decision

## 🎯 Agent Communication Channels

### Documentation Updates

- **README.md:** Project vision, goals, roadmap
- **AGENTS.md:** This file - agent roles and workflow
- **Iteration Logs:** What was tried and results
- **Configuration Files:** Actual llama-swap settings
- **SKILL.md:** AI agent commands and capabilities (see [Skill File Locations](#skill-file-locations))

### Intent Layer Files

The `.continue/` directory serves as the **intent layer**, capturing institutional knowledge that isn't visible in code:

- **System boundaries and ownership** - What each agent owns and doesn't own
- **Invariants and contracts** - Configuration patterns that must hold
- **Patterns to follow / anti-patterns to avoid** - Best practices and pitfalls
- **Performance optimization strategies** - Resource management guidelines
- **Security considerations** - API key handling, model swapping safety

### Agent Tool Discovery

When agents need to find tools and information, they should search in this order:

1. **.continue/ directory** - Contains agent definitions, rules, and checks:

   - agents/ - Agent definitions (breaking-change-detector, dependency-security-review, error-message-quality, input-validation, test-coverage)
   - rules/ - Rule definitions for various coding standards and practices
   - checks/ - Quality checks (anti-slop, react-best-practices, security-audit, stale-comments, update-agents-md, update-continue-docs, setup-scripts)
   - prompts/ - Prompt templates and examples

1. AGENTS.md - Primary intent layer file with:

   - Agent roles and responsibilities
   - Configuration workflow definitions
   - Performance tracking targets
   - Collaboration guidelines

1. README.md - Project vision, goals, and roadmap

1. Iteration logs - Historical configuration changes and results

1. Configuration files - llama-swap and continue.dev settings

### Skill File Locations

continue.dev looks for SKILL.md files in the following locations:

1. Project Root Directory (Primary)

   ```text
   <project-root>/SKILL.md
   ```

1. Per-Project Configuration

   ```text
   <project-root>/.continue/config.json
   ```

1. Extension Package (for custom skills)

   ```text
   ~/.continue/packages/
   ```

**How Skills Work:**

- Create a SKILL.md file with markdown content

- Document commands using `## Commands` sections

- Example:

  ```text
  ## Commands

  - /benchmark
  - /swap-model
  - /config-analyze
  ```

- continue.dev parses the file and makes commands available in the chat interface

- Skills are automatically associated with the current project context

### Performance Reports

- **Benchmark Results:** Speed, latency, memory usage
- **Comparison Tables:** Model performance rankings
- **Resource Utilization:** VRAM, RAM, swap usage

### Technical Deep-Dives

- **Architecture Analysis:** How configurations work
- **Troubleshooting Guides:** Common issues and solutions
- **Optimization Tips:** Performance improvement strategies

## 📋 Agent Responsibilities Matrix

| Task | Lead | Research | Config | Benchmark | Doc |
| ---------------- | ---- | -------- | ------ | --------- | --- |
| Define vision | ✅ | | | | |
| Select models | ✅ | | | | |
| Configure system | ✅ | | ✅ | | |
| Run benchmarks | | | | ✅ | |
| Analyze results | ✅ | ✅ | | ✅ | |
| Write docs | | ✅ | | | ✅ |
| Make decisions | ✅ | | | | |

## 🚀 Agent Capabilities

### Lead Developer (AI)

- **Strategic:** Vision setting, goal definition
- **Technical:** Configuration, deployment
- **Evaluative:** Performance assessment, decision making

### Research Assistant (AI)

- **Investigative:** Configuration research, best practices
- **Analytical:** Performance analysis, comparison
- **Documentary:** Technical writing, deep-dives

### Configuration Analyst (Capabilities)

- **Hardware-aware:** GPU/CPU resource management
- **Model-aware:** Architecture understanding
- **Optimization:** Quantization, context management

### Documentation Analyst (Performance)

- **Writing:** Clear, concise documentation
- **Organization:** Structured information presentation
- **Maintenance:** Keeping docs current and accurate

## 🔄 Iteration Protocol

### Session Structure

**Pre-Session:**

1. Review previous iteration logs
1. Check performance benchmarks
1. Identify optimization opportunities

**During Session:**

1. Execute planned experiments
1. Collect performance data
1. Document findings immediately

**Post-Session:**

1. Update documentation
1. Write iteration log entry
1. Plan next session

### Documentation Standards

**Iteration Log Entries Must Include:**

- Date and session number
- Objective of this iteration
- Configuration changes made
- Performance metrics collected
- Issues encountered
- Lessons learned
- Next steps planned

**Technical Deep-Dive Requirements:**

- Clear problem statement
- Configuration details
- Expected vs actual results
- Analysis of findings
- Recommendations

**Benchmark Report Requirements:**

- Test setup description
- Models tested
- Metrics collected
- Comparison tables
- Performance rankings

## 📊 Performance Tracking

### Metrics Dashboard

| Metric | Target | Current | Status |
| --------------------- | -------- | ------- | ------ |
| Model Swap Time | < 2s | TBD | ⏳ |
| Generation Speed (7B) | > 10 t/s | TBD | ⏳ |
| VRAM Utilization | < 70% | TBD | ⏳ |
| Context Efficiency | > 80% | TBD | ⏳ |

### Benchmark Schedule

**Weekly:**

- Model swap timing tests
- Generation speed benchmarks
- Memory usage monitoring

**Monthly:**

- Full performance suite
- Model comparison analysis
- Configuration optimization

**Per Major Change:**

- Before/after comparison
- Impact assessment
- Regression testing

## 🎓 Knowledge Management

### Documentation Categories

1. **Configuration Guides**

   - llama-swap setup
   - continue.dev integration
   - Model loading strategies

1. **Performance Analysis**

   - Benchmark results
   - Model comparisons
   - Optimization tips

1. **Troubleshooting**

   - Common issues
   - Error resolutions
   - Debugging guides

1. **Best Practices**

   - Resource management
   - Model selection
   - Performance tuning

### Knowledge Sources

- Primary: This project documentation
- Secondary: llama-swap docs, continue.dev docs
- Tertiary: llama.cpp documentation, community forums

## 🌟 Success Criteria

### Individual Agent Success

**Lead Developer:**

- ✅ System configured and operational
- ✅ Performance meets targets
- ✅ Documentation comprehensive
- ✅ Iteration process effective

**Research Assistant:**

- ✅ Configuration options explored
- ✅ Best practices documented
- ✅ Performance analysis complete
- ✅ Recommendations actionable

**All Agents:**

- ✅ Clear communication maintained
- ✅ Documentation up-to-date
- ✅ Performance tracked
- ✅ Lessons captured

## 📈 Evolution Path

### Phase 1: Foundation (Current)

- Establish basic configuration
- Document initial setup
- Create benchmarking framework

### Phase 2: Optimization

- Refine model swapping strategy
- Optimize resource utilization
- Improve performance metrics

### Phase 3: Advanced

- Implement intelligent model selection
- Add multi-model support
- Enhance C/C++ optimizations

### Phase 4: Production

- Achieve production-ready configuration
- Document best practices
- Create deployment guides

## 🔄 Continuous Improvement

### Regular Review Cadence

**Daily:**

- Check performance metrics
- Update iteration logs
- Address immediate issues

**Weekly:**

- Review benchmark results
- Plan next experiments
- Update documentation

**Monthly:**

- Evaluate overall progress
- Review success criteria
- Plan major improvements

### Feedback Loops

**From Benchmarks → Configuration:**

- Performance data informs model selection
- Latency metrics guide optimization
- Memory usage patterns reveal bottlenecks

**From Documentation → Knowledge:**

- Iteration logs build expertise
- Deep-dives create reference material
- Troubleshooting guides help future sessions

Last updated: 2026
Status: Phase 1 - Foundation
Next milestone: First configuration iteration

AGENTS.md has 607 lines total.
