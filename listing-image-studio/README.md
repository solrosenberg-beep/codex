# Listing Image Studio

Internal tool to audit and rebuild Amazon listing images, driven by the rules and brand kits in [solrosenberg-beep/codex](https://github.com/solrosenberg-beep/codex).

- `prototype/index.html`: a clickable, chat-style design of one complete product run. Type an ASIN plus a note ("B0HJ3R1ZQD rebuild this, it has auto incline so the main image needs to be amazing"). The tool pulls the listing, flags problems, asks for one-tap fact checks, then shows the image set in listing order (original next to new) with Approve, Request Changes and Regenerate. Say "save to drive" to finish. The left sidebar is History. Open it in a browser while serving the folder, so the logos load. For example:

  ```bash
  cd listing-image-studio/prototype && python3 -m http.server 8000
  ```

  The "Prototype controls" box shows the error states: a failed slot, a failed Drive save and a listing that won't load.
- `DEVELOPER-HANDOFF.md`: architecture, API, data model, rules sync, Drive and error handling for the developer who connects the real services.

Images in the prototype are drawn stand-ins. The product, SKU and history rows are sample data.
