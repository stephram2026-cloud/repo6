# fgilywv4 — evidence for the answer key (taiga-back @ 8ab6a4e3)

All file:line references are at the pinned commit `8ab6a4e3b5f6fbbfcbf108a6449011f07b7308aa`.
Every bug below was reproduced over the HTTP API on a fresh instance (gunicorn 4 workers + Postgres 16),
with low-privilege roles and two projects with different owners where that matters. "proof" is a re-runnable
script under `/root/johto-task4/<L*>/scratch/...`.

Scope note: the opening prompt names memberships, roles, project settings, stories/tasks/sprints, issues and
epics. The bugs below are inside those areas. Tag and attachment bugs are listed separately at the end and are
NOT counted in the in-scope key (per Review 1).

Score on the in-scope key: see SCORE.md. This file gives setup / expected / actual for the bugs the model
MISSED and for the one real bug it WITHDREW, which are the ones Review 1 asked to see; the bugs it FOUND are
listed in SCORE.md with their file:line and proof path.

================================================================================
PART A — the real bug the model withdrew in turn 2
================================================================================

## W1  Task reorder ignores the user story, so reordering a task in one story renumbers a task in a sibling story
- area: tasks
- where: taiga/projects/tasks/api.py:258 passes `user_story_id=data["us_id"]`, but the client sends
  `user_story_id` while the validator field is `us_id` (taiga/projects/tasks/validators.py:39-40, 65-71);
  the taskboard/us order service filters only by status/milestone, never by the story.
- setup: one project; story1 with tasks aX, aY; story2 (same status) with tasks bX, bY. As a member,
  POST /api/v1/tasks/bulk_update_taskboard_order with the ids of story1's tasks in reversed order.
- expected: only story1's tasks are renumbered; story2's order is untouched.
- actual: story2's tasks are renumbered too — observed order of story2 went `bX,bY` -> `bY,bX`. Same effect
  whether the key is sent as `us_id` or `user_story_id`, and for both taskboard_order and us_order.
- proof: /root/johto-task4/L3/scratch/verify1/c08.py  (verdict TRUE in /root/johto-task4/L3/VERIFY-LANE-T1.md)
- why it matters for the score: the model reported this in turn 1, then in turn 2 ran a single case that did
  not trigger it and withdrew it as "no visible effect". It is a real bug, so the withdrawal is a mistake.

================================================================================
PART B — in-scope bugs the model never reported (the "missed" count)
================================================================================

## M1  Deleting a status with moveTo pointing at another project's status corrupts data across projects
- area: project settings (statuses)
- where: taiga/projects/mixins/on_destroy.py:35 `get_object_or_404(self.model, id=move_to)` (id only, no
  same-project check); line 45 `qs.update(**{field: move_item})`.
- setup: projects A and B owned by the same user. Delete an IssueStatus in A with `?moveTo=<a status id in B>`.
- expected: 400/404, or the moveTo restricted to A's own statuses.
- actual: 204; A's issues now point at a status row that belongs to B.
  `issue in project A now has status id 557 which belongs to project 80 but the issue's project is 79`
- proof: /root/johto-task4/L3/scratch/proofs/p02_moveto_crossproject.py

## M2  Deleting a status with moveTo leaves every derived field stale (is_closed, finished dates, sprint closed)
- area: project settings (statuses) / stories / tasks / sprints
- where: taiga/projects/mixins/on_destroy.py:45 moves rows with `queryset.update()`, which does not run the
  signals that set is_closed / finish_date / the sprint closed flag.
- setup: a story/task/issue in an "open" status that is deleted with moveTo -> a "closed" status.
- expected: the item becomes closed with a finish date and the sprint recloses, same as editing it by hand.
- actual: `task is_closed=False finished_date=<set wrongly> its US is_closed=True`;
  `issue is_closed=True finished_date=None milestone.closed=False`; control single PATCH sets them correctly.
- proof: /root/johto-task4/L1/scratch/r2/r2a03_status_delete_moveto_derived.py

