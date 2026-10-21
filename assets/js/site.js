(function () {
  "use strict";

  var content = document.querySelector(".post-content");
  if (!content) return;

  var headings = content.querySelectorAll("h2[id], h3[id], h4[id]");

  // Hover anchors on section headings
  headings.forEach(function (h) {
    var a = document.createElement("a");
    a.className = "heading-anchor";
    a.href = "#" + h.id;
    a.setAttribute("aria-label", "Link to this section");
    a.textContent = "#";
    h.prepend(a);
  });

  // Table of contents for posts with `toc: true`
  var toc = document.querySelector("[data-toc]");
  if (!toc) return;
  var root = document.createElement("ol");
  var currentH2 = null;
  headings.forEach(function (h) {
    if (h.tagName === "H4") return;
    var li = document.createElement("li");
    var link = document.createElement("a");
    link.href = "#" + h.id;
    link.textContent = h.textContent.replace(/^#/, "").trim();
    li.appendChild(link);
    if (h.tagName === "H2" || !currentH2) {
      root.appendChild(li);
      if (h.tagName === "H2") currentH2 = li;
    } else {
      var sub = currentH2.querySelector("ol");
      if (!sub) { sub = document.createElement("ol"); currentH2.appendChild(sub); }
      sub.appendChild(li);
    }
  });
  if (root.children.length) toc.appendChild(root);
  else toc.remove();
})();
