# eVitals Documentation RAG Backend

QUESTIONS ANSWERED FOR TESTING 
=== FACTUAL LOOKUPS ===
1. What is the exact character length required for a Meter Serial Number?
2. What are the four CPT codes associated with RPM?
3. What are the three CPT codes associated with CCM?
4. How many chronic conditions must a patient have to be eligible for CPT 99490?
5. What is the default Systolic, Diastolic, and Pulse target range for Blood Pressure?
6. What is the default Weight Target Range in pounds?
7. What BMI value marks the threshold for "Obese"?
8. How many measurement days are required for CPT 99454 eligibility?
9. What is the default Blood Glucose target range for fasting/before-meal windows?
10. What are the five Blood Pressure reading windows?

=== ROLE & PERMISSION COMPARISONS ===
11. Can a Provider delete a patient record?
12. Can a Practice Admin create a new practice?
13. What's the difference between what a Practice Caregiver and a System Caregiver can do?
14. Which roles can access the Inventory Management module?
15. Can an Admin view Email Logs?
16. Which roles can add a new Practice Admin?
17. Does a Provider have edit rights on the Practice Caregivers roster?
18. Can a Practice Caregiver access the Calendar module?
19. Which roles can create a custom role under Permission/RBAC?

=== NAVIGATION ("WHERE DO I GO TO...") ===
20. Where do I go to add a patient's device serial number?
21. How do I reach the screen to configure Blood Glucose reading windows?
22. Where can I grant a System Caregiver calendar access?
23. How do I get to the per-practice RPM billing report?
24. Where do I configure which CPT codes belong to the RPM program?
25. Where do I go to bulk-import patients via CSV?

=== FIELD / UI DEFINITIONS ===
26. What does the "T / A / P / L" badge mean on the Billing Management screen?
27. What is the difference between "Measurement Days" and "Service Time"?
28. What does "Buying Device = No" mean on the Practice tab?
29. What does the Complexity column mean on the CCM billing report, and can it be edited?
30. What happens when a device's Model # or Serial # shows a dash on the RPM report?
31. What is a Gateway Serial Number and when is it used?

=== WORKFLOW / CROSS-MODULE REASONING ===
32. Walk me through what happens from when a device is assigned to a patient to when it becomes eligible for billing.
33. What has to be true before a System Caregiver can be assigned to book an appointment on the calendar?
34. If I toggle Chat Access to Blocked for a caregiver-patient pair, what happens immediately?
35. What's required on the patient enrollment wizard before you can click Next past Step 1?
36. How does an abnormal reading turn into a documented follow-up?

=== EDGE CASES / VALIDATION RULES ===
37. What happens if I try to import a CSV row with an MRN that already exists?
38. Can I delete an Inventory product that still has assigned devices?
39. What happens if I try to enroll a patient without selecting a Practice Caregiver?
40. Can Blood Pressure reading windows overlap?
41. What happens if I try to reduce Inventory Qty below the number of already-mapped serial numbers?

=== GAP / DISCREPANCY TRAPS (should say "not specified" or flag the conflict) ===
42. Can a Super Admin use Patient Management?
43. What is the minimum password length required?
44. What does "MRN" refer to on the patient enrollment form?
45. What are all the possible values of "Billing Path" on the CCM report?
46. Does an Admin have access to the Permission (RBAC) tab?
47. What is the maximum allowed Session Time value?

=== OUT-OF-SCOPE / ADVERSARIAL (should decline or say "not covered", not hallucinate) ===
48. What does the red color on a BP reading actually mean clinically?
49. How does the eVitals patient mobile app work?
50. What insurance carriers does eVitals support?