## M3  Flipping is_closed on a task status or issue status does not update finished dates or sprint closure
- area: project settings (statuses) / tasks / issues / sprints
- where: issue statuses have no is_closed change handler at all; the task handler only re-evaluates the parent
  user story.
- setup: flip a task status / issue status to is_closed=true after items already use it.
- expected: those items get a finished date and their sprint recloses.
- actual: `task is_closed=True milestone.closed=False`; `issue is_closed=True finished_date=None sprint closed=False`;
  `issues_stats closed_issues=1 but by_open_closed closed today=0`.
- proof: /root/johto-task4/L1/scratch/r2/r2a04_status_flag_flip.py

## M4  Role points of the last role made non-computable are never removed
- area: roles / points
- where: update_role_points early-returns when no computable roles remain, leaving the stale RolePoints.
- setup: make the last computable role non-computable, then read the story points and project stats.
- expected: total points become None / {}.
- actual: `US total_points = 2.0 points = {'721': 1434} (expected None / {})`; clearing the estimate 400s with
  `Invalid role id '721'`.
- proof: /root/johto-task4/L1/scratch/r2/r2a05_last_computable_role.py

## M5  Deleting the last item of a closed sprint leaves an empty sprint flagged closed
- area: sprints
- setup: close a sprint (all items closed), then delete its last item.
- expected: the empty sprint is no longer flagged closed, consistent with moving the item out (which reopens it).
- actual: `sprint A: user_stories=0 closed=True` while the control `sprint B` reopens to closed=False;
  the closed-sprint header count is wrong too.
- proof: /root/johto-task4/L1/scratch/r2/r2a06_empty_milestone_stays_closed.py

## M6  Concurrent likes leave Project.total_fans below the real number of fans
- area: project (likes) — in scope as a project counter
- where: add_like/remove_like recount and write total_fans with no row lock / F() (taiga/projects/likes/services.py:16-34).
- setup: 4 users like a project at the same instant, 15 rounds.
- expected: total_fans == number of fans.
- actual: `fans list has 4 users but project.total_fans=3` (and 1); `15/15 rounds ended with total_fans != number of fans`.
- proof: /root/johto-task4/L1/scratch/r2/r2a07_like_race.py

## M7  Concurrent downvotes by one user corrupt the vote counter (and can 500)
- area: issues/stories votes — in scope as an item counter
- where: taiga/projects/votes/services.py:52-60 decrements `count = F('count') - 1` OUTSIDE the advisory lock
  (add_vote at line 30 is inside it).
- setup: one user fires 2 downvotes at the same instant, 30 rounds.
- expected: total_voters matches the voters list; never negative.
- actual: `voters list has 1 user(s) but total_voters=0`; `23/30 rounds ended with total_voters != number of voters`.
- proof: /root/johto-task4/L1/scratch/r2/r2a08_downvote_race.py

## M8  Membership limit is a lock-free TOCTOU; concurrent invites exceed the owner's limit
- area: memberships
- where: taiga/projects/api.py:1024 `_check_if_new_member_can_be_created` + 1161 save, no advisory lock on the
  single-create path (the bulk path has one).
- setup: owner with max_memberships=3; fire 8 single invitations at the same instant.
- expected: at most the limit is created.
- actual: `statuses: [201,201,201,201,400,400,400,400] total memberships in project (limit was 3): 5`.
- proof: /root/johto-task4/L3/scratch/proofs/p05_limit_race.py

## M9  bulk_create raises an uncaught IntegrityError (500) when the same user is invited by username and email
- area: memberships
- where: taiga/projects/validators.py (MembersBulkValidator) misses the user-level collision; only
  exc.ValidationError is caught at taiga/projects/api.py:1048-1088.
- setup: POST memberships/bulk_create with the same existing user by username and by their email.
- expected: 400.
- actual: `bulk same existing user by username+email: 500 {"error": "Server application error"}`.
- proof: /root/johto-task4/L3/scratch/proofs/p06_bulk_dup_500.py

