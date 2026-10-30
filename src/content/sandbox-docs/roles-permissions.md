---
title: "Roles & Permissions"
headingId: "roles--permissions"
---

Before sharing a model, decide who should use it and who should be able to edit it. Sharing with a course group is different from making a resource available across the Sandbox, and a model's permissions do not automatically cover its attachments.

## Share with the Intended Group

Approved courses receive a private group and text channel automatically. Confirm enrollment through [My classes](https://tools.ailab.gc.cuny.edu/my-classes), and contact [ailab@gc.cuny.edu](mailto:ailab@gc.cuny.edu) if the course group or its membership needs attention.

1. Open the model, knowledge base, or prompt you want to share.
2. Open **Access**, or the resource's access controls.
3. Keep **Private** and choose **Add Access**.
4. Select the course group and grant **Read** access. Grant **Write** only to collaborators who should edit the resource.
5. Save if the editor presents a save button. Review the saved audience and permissions.

Repeat for the knowledge collections, tools, and skills attached to a shared model. Arrange a check from the intended user's view before class; seeing a resource as its owner does not establish that students can use it.

## Understand Visibility

With **Private** selected and no access grants, a resource stays private to you. **Add Access** admits selected users or groups without making it public. **Public**, when your account permits it, makes the resource available to all signed-in Sandbox users, not just your course. Administrators may also access resources for platform management.

Resource visibility does not replace a separate review before sharing a chat or posting in a course channel. Check the content and audience of those actions too.

## Understand Account Roles

Open WebUI uses **Admin**, **User**, and **Pending** roles. Administrators configure connections, users, groups, installed tools, and defaults. A Pending account cannot use the main platform until activated.

Faculty, staff, and students receive access through assigned permissions and groups. Individual Lab access lets you use shared resources but does not automatically include **Workspace**. Request Workspace access from the Lab if you need to create configurations. Students join through an instructor's invitation; editing a shared resource or creating a private configuration requires the relevant permission.

## Review Access When Membership Changes

A group grant applies to its members, including new members. Removing someone removes that group's grant, but access through another group or a direct grant may remain. Ask the Lab to resolve uncertain access rather than assuming that removing one membership revokes everything.

For course enrollment, follow [Student Onboarding](student-onboarding.md) and **My classes**. A registrar roster change alone is not confirmation of Sandbox enrollment or removal.

## Administrator Reference

<details>
<summary>Open group-management details</summary>

For groups that need manual administration, open **Admin Panel > Users > Groups**, choose **Create Group**, enter a recognizable name, add members, and select **Save**. Do not create a duplicate group in place of the approved-course process.

Administrators set default and group permissions; group grants are additive. Open WebUI also supports SCIM 2.0 provisioning when configured. That platform capability does not establish that a particular Sandbox roster is synchronized. Consult the [Open WebUI access-control reference](https://docs.openwebui.com/features/authentication-access/rbac/) and the Lab before changing provisioning.

</details>

[← Return to Tools & Skills](tools-skills.md) | [Continue to Student Onboarding →](student-onboarding.md)
