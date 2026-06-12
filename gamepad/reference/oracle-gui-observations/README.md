# Oracle GUI observations — user's live Steam session captures

User-captured evidence from their own Steam client (Desktop Controller Layout configurator),
supporting findings in `../../findings/steam_lane_behavior.md`.

## `20260612-slot-order-repro.png`

Screenshot of the configurator during the order-dependent edge-activator-loss repro
(finding §Order-dependent edge-activator loss, commit `48e534e`). What it documents:

- **The GUI slot model:** multiple activators on one button render as numbered **"Command 1..N"**
  rows under "Executes N Commands". Slot order is explicit, user-visible, and ordinal — real
  configs carry these orderings, created implicitly by binding order. This is the order that the
  bug-class is sensitive to.
- **Button B = the broken arrangement, as bound:** Command 1 *Start Press* → A Key, Command 2
  *Release Press* → B Key, Command 3 *Long Press* → C Key — the exact stack that produced
  `B C C C…` with Start never firing and Release firing early.
- **Button A = Release Press → F2, alone — and it fires.** Same activator, same key our generated
  marker layout used; firing in isolation, this fully acquits the key choice and the
  `Release_Press` token.
- **GUI labeling quirk:** default Regular Press commands show NO activation label in the list
  view (see X's Command 1 and Y's Command 2) — only non-default activations are tagged. Read
  future screenshots accordingly.
- Also visible: X = Regular(X Button) + Long Press(V Key); Y = Button Chord(N Key) + Regular(0) —
  the user's own side experiments, not part of the repro.