## M10  Removing a member leaves their NotifyPolicy, so an ex-member keeps receiving notifications
- area: memberships
- where: taiga/projects/signals.py:22-23 membership_post_delete only calls update_role_points; the NotifyPolicy
  is not removed, so project.get_watchers() still includes the user.
- setup: remove a member who had a notify policy; read the project watchers.
- expected: the ex-member is no longer a watcher.
- actual: `is in project watchers (gets notifications): True`.
- proof: /root/johto-task4/L3/scratch/proofs/p07_exmember_watcher.py

## M11  A sprint can be moved into another project via PATCH project
- area: sprints
- where: MilestoneValidator (taiga/projects/milestones/validators.py:29-32) leaves `project` writable;
  the permission is checked only against the sprint's current project (member-level modify_milestone).
- setup: member of A PATCHes one of A's sprints with `{"project": <B id>}`.
- expected: rejected.
- actual: `PATCH milestone.project -> B(victim) -> HTTP 200 ... milestone 63`.
- proof: /root/johto-task4/L2/scratch/r2/r2b02b_more.py

## M12  Object history is readable with only view_project, bypassing per-item view permissions
- area: issues/stories/epics (activity) — in scope
- where: HistoryViewSet has no object-level permission filter; the history endpoints require only view_project.
- setup: anonymous / a role without view_us reads /history/userstory/<id> for a private item.
- expected: 401/403.
- actual: `ANON GET /userstories/140 -> 401` but `ANON GET /history/userstory -> 200 entries: 2`, leaking the
  subject diff and an internal comment ("internal comment leak-me").
- proof: /root/johto-task4/L2/scratch/r2/r2b05_history_leak.py

## M13  The role filter returns every row when nobody holds the role
- area: stories / tasks / issues (filters)
- setup: filter a list by a role that has no members: `?role=Design`.
- expected: no rows (nobody is assigned via that role).
- actual: returns all rows: `?role=Design (0 members) -> ['task of m', 'task unassigned']`.
- proof: /root/johto-task4/L1/scratch/r2/r2a13_role_filter_empty_role.py

## M14  The swimlane filter on the user story list is silently ignored (misspelled "swimnlane")
- area: stories / swimlanes (filters)
- where: taiga/projects/userstories/filters.py:34 `param_name = "swimnlane"`.
- setup: `GET /userstories?swimlane=<id>`.
- expected: only stories in that swimlane.
- actual: the filter is ignored (`?swimlane=A -> ['in A','in B']`); only the misspelled `?swimnlane=A` works.
- proof: /root/johto-task4/L1/scratch/r2/r2a14_swimlane_filter_typo.py

## M15  Malformed filter values return HTTP 500 instead of 400
- area: stories / tasks / issues (filters)
- setup: realistic bad query values from a client.
- expected: 400 Bad Request.
- actual: `500 ...status__is_closed=yes`, `500 ...closed=no`, `500 ...order_by=epic_order`, `500 ...epic=abc`
  (one case, milestone=abc, is correctly 400).
- proof: /root/johto-task4/L1/scratch/r2/r2a15_filter_500.py

## M16  User-story "points" sent as a non-dict value raises an uncaught 500
- area: stories
- where: RolePointsField.from_native does not guard a string/number value.
- setup: PATCH a story with `points` set to `"notjson"`, `"[1,2"`, or `123`.
- expected: 400.
- actual: each returns `500 {"error": "Server application error"}`.
- proof: /root/johto-task4/L1/scratch/p08_points_500.py

================================================================================
PART C — tag and attachment bugs (OUT of the in-scope key per Review 1; listed for completeness)
================================================================================

The model FOUND these in turn 4; they are excluded from the in-scope score because the prompt does not name
tags or attachments. Proof scripts: /root/johto-task4/L2/scratch/proofs/explore4_tags.py,
/root/johto-task4/L2/scratch/r2/r2b04_attach_move.py, r2a09_tags_colors_race.py, r2a10_move_project_attachments.py.
