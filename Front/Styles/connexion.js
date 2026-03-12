const items = [
  { btn: "btn-eleve", panel: "panel-eleve", focus: "email-eleve" },
  { btn: "btn-prof", panel: "panel-prof", focus: "email-prof" },
  { btn: "btn-admin", panel: "panel-admin", focus: "email-admin" }
];

function closeAll() {
  for (const it of items) {
    const b = document.getElementById(it.btn);
    const p = document.getElementById(it.panel);
    b.classList.remove("is-open");
    b.setAttribute("aria-expanded", "false");
    p.hidden = true;
  }
}

function toggleOne(btnId) {
  const it = items.find(x => x.btn === btnId);
  if (!it) return;

  const b = document.getElementById(it.btn);
  const p = document.getElementById(it.panel);

  const isOpen = !p.hidden;

  closeAll();
  if (!isOpen) {
    b.classList.add("is-open");
    b.setAttribute("aria-expanded", "true");
    p.hidden = false;

    const focusEl = document.getElementById(it.focus);
    if (focusEl) focusEl.focus();
  }
}

for (const it of items) {
  document.getElementById(it.btn).addEventListener("click", () => toggleOne(it.btn));
}

toggleOne("btn-eleve");

document.querySelectorAll(".lang").forEach(container => {
  const targetId = container.dataset.target;
  const hidden = document.getElementById(targetId);
  if (!hidden) return;
  const btns = container.querySelectorAll(".lang__btn");

  btns.forEach(btn => {
    btn.addEventListener("click", () => {
      const lang = btn.dataset.lang;
      window.location.href = "/set_lang/" + lang;
    });
  });
});
