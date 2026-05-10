# Deployment & Infrastructure Skill

## Objective
Safely package, tag, and deploy validated codebase artifacts to staging and production environments, ensuring zero downtime and strict environment isolation.

## Execution Constraints
- Containerization First: All builds must be executed via the Docker MCP Server. Local host environment dependencies are strictly prohibited.
- Secret Management: Hardcoding environment variables or secrets into Dockerfiles or deployment scripts is a critical offense. All secrets must be injected at runtime via secure environment contexts.
- UAT Trigger: Upon successful deployment to the staging environment, you MUST explicitly invoke the Render MCP to trigger the User Acceptance Testing (UAT) phase and notify the executive channel.

## Mandatory Deployment Pipeline
1. Image Build & Tag: Utilize the Docker MCP to build the image, tagging it strictly with the current sprint version and Git commit hash.
2. Container Provisioning: Spin up the containerized environment.
3. Health Verification: Execute mandatory health-check validations against the primary application endpoints. The deployment is not complete until a `200 OK` is returned from the health route.
4. UAT Escalation: Trigger the Render MCP to finalize the staging rollout and signal readiness for human review.

## Output Format
Return an explicit deployment status:
- ### 🟢 [DEPLOYMENT SUCCESSFUL]: Image tagged. Health checks passed. Render MCP triggered for UAT.
- ### 🔴 [DEPLOYMENT FAILED]: Execution halted. Provide the exact Docker build log or health-check failure trace.