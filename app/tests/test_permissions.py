import pytest
from app.utilities import allowed_role_action

# Define user roles
USERS = {
    "editor_only": ["editor"],
    "admin_only": ["admin"],
    "superuser_only": ["superuser"],
    "admin_and_editor": ["admin", "editor"],
    "su_and_editor": ["superuser", "editor"],
    "su_and_admin": ["superuser", "admin"],
    "allroles": ["superuser", "admin", "editor"],
    "norole": []
}

ALL_ROLES = ["superuser", "admin", "editor"]


@pytest.mark.parametrize("actor,actor_roles", USERS.items())
@pytest.mark.parametrize("target,target_roles", USERS.items())
@pytest.mark.parametrize("action", ["add", "edit", "delete"])
def test_allowed_role_action_combinations(actor, actor_roles, target, target_roles, action):
    # --- ADD ---
    if action == "add":
        target_roles = []
        # Try adding each possible role set
        for requested_roles in [
            [],
            ["editor"],
            ["admin"],
            ["superuser"],
            ["admin", "editor"],
            ["superuser", "editor"],
            ["superuser", "admin"],
            ["superuser", "admin", "editor"],
        ]:
            allowed, message = allowed_role_action(
                actor_roles=actor_roles,
                action=action,
                actor=actor,
                target=target,
                target_roles=target_roles,
                requested_roles=requested_roles
            )
            # Superuser can add any role combination
            if "superuser" in actor_roles:
                assert allowed, f"{actor} should be able to add {requested_roles}"
            # Admin can only add users with no roles or just editor
            elif "admin" in actor_roles:
                if set(requested_roles) == {"editor"} or set(requested_roles) == set():
                    assert allowed, f"{actor} should be able to add {requested_roles}"
                else:
                    assert not allowed, f"{actor} should NOT be able to add {requested_roles}"
            # Editors and no-role users cannot add users
            else:
                assert not allowed, f"{actor} should NOT be able to add {requested_roles}"
    
    # --- EDIT ---
    else:
        if action == "edit":
            # Try editing
            for requested_roles in [
                target_roles,
                [],
                ["editor"],
                ["admin"],
                ["superuser"],
                ["admin", "editor"],
                ["superuser", "editor"],
                ["superuser", "admin"],
                ["superuser", "admin", "editor"],
            ]:
                allowed, message = allowed_role_action(
                    actor_roles=actor_roles,
                    action=action,
                    actor=actor,
                    target=target,
                    target_roles=target_roles,
                    requested_roles=requested_roles
                )
                # Superuser can edit anyone in any way
                if "superuser" in actor_roles:
                    assert allowed, f"{actor} should be able to {action} {target} as {requested_roles}"
                # Admin logic
                elif "admin" in actor_roles:
                    # Admin can edit their own admin/editor roles
                    if actor == target and set(target_roles) in [{"admin"}, {"admin", "editor"}] and set(requested_roles) in [{"admin"}, {"admin", "editor"}]:
                        assert allowed, f"{actor} should be able to edit self editor role"
                    # Admin cannot edit other admins or superusers
                    elif "superuser" in target_roles or ("admin" in target_roles and actor != target):
                        assert not allowed, f"{actor} should NOT be able to edit {target} as {requested_roles}"
                    # Admin cannot assign admin/superuser roles to others
                    elif requested_roles and ("superuser" in requested_roles or ("admin" in requested_roles and actor != target)):
                        assert not allowed, f"{actor} should NOT be able to assign admin/superuser to {target}"
                    # Admin can edit editors or no-role users
                    else:
                        assert allowed, f"{actor} should be able to edit {target} as {requested_roles}"
                # Editors and no-role users
                elif "editor" in actor_roles or not actor_roles:
                    # Can only edit themselves
                    if actor != target:
                        assert not allowed, f"{actor} should NOT be able to edit {target}"
                    # Cannot remove their own editor role
                    elif "editor" in target_roles and (not requested_roles or "editor" not in requested_roles):
                        assert not allowed, f"{actor} should NOT be able to remove own editor role"
                    # Cannot change roles at all (must match exactly)
                    elif set(target_roles) != set(requested_roles or target_roles):
                        assert not allowed, f"{actor} should NOT be able to change roles"
                    # Allowed to edit self if roles unchanged or only keeping editor
                    else:
                        assert allowed, f"{actor} should be able to edit self as {requested_roles}"

        # --- DELETE ---
        elif action == "delete":
            # Only test delete with the actual target_roles (no requested_roles)
            allowed, message = allowed_role_action(
                actor_roles=actor_roles,
                action=action,
                actor=actor,
                target=target,
                target_roles=target_roles,
                requested_roles=None
            )
            # Superuser can delete anyone
            if "superuser" in actor_roles:
                assert allowed, f"{actor} should be able to delete {target} as {target_roles}"
            # Admin can delete editors or no-role users, and can delete self if only admin or admin+editor
            elif "admin" in actor_roles:
                if actor == target and set(target_roles) in [{"admin"}, {"admin", "editor"}]:
                    assert allowed, f"{actor} should be able to delete self editor role"
                elif "superuser" in target_roles or ("admin" in target_roles and actor != target):
                    assert not allowed, f"{actor} should NOT be able to delete {target} as {target_roles}"
                else:
                    assert allowed, f"{actor} should be able to delete {target} as {target_roles}"
            # Editors/no-role cannot delete anyone, including themselves
            elif "editor" in actor_roles or not actor_roles:
                assert not allowed, f"{actor} should NOT be able to delete {target}"
            else:
                assert not allowed, f"{actor} should NOT be able to delete {target}"
