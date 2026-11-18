# fgilywv4 — Task Success accounting

The model's final list (turn 5) had 40 rows. Below each is mapped to the proved key. A bug counts as FOUND if
the model mentioned it at all, even as "Read" (not run) or inside a grouped row; otherwise MISSED. Tag and
attachment bugs are listed last and are NOT in the in-scope totals (Review 1: the prompt does not name them).

## In-scope bugs the model FOUND (29)

| # | bug | area | file:line | proof |
|---|-----|------|-----------|-------|
| 1 | generated_from_issue/task cross-project leak + injected comment | stories | userstories/validators.py:57; userstories/api.py:186,289 | L1/scratch/p07_generated_from_issue.py |
| 2 | epic related-US: permission on the body epic, row saved on the URL epic | epics | epics/api.py:227-229 | L2/scratch/proofs/explore1.py |
| 3 | epic related-US accepts a US the caller cannot see | epics | epics/api.py | L2/scratch/proofs/explore2.py |
| 4 | epic related-US list has no permission filter (anon can read id pairs) | epics | epics/api.py:211 | L3/scratch/verify1/c01.py |
| 5 | view-only member can promote a task (deletes task, creates US) | tasks | tasks/permissions.py:32; mixins/promote.py:31 | L1/scratch/p01_promote_perm.py |
| 6 | promote checks permission on the body project_id, not the object's project | tasks | mixins/promote.py:31-32 | L1/scratch/p01_promote_perm.py |
| 7 | issue promote requires add_us but checks it in the wrong project | issues | issues/permissions.py:33 | L1/FINDINGS.md L1-01 |
| 8 | modify_epic alone can create user stories via bulk_create | epics | epics/api.py:181-187 | L3/scratch/verify1/c15.py |
| 9 | US moved into another project's sprint via move_userstories_to_sprint | sprints | milestones/validators.py:41; milestones/api.py | L3/scratch/verify1/c02.py |
| 10 | bulk-created issues accept a sprint id from any project | issues | issues/validators.py:36 | L2/scratch/proofs (bulk) |
| 11 | sprint closed flag stale after bulk_update_milestone | sprints | userstories/services.py:236-237 | L1/scratch/p06_milestone_closed_not_recalc.py |
| 12 | bulk-created stories in a closed status are not marked closed | stories | userstories/services.py:77-83 | L1/scratch/p04_bulk_create_us_isclosed.py |
| 13 | bulk-created closed tasks get no finished date | tasks | tasks/services.py:65-70 | L1/scratch/p05_bulk_create_task_finished_date.py |
| 14 | task bulk-move desyncs a task from its story's sprint | tasks | userstories/services.py:434 | L1/scratch/p09_task_milestone_desync.py |
| 15 | two users saving the same item lose one change, no error | stories/tasks/issues/epics/sprints | occ/mixins.py:41-44; notifications/mixins.py:93 | L1/scratch/r2/r2a01_lost_update.py |
| 16 | project admin seizes ownership via writable transfer_token | project/memberships | validators.py:300; services/transfer.py:47 | L3/scratch/proofs/p01_transfer_token.py |
| 17 | deleting a role without moveTo cascade-deletes members incl. owner | roles | users/api.py:487-491; models.py:74-79 | L3/scratch/proofs/p03_role_delete_no_moveto.py |
| 18 | settings/role rows re-parented into another project via PATCH project | project settings/roles | validators.py:63-127; users/validators.py:99-104 | L3/scratch/proofs/p08_role_move_project.py; L2/scratch/r2/r2b02_project_move.py |
| 19 | project admin can un-archive a staff-archived project (archived_code writable) | project | validators.py:293-300 | lane turn1 item 15 (read); confirmed writable |
| 20 | blocked/archived projects writable via bulk & action routes | project settings/sprints | on_destroy/bulk services; routes miss the guard | L1/scratch/r2/r2a11_blocked_archived_bypass.py |
| 21 | Taiga-Info-* list headers leak private backlog/sprint counts | sprints/stories | userstories/api.py:154; milestones/api.py:75 | L1/scratch/r2/r2a02_info_headers.py |
| 22 | assigned_users bypasses the project-membership check assigned_to enforces | stories | mixins/validators.py (no assigned_users check) | L2/scratch/r2/r2b01_assigned_users.py |
| 23 | every assignee re-notified on each assigned_users change | stories | notifications/mixins.py:404 | L3/scratch/verify1/c17.py |
| 24 | moving a story to another project leaves its tasks behind | stories/tasks | (cross-project move) | L1/scratch/p03_us_crossproject_tasks.py |
| 25 | bulk invite of an existing member 500s on the DB constraint | memberships | validators.py:283; api.py:1048-1088 | L3/scratch/proofs/p06_bulk_dup_500.py |
| 26 | editing a membership can hand it to a different account (invite email) | memberships | api.py:1164 | L3/scratch/verify1/c07.py |
| 27 | project duplication counts the wrong privacy limit | project | services/projects.py:183 | L3/scratch/verify1/c09.py |
| 28 | nested data returns items without per-type view permission | stories/tasks | milestones/serializers.py:33; userstories/utils.py:60 | L3/scratch/verify1/c03.py,c04.py,c05.py |
| 29 | uncapped sprint-stats date loop (huge range -> hang/500) | sprints | milestones/api.py:129; models.py:171 | L3/scratch/verify1/c14.py |

## In-scope bugs the model MISSED (15) — full setup/expected/actual in EVIDENCE.md

M1 status delete with cross-project moveTo; M2 stale derived state after status delete; M3 stale state after
status is_closed flip (issue statuses have no handler); M4 role points of the last computable role;
M5 empty sprint stays closed; M6 like counter race; M7 vote counter race (+500); M8 membership-limit race;
M10 removed member keeps NotifyPolicy (still a watcher); M11 sprint re-parented via PATCH project;
M12 history readable with only view_project; M13 role filter returns all when nobody holds the role;
M14 swimlane filter ignored (misspelled param); M15 malformed filter values 500; M16 "points" non-dict 500.

Plus one real bug WITHDRAWN after an inconclusive test: W1 task reorder ignores the user story (EVIDENCE.md Part A).

## Totals (in scope)
- Found: 29 of 44 (66%).
- Missed and not flagged: 15.
- Of the model's own top 7 ("Stop before rollout"), 5 were never run (only read).
- One real bug was withdrawn.

Task Success 3 ("completed but with notable problems"): a large, accurate set of real bugs, but a third of the
in-scope key missed with no mention, most of the highest-ranked items never executed, and a real bug withdrawn.
Not 4 (more than minor problems); not 2 (far more than a partial result).

## Out of scope (tags & attachments) — found by the model in turn 4, not in the totals above
Tag duplication by case; tag merge-on-rename overwrites colour; tags_colors lost under concurrent saves;
attachment re-parented onto another project's item; attachment left behind on cross-project move; comment-only
member uploads a regular attachment; replacing a file keeps old name/size. Proofs under L2/scratch.
