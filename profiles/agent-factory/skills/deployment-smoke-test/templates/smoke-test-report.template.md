# {{project_name}} Smoke Test Report

**Test Date**: {{test_date}}
**Test Environment**: {{test_environment}}
**Deployment Mode**: {{deployment_mode}} <!-- Local | Container -->
**Commit Tested**: {{git_commit}}

---

## Execution Summary

| Metric | Status |
|------|------|
| Total Test Phases | {{total_phases}} |
| Passed Phases | {{passed_stages}} |
| Failed Phases | {{failed_stages}} |
| Overall Conclusion | **{{overall_status}}** |

### Key Test Cases

| Case | Result | Details |
|------|--------|---------|
| Code update check | {{case_code_update}} | {{case_code_update_details}} |
| Environment check | {{case_env_check}} | {{case_env_check_details}} |
| Configuration preparation | {{case_config_prep}} | {{case_config_prep_details}} |
| Deployment | {{case_deploy}} | {{case_deploy_details}} |
| Health check | {{case_health_check}} | {{case_health_check_details}} |
| Route/page smoke checks | {{case_route_checks_overall}} | {{case_route_checks_details}} |

---

## Detailed Test Results

### Phase 1: Code Update Check

- [x] Confirm project root — {{status_dir_check}}
- [x] Check Git status — {{status_git_status}}
- [x] Pull latest code — {{status_git_pull}}
- [x] Confirm code update — {{status_git_verify}}

**Phase Status**: {{stage1_status}}

---

### Phase 2: Environment Check

<!-- Rows below are discovered per-project in Phase 0 of
 references/smoke-test-sop.md — delete/add rows to match what was
 actually checked for this repo instead of assuming a fixed tool list. -->

| Tool/Dependency | Required version (if any) | Status |
|---|---|---|
| {{tool_1_name}} | {{tool_1_required_version}} | {{tool_1_status}} |
| {{tool_2_name}} | {{tool_2_required_version}} | {{tool_2_status}} |
| {{tool_3_name}} | {{tool_3_required_version}} | {{tool_3_status}} |

- [x] Port availability — {{status_port_check}}

**Phase Status**: {{stage2_status}}

---

### Phase 3: Configuration Preparation

- [x] Main config file — {{status_config_file}}
- [x] Environment/secrets file — {{status_env_file}}
- [x] Mandatory settings populated — {{status_mandatory_settings}}

**Phase Status**: {{stage3_status}}

---

### Phase 4: Deployment

- [x] Dependency check — {{status_dep_check}}
- [x] Install — {{status_install}}
- [x] Start command — {{status_start}}
- [x] Startup wait / poll — {{status_wait_startup}}

**Phase Status**: {{stage4_status}}

---

### Phase 5: Service Health Check

- [x] Process/container status — {{status_processes}}
- [x] Entrypoint reachable — {{status_entrypoint}}
- [x] Health endpoint — {{status_health_endpoint}}
- [x] Additional documented routes — {{status_additional_routes}}

**Phase Status**: {{stage5_status}}

---

### Route/Page Smoke Results

<!-- Populate rows for whatever routes were actually checked in this
 project (see scripts/route-check.sh) — don't assume a fixed set. -->

| Route | Status | Details |
|-------|--------|---------|
| {{route_1_path}} | {{route_1_status}} | {{route_1_details}} |
| {{route_2_path}} | {{route_2_status}} | {{route_2_details}} |
| {{route_3_path}} | {{route_3_status}} | {{route_3_details}} |

**Summary**: {{route_checks_summary}}

---

### Phase 6: Test Report Generation

- [x] Result summary — {{status_summary}}
- [x] Issue log — {{status_issues}}
- [x] Report generation — {{status_report}}

**Phase Status**: {{stage6_status}}

---

### Optional Functional Verification

<!-- Only fill in if this phase was actually run; otherwise delete this
 section rather than showing it as skipped, per SKILL.md Section 4's
 execution rules. -->

- [ ] {{optional_check_1_description}} — {{optional_check_1_status}}
- [ ] {{optional_check_2_description}} — {{optional_check_2_status}}

---

## Issue Log

### Issue 1
**Description**: {{issue1_description}}
**Severity**: {{issue1_severity}}
**Solution**: {{issue1_solution}}

---

## Environment Information

### Dependency Versions
```text
{{tool_versions_output}}
```

### Git Information
```text
Repository: {{git_repo}}
Branch: {{git_branch}}
Commit: {{git_commit}}
Commit Message: {{git_commit_message}}
```

### Configuration Summary
- Main config file exists: {{config_exists}}
- Environment/secrets file exists: {{env_exists}}
- Mandatory settings count / configured: {{mandatory_settings_summary}}

---

## Service Status

<!-- Rows correspond to whatever processes/containers this project
 actually runs — discovered in Phase 0.2 of smoke-test-sop.md. -->

| Service | Status | Endpoint |
|---------|--------|----------|
| {{service_1_name}} | {{service_1_status}} | {{service_1_endpoint}} |
| {{service_2_name}} | {{service_2_status}} | {{service_2_endpoint}} |
| {{service_3_name}} | {{service_3_status}} | {{service_3_endpoint}} |

---

## Recommendations and Next Steps

### If the Test Passes
1. [ ] Visit {{entrypoint_url}} to confirm the deployment manually.
2. [ ] Configure any optional settings not covered by this smoke test.
3. [ ] Note anything worth documenting for the next run.

### If the Test Fails
1. [ ] Check `references/troubleshooting.md` for the matching symptom
 category.
2. [ ] Check local/container logs: {{log_locations}}
3. [ ] Verify configuration file format and content.
4. [ ] If needed, fully reset the environment using the project's own
 documented stop/clean/reinstall/start sequence.

---

## Appendix

### Full Logs
{{full_logs}}

### Tester
{{tester_name}}

---

*Report generated at: {{report_time}}*
