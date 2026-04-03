# Reference: GTM Audit Checkpoints

This document defines the criteria for auditing Google Tag Manager (GTM) configurations using GTM Copilot. When performing an audit (Audit Workflow), AI agents must always check the content of this file and conduct analysis based on the following items.

## 1. PII Leakage (Personally Identifiable Information)
Ensure that user's PII is not collected or transmitted unintentionally.
- **URL Parameters**: Check if parameters like `email=`, `phone=`, `address=`, or `name=` are included in custom dimensions or URLs.
- **Form Data**: Check if variables that directly retrieve input form values are transmitting passwords or email addresses as is.

Note: Consider that hashing may be performed on the tag side, so use your judgment accordingly.

## 2. Naming Conventions
These rules are for improving readability and searchability in the management console. We do not define specific naming conventions, but check from the following perspectives:

- Does the name allow you to understand what behavior it performs?
- Is there consistency in naming conventions within the same GTM container?

## 3. Duplication
Check for any components (tags, triggers, or variables) that are duplicated with the same settings.

## 4. Unused Components
Check for any tags, triggers, or variables that are not being used.
Triggers or variables that are not referenced by anything else are candidates for deletion. Tags with no triggers attached are also candidates for deletion.

## 5. Don't Repeat Yourself (DRY)
Check if similar configuration details are repeatedly written in tags, triggers, or variables. Similar trigger conditions can be candidates for replacement with a new variable. For items that need to be specified in multiple tags, such as GA4 Measurement IDs, it is recommended to use variables instead of hard-coding values directly in the tags. The same applies to common event parameters for GA4.

## 6. Condition Integrity
Examine whether the conditions specified in triggers are necessary and sufficient for their purpose. For example, DOM class names may change dynamically due to user operations. If a condition is set to "exactly matches" a DOM class name or text, it may break unexpectedly. Exact matches for Page URL variables may also break due to the presence or order of query parameters.

## 7. GA4 Recommended Settings
GA4 has various recommended settings; check if the configurations follow them. Key check items include:

* Do the event names and parameters of recommended events follow their definitions?
* Are multi-byte characters excluded from event names?

## 8. Container Performance & Size
There are size limits for tags, triggers, and variables in GTM. There is no specific count limit, but rather a limit based on the number of bytes in strings, and it's not possible to determine if the limit is being approached.

However, generally, a large number of Custom HTML tags (even a few if they have a large amount of code) or Custom JavaScript variables with large amounts of code are factors that increase container size.

If such a tendency is seen as a result of the audit, please point it out.

## 9. Documentation
Check if the purpose or history of creation for complex triggers, tags, or variables is described in the "Notes" (description) field.

## 10. Consent Management
In environments where Google Tag Consent Mode or Cookie Consent tools are used, verify that all tags are correctly fired or restricted based on the consent status. It is a critical issue if a tag fires regardless of consent when a Cookie Consent tool is implemented.

## 11. Debug / Preview Artifacts
Keep the production environment clean. Check if test-only exception settings (e.g., "fire only for my IP address") or console log code for debugging remain in the published version.

---

## 101. Meta Pixel
### 101-1. Multiple Pixel Management
Check items for when multiple Meta Pixels are installed on a single site.

* Use of trackSingle:
** When you want to send a specific event only to a specific Pixel ID, check if `fbq('trackSingle', 'PIXEL_ID', 'EventName', { ... })` is used instead of `fbq('track', ...)`.
* Duplicate Initialization (init):
** If there are multiple Pixels, check if `fbq('init', 'PIXEL_ID')` is executed for each Pixel ID without omission and without duplication.
* PageView Control:
** Pasting the standard base code multiple times may result in duplicate PageView measurements for all Pixels. Check if it is configured to send PageView only to specific Pixels if necessary.

### 101-2. Advanced Matching Safety
Check items for "Advanced Matching" to improve matching accuracy.

* Hashing: When sending email addresses or phone numbers via `em` or `ph` parameters, check if they are SHA256 hashed before transmission (this is automatic when using official GTM Meta templates, but manual hashing is required for custom HTML).
* Plain Text Inclusion: Check that PII is not sent to Meta as plain text without hashing. This is directly linked to the risk of account suspension.

### 101-3. Standard Event Compliance
Check items to ensure Meta's optimization algorithms function correctly. Note that naming conventions differ from GA4 recommended events.

* Use of Standard Events: Check if standard event names like `Purchase`, `AddToCart`, and `Contact` are used correctly. Using only custom names (e.g., `Clicked_Button`) makes optimization (conversion goal setting) difficult.
* Spelling and Case Sensitivity: Check if it is `Purchase` (starting with an uppercase letter) rather than `purchase`. Meta distinguishes between the two.

### 101-4. Currency & Value Formatting
Essential check for calculating ROAS (Return on Ad Spend).

* Numeric Format: Ensure that the `value` parameter does not include symbols like `¥` or `,` (it must be a pure number).
* Currency Code: Check if `currency` is sent correctly in ISO standard formats like `JPY` or `USD`.
* Pair Sending: If sending `value`, ensure `currency` is always sent as a pair.