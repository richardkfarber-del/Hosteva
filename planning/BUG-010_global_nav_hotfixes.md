# BUG-010: Global Navigation Hotfixes
**Type:** Bug
**Description:** 
The application navigation requires immediate remediation based on Recon team findings. 
- The Integrations link is currently missing from the navigation menu.
- The Hosteva Logo is broken/not displaying correctly.
- The user state is static (hardcoded as "John Smith").

## Acceptance Criteria
- Given a user is logged into the application, when they view the navigation menu, then they will see the Integrations link.
- Given a user views any page with the global navigation, when the navigation loads, then the Hosteva Logo will display correctly.
- Given a specific user logs in, when the application loads the user state, then the dynamic user name will be displayed instead of a static "John Smith".
