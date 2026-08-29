# Changelog

All notable changes to Monash Hub are documented here.

## Unreleased

### Added

- Signing in with Google. An account is matched by email address, so a Google
  sign-in with an address that already has a password account signs into that
  same account rather than making a second one. Only addresses Google reports as
  verified are accepted, because matching by email is what the flow rests on.
  The button appears only where the server has credentials configured, so a
  deployment without them looks like a deployment without the feature.

### Documentation

- Added a direct production-site link to every language version of the README.
- Reworked the primary README as a Simplified Chinese, user-facing guide for students who need help finding and understanding Monash information.
- Added English, Japanese and Korean README versions, linked from every README.
- Clarified the separation between official Handbook data, official Monash sources and student community content.
- Documented community participation, including finding study partners, activity companions and students with shared interests, as a supporting feature.
- Moved developer-oriented references to the existing documentation set instead of placing local setup instructions in the user-facing README.
