# Roles & Permissions

When you share a model, knowledge base, or prompt with students, you need to control who can use it, who can edit it, and who can see it. Roles and permissions give you that control. The Sandbox serves faculty, graduate students, undergraduates, and staff across multiple departments. Clear permissions prevent confusion and protect sensitive institutional data.

---

## How Roles Work

The Sandbox supports three role tiers:

### Administrators
Full platform access. Configure providers, manage users, install tools, set instance-wide defaults. Typically the AI Lab team and designated departmental contacts.

### Faculty / Staff
Create and share models, knowledge bases, and prompts. Manage their own groups. Cannot modify instance-wide settings or install tools.

### Students
Use shared resources. Create private configurations. Cannot modify shared resources unless explicitly granted access by a faculty member or administrator.

These roles map to CUNY's existing institutional hierarchy. Administrators can customize role definitions and permission boundaries through the Admin Panel.

---

## Visibility Settings

Every resource you create has a visibility setting:

1. **Private** — only you can see and use it
   - Good while you are building and testing
2. **Limited** — shared with specific users or groups you designate
   - The most common setting for course-specific resources
3. **Public** — available to all Sandbox users
   - Use for resources that serve the entire community (e.g., a quantitative methods model)

### Setting Visibility

1. Create or edit a resource (model, knowledge base, or prompt)
2. Look for the **Visibility** setting in the editor
3. Select Private, Limited, or Public
4. If Limited, specify which users or groups should have access
5. Click **Save**

> **Tip:** Start private. Share when ready. This lets you iterate without exposing unfinished work to your students.

---

## Working with Groups

Groups simplify permission management. Instead of sharing a resource with 30 individual students, you share it with the "ENG 2100 Fall 2026" group.

### Creating a Group (Admin)

1. Go to **Admin Panel > Users**
2. Select **Groups**
3. Click **+ Create Group**
4. Name the group
   - Use something recognizable: course code + term, research team name, department
5. Add members
6. Click **Save**

### What Groups Enable

When you share a resource with a group:
- Every member of that group gains access immediately
- New members added to the group automatically see the shared resources
- Members removed from the group lose access
- You manage one group. Thirty students, one permission change.

---

## Advanced Settings

<details>
<summary>View details</summary>

### SCIM 2.0 Provisioning

For institutions with identity providers (Okta, Azure AD, Google Workspace), Open WebUI supports SCIM 2.0. This automates user lifecycle management: when a student is added to a course roster in your identity provider, their Sandbox account and group memberships update automatically. When they drop the course, access revokes.

Contact the AI Lab team to configure SCIM integration for your department.

### Permission Inheritance

Custom roles inherit from the default `@everyone` baseline. When you create a new group, its members start with standard user permissions. You then layer on additional access through resource sharing.

</details>

---

## Callout

<div class="callout">
  <strong>For instructors:</strong> Establish groups at the start of each semester, organized by course section. Share your models and knowledge bases with those groups before the first day of class. When students log in, your resources are already waiting for them.
</div>

---

## Additional Resources

- [Open WebUI User Management](https://docs.openwebui.com) — official documentation for roles, groups, and SCIM provisioning
- [CUNY IT Policies](https://www.cuny.edu/about/administration/offices/cis/it-policies/) — institutional guidelines for data access and user management

---

[← Return to Tools & Skills](tools-skills.md) | [Teaching Tips →](teaching-tips.md)
