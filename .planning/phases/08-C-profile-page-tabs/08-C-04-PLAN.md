---
phase: 08-C-profile-page-tabs
plan: 04
type: execute
wave: 1
depends_on: ["08-C-03"]
files_modified:
  - static/js/profile_tabs.js
autonomous: true
gap_closure: true

must_haves:
  truths:
    - "Arrow Right moves focus to next tab with wrap-around"
    - "Arrow Left moves focus to previous tab with wrap-around"
    - "Active tab has tabindex=0, inactive tabs have tabindex=-1"
    - "Focus follows selection (automatic activation)"
  artifacts:
    - path: "static/js/profile_tabs.js"
      provides: "Keyboard navigation handler"
      contains: "keydown"
  key_links:
    - from: "static/js/profile_tabs.js"
      to: "tablist element"
      via: "keydown event listener"
      pattern: "addEventListener.*keydown"
---

<objective>
Add arrow key navigation to TabController to close UAT gap.

Purpose: The TabController only implements click handlers. ARIA tab pattern requires arrow key navigation with wrap-around at ends.

Output: TabController with full keyboard navigation per W3C ARIA Authoring Practices.
</objective>

<execution_context>
@C:\Users\Administrator\.claude/get-shit-done/workflows/execute-plan.md
@C:\Users\Administrator\.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@static/js/profile_tabs.js
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add keyboard navigation to TabController</name>
  <files>static/js/profile_tabs.js</files>
  <action>
    Modify the existing TabController class in `static/js/profile_tabs.js`:

    1. Add keydown event listener in constructor (after click handlers):
       ```javascript
       this.tablist.addEventListener('keydown', this.onKeydown.bind(this));
       ```

    2. Add onKeydown method to handle ArrowLeft/ArrowRight:
       ```javascript
       onKeydown(event) {
           const currentIndex = this.tabs.indexOf(document.activeElement);
           if (currentIndex === -1) return;

           let targetIndex = currentIndex;

           switch (event.key) {
               case 'ArrowRight':
                   targetIndex = (currentIndex + 1) % this.tabs.length;
                   break;
               case 'ArrowLeft':
                   targetIndex = (currentIndex - 1 + this.tabs.length) % this.tabs.length;
                   break;
               case 'Home':
                   targetIndex = 0;
                   break;
               case 'End':
                   targetIndex = this.tabs.length - 1;
                   break;
               default:
                   return; // Don't prevent default for other keys
           }

           event.preventDefault();
           this.activateTab(targetIndex);
           this.tabs[targetIndex].focus();
       }
       ```

    3. Update activateTab method to manage tabindex attributes:
       ```javascript
       activateTab(index) {
           this.tabs.forEach((tab, i) => {
               const isActive = i === index;
               tab.setAttribute('aria-selected', isActive);
               tab.setAttribute('tabindex', isActive ? '0' : '-1');
               tab.classList.toggle('tab-button-active', isActive);
           });

           this.panels.forEach((panel, i) => {
               if (panel) {
                   panel.hidden = i !== index;
               }
           });
       }
       ```

    The wrap-around formula `(currentIndex - 1 + this.tabs.length) % this.tabs.length` handles the left edge case (going from index 0 to last tab).
  </action>
  <verify>
    Open browser dev tools console and test:
    ```javascript
    // Click on first tab to focus it
    document.querySelector('[role="tab"]').focus();

    // Simulate arrow right - should move to second tab
    document.querySelector('[role="tablist"]').dispatchEvent(
      new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true })
    );
    console.log('Active tab:', document.activeElement.textContent.trim());

    // Simulate arrow left - should go back to first tab
    document.querySelector('[role="tablist"]').dispatchEvent(
      new KeyboardEvent('keydown', { key: 'ArrowLeft', bubbles: true })
    );
    console.log('Active tab:', document.activeElement.textContent.trim());

    // Test wrap-around: focus last tab, then arrow right
    const tabs = document.querySelectorAll('[role="tab"]');
    tabs[tabs.length - 1].focus();
    document.querySelector('[role="tablist"]').dispatchEvent(
      new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true })
    );
    console.log('After wrap, active tab:', document.activeElement.textContent.trim());
    // Should be first tab
    ```

    Manual test:
    1. Click on any tab to focus it
    2. Press Right Arrow - focus moves to next tab, panel switches
    3. Press Left Arrow - focus moves to previous tab, panel switches
    4. On last tab, press Right Arrow - wraps to first tab
    5. On first tab, press Left Arrow - wraps to last tab
  </verify>
  <done>
    Arrow key navigation works with wrap-around at both ends, tabindex managed correctly.
  </done>
</task>

</tasks>

<verification>
1. Focus a tab (click or tab into tablist)
2. Press Right Arrow - moves to next tab with focus
3. Press Left Arrow - moves to previous tab with focus
4. At last tab, Right Arrow wraps to first tab
5. At first tab, Left Arrow wraps to last tab
6. Home key goes to first tab
7. End key goes to last tab
8. Active tab has tabindex="0", inactive tabs have tabindex="-1"
</verification>

<success_criteria>
- [ ] keydown event listener added to tablist
- [ ] ArrowRight navigates forward with wrap-around
- [ ] ArrowLeft navigates backward with wrap-around
- [ ] Home/End keys navigate to first/last tab
- [ ] tabindex attributes updated (active=0, others=-1)
- [ ] focus() called on newly active tab
</success_criteria>

<output>
After completion, create `.planning/phases/08-C-profile-page-tabs/08-C-04-SUMMARY.md`
</output>
