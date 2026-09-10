---
title: "Roles & Permissions"
headingId: "roles--permissions"
---

Set permissions when sharing models, knowledge bases, or prompts so the intended faculty, students, or staff can view, use, and edit them. The sections below distinguish account roles from the visibility settings on individual resources.

---

## How Roles Work

Open WebUI has three account roles — **Admin**, **User**, and **Pending**. Individual access lets you use resources shared by the CUNY AI Lab; it does not automatically include **Workspace** access for creating configurations.

### Administrators
Administrators configure the model connection, manage users and groups, install tools, and set defaults for the Sandbox.

### Faculty / Staff
Faculty and staff can request **Workspace** access by emailing the [CUNY AI Lab team](mailto:ailab@gc.cuny.edu) to create and share models, knowledge bases, and prompts. Approved courses receive a group automatically; contact the Lab if its membership or permissions need attention.

### Students
Students join through their instructor’s invitation and use resources shared with their course group. Creating private configurations and editing shared resources require the corresponding permissions.

A **Pending** account cannot use the main platform until activated.

---

## Visibility Settings

Use the resource’s access controls to choose its audience.

1. **Private** — available to you and any users or groups added through **Add Access**. With no access grants, it stays private to you.
2. **Public** — available to all signed-in Sandbox users, where your account permits public sharing.

Administrators may also access resources for platform management.

### Setting Visibility

1. Create or edit a resource (model, knowledge base, or prompt)
2. Open **Access** or the access controls shown in the editor
3. Keep **Private** for course materials and choose **Add Access**
4. Select your course group and grant **Read** access; grant **Write** only to collaborators who should edit
5. Save the resource if the editor shows a save button

> **Tip.** Build and test resources with Private visibility, then share them when they are ready for students.

---

## Working with Groups

Share a resource with a course group, such as "ENG 2100 Fall 2026", to grant access to its 30 students through one group setting.

### Creating a Group (Admin)

1. Go to **Admin Panel > Users**
2. Select **Groups**
3. Choose **Create Group**
4. Name the group
   - Use a recognizable name, such as the course code and term, research team, or department
5. Add members
6. Click **Save**

### What Groups Enable

When you share a resource with a group
- Members gain the access granted to their group.
- New members receive that group access.
- Removing a member removes access granted through that group; other grants may still apply.

---

## Advanced Settings

<details>
<summary>View details</summary>

### SCIM 2.0 Provisioning

Open WebUI supports SCIM 2.0 for identity-provider provisioning when administrators configure it. For Sandbox courses, use the course invitation and **My classes** process described in [Student Onboarding](student-onboarding.md); a registrar roster change alone is not confirmation of Sandbox enrollment or removal.

### Permission Inheritance

Administrators set default user permissions and group permissions. Group grants are additive, so a user may retain access through another group or a direct grant after leaving one group.

</details>

---

## Callout

<div class="callout">
  <strong>For instructors.</strong> Approved Sandbox courses automatically receive a private course group and text channel. Confirm access to your course group, then share the course models and knowledge bases with it before the first class.
</div>

---

## Additional Resources

- [Open WebUI User Management](https://docs.openwebui.com/features/authentication-access/rbac/) — official documentation for roles, groups, and SCIM provisioning
- [CUNY IT Policies](https://www.cuny.edu/about/administration/offices/cis/it-policies/) — institutional guidelines for data access and user management

---

[← Return to Tools & Skills](tools-skills.md) | [Teaching Tips →](teaching-tips.md)
