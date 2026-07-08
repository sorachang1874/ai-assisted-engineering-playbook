# References

Primary and official references used to calibrate this playbook.

## AI Coding Agents

- OpenAI Codex `AGENTS.md` documentation: https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex repository `AGENTS.md` docs pointer: https://github.com/openai/codex/blob/main/docs/agents_md.md
- OpenAI Codex product overview: https://openai.com/index/introducing-codex/
- Anthropic Claude Code overview: https://docs.anthropic.com/en/docs/claude-code/overview
- Anthropic Claude Code best practices: https://code.claude.com/docs/en/best-practices
- Anthropic Claude Code engineering best-practices post: https://www.anthropic.com/engineering/claude-code-best-practices

## Durable Execution and Workflow Architecture

- Temporal documentation: https://docs.temporal.io/
- Temporal durable execution technical guide: https://assets.temporal.io/durable-execution.pdf
- Microsoft CQRS pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
- Microsoft Event Sourcing pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing

## Model Safety, Output, and Evaluation

- OWASP Top 10 for LLM Applications: https://genai.owasp.org/llm-top-10/
- Anthropic responsible use / safety guidance: https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails
- OpenAI safety best practices: https://platform.openai.com/docs/guides/safety-best-practices
- OpenAI evals: https://github.com/openai/evals

## Configuration and Secrets

- The Twelve-Factor App (config): https://12factor.net/config
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

## Testing and CI

- Testcontainers getting started: https://testcontainers.com/getting-started/
- Testcontainers best practices: https://www.docker.com/blog/testcontainers-best-practices/
- Docker/Testcontainers Java guide: https://docs.docker.com/guides/testcontainers-java-getting-started/run-tests/
- GitHub Actions workflow syntax and schedules: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- Martin Fowler on Continuous Integration: https://martinfowler.com/articles/continuousIntegration.html

## Agent Loops, Model Composition, and Harness Self-Improvement

- Claude Code team loop-design guide (2026) — the four loop types (interactive, goal-driven,
  scheduled, event-driven): https://code.claude.com/docs/en/agents,
  https://code.claude.com/docs/en/goal, https://code.claude.com/docs/en/routines,
  https://code.claude.com/docs/en/workflows
- Anthropic advisor/orchestrator (managed-agents) cost-composition guidance, and the
  claude-cookbooks notebook `managed_agents/CMA_plan_big_execute_small.ipynb` (2026):
  https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/CMA_plan_big_execute_small.ipynb
- Lilian Weng, "Harness Engineering for Self-Improvement" (2026-07-04):
  https://lilianweng.github.io/posts/2026-07-04-harness/
- Trehan & Chopra, failure modes of autonomous research/engineering agents (2026; via Weng
  2026-07-04): https://arxiv.org/abs/2601.03315
- Bubeck et al., on overclaiming from noisy or failed results ("p-hacking eureka") (2025):
  https://arxiv.org/abs/2511.16072

