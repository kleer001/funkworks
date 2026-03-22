# Plugin Brief: Fluid Domain Auto-Visibility

## Problem Statement
When a Blender fluid simulation starts after frame 1, the domain object is visible as an empty box during the frames before the simulation begins, requiring users to manually add visibility keyframes every time.

## Proposed Solution
A single operator the user runs on a selected fluid domain object. It reads the simulation's start frame from the fluid modifier settings and inserts two sets of visibility keyframes: hidden one frame before the sim starts, visible on the sim start frame. One click, no manual keyframing.

## Host Application
- Application: Blender
- Minimum version: Blender 4.0+
- API surfaces required:
  - `bpy.types.Operator` — the operator class
  - `bpy.types.Panel` — sidebar panel in the Physics tab
  - `bpy.props` — no user inputs needed beyond the selection
  - `obj.modifiers` — to find the FLUID modifier
  - `modifier.domain_settings.cache_frame_start` — to read the sim start frame
  - `obj.keyframe_insert(data_path="hide_viewport", frame=N)` — visibility keyframes
  - `obj.keyframe_insert(data_path="hide_render", frame=N)` — render visibility keyframes
  - `bpy.context.scene.frame_start` — fallback for "hide from" frame

## User Interface
- Appears in: Physics Properties panel → Fluid section, as a button labeled **"Auto-Keyframe Visibility"**; also accessible via the operator search (F3) as "Fluid Domain: Auto-Keyframe Visibility"
- User inputs: none — operator reads everything from the modifier
- Feedback: an `operator.report(INFO, ...)` message in the status bar confirming the frames at which keyframes were inserted, e.g. "Visibility keyframes set: hidden at frame 23, visible at frame 24"

## Inputs and Outputs
- Input: the active object, which must have a Fluid modifier set to Domain type
- Output: two pairs of keyframes on `hide_viewport` and `hide_render`:
  - Frame `cache_frame_start - 1`: both set to `True` (hidden)
  - Frame `cache_frame_start`: both set to `False` (visible)
- Side effects: creates one undo step; modifies the object's animation data

## Edge Cases
- **No selection:** operator is greyed out (poll fails) — button is disabled, no error
- **Selected object is not a fluid domain:** poll fails, button is greyed out with tooltip "Active object must be a fluid domain"
- **Sim starts at frame 1:** operator runs but warns via `report(WARNING, ...)` — "Sim starts at frame 1; no pre-sim frames to hide. Keyframes inserted anyway." (still inserts at frame 0 and frame 1 for consistency)
- **Existing keyframes on hide_viewport / hide_render:** new keyframes overwrite existing ones at those frames; keyframes at other frames are untouched
- **Multiple fluid modifiers on one object:** uses the first modifier of type FLUID with domain_settings

## Known Limitations
- Does not handle the case where the sim *ends* before the scene ends (no post-sim hide keyframe)
- Does not modify keyframes on objects other than the active one — users with multiple domains must run it once per domain
- Does not touch the `hide_select` or collection visibility properties
- Does not interact with Blender's cache bake state — works regardless of whether the sim is baked

## Acceptance Criteria
1. Plugin installs without error on Blender 4.0+
2. "Auto-Keyframe Visibility" button appears in the Physics Properties panel when a fluid domain is selected
3. Button is greyed out (poll returns False) when active object has no fluid domain modifier
4. Running the operator on a domain with `cache_frame_start = 24` inserts `hide_viewport = True` and `hide_render = True` at frame 23, and `hide_viewport = False` and `hide_render = False` at frame 24
5. Status bar shows a confirmation message with the correct frame numbers after execution
6. Ctrl+Z undoes all inserted keyframes in a single undo step
7. Running the operator twice on the same object does not create duplicate keyframes
8. Running on a domain with `cache_frame_start = 1` completes without error and shows a warning in the status bar
